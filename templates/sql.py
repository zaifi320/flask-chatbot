import sqlite3

# Connect to the SQLite database (creates if not exists)
conn = sqlite3.connect("properties.db")
cursor = conn.cursor()

# SQL query to insert data
sql_query = """
INSERT INTO properties (location, type, price, bedrooms, bathrooms, area_sqft, description)
VALUES 
('New York', 'Apartment', 500000, 2, 2, 1200, 'Luxury apartment in downtown New York.'),
('Los Angeles', 'Villa', 1200000, 4, 3, 2500, 'Spacious villa with a pool in LA.'),
('Chicago', 'Office', 300000, 0, 1, 800, 'Modern office space in the heart of Chicago.');
"""

# Execute the query
cursor.execute(sql_query)

# Commit changes and close connection
conn.commit()
conn.close()

print("Data inserted successfully!")
