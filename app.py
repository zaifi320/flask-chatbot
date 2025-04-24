from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import sqlite3

app = Flask(__name__)

# Set your Gemini API key
GEMINI_API_KEY = "AIzaSyBeHtk-59VXsvsc-b3tNqas-2VbmeLaXo4"

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Database connection
def get_db_connection():
    conn = sqlite3.connect('properties.db')
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def chatbot(prompt):
    """
    Function to interact with the Gemini API and database.
    """
    try:
        prompt_lower = prompt.lower()

        if "who are you" in prompt_lower:
            return "<p><strong>I am a chatbot assistant for the Proptech Platform.</strong> How can I assist you today?</p>"

        if "what is proptech" in prompt_lower:
            return (
                "<p><strong>Proptech</strong> (Property Technology) refers to the use of technology to innovate "
                "and improve the real estate industry. Our platform helps users find, buy, and manage properties efficiently.</p>"
            )

        if "show me property" in prompt_lower or "recommend property" in prompt_lower:
            # Try to get location from the prompt
            if "in" in prompt_lower:
                location = prompt_lower.split("in", 1)[1].strip()
            else:
                location = None

            conn = get_db_connection()
            cursor = conn.cursor()

            if location:
                cursor.execute("SELECT * FROM properties WHERE location LIKE ?", (f"%{location}%",))
            else:
                cursor.execute("SELECT * FROM properties")

            properties = cursor.fetchall()
            conn.close()

            if not properties:
                return f"<p><strong>No properties found</strong> in that location.</p>"

            response = f"<p><strong>Here are some properties in {location if location else 'your area'}:</strong></p>"
            for prop in properties:
                response += (
    f"<div style='margin-bottom: 10px;'>"
    f"<strong>{prop['type'].title()} in {prop['location']}</strong><br>"
    f"💰 <strong>Price:</strong> {prop['price']}<br>"
    f"🛏️ <strong>Bedrooms:</strong> {prop['bedrooms']}<br>"
    f"🛁 <strong>Bathrooms:</strong> {prop['bathrooms']}<br>"
    f"📐 <strong>Area:</strong> {prop['area_sqft']} sqft<br>"
    f"📝 <strong>Description:</strong> {prop['description']}</div>"
)
            response += "<p><em>Note: Availability and pricing may vary.</em></p>"
            return response

        # If it's a general query — pass to Gemini AI
        system_prompt = (
            "You are a helpful chatbot assistant for a Proptech platform. "
            "only give respond if query is related to realstate, else other than property the ask them sorry only realstate related queries."
            "give respond to only property related queries inside pakistan only."
            "Your job is to guide users in finding and understanding property listings. "
            "Respond using clean HTML formatting. Bold key labels using <strong> and separate points with <p>."
        )

        messages = [
            {"role": "user", "parts": [{"text": system_prompt}]},
            {"role": "user", "parts": [{"text": prompt}]}
        ]

        response = model.generate_content(messages)
        return response.text

    except Exception as e:
        return f"<p><strong>An error occurred:</strong> {e}</p>"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("message")
        if not user_input:
            return jsonify({"error": "No message provided"}), 400
        response = chatbot(user_input)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
