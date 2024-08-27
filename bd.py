import psycopg2
import pandas as pd

# Load the extracted articles from the CSV file
df = pd.read_csv("extracted_articles.csv")

# Create a PostgreSQL database connection
conn = psycopg2.connect(
    dbname="article_db",
    user="postgres",
    password="mayssa",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Create a table to store the articles
cur.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id SERIAL PRIMARY KEY,
        url TEXT,
        title TEXT,
        date TEXT,
        site TEXT
    );
""")
conn.commit()

# Insert the extracted articles into the table
for index, row in df.iterrows():
    cur.execute("""
        INSERT INTO articles (url, title, date, site)
        VALUES (%s, %s, %s, %s);
    """, (row['url'], row['title'], row['date'], row['site']))
conn.commit()

print("Articles inserted into the database.")

# Close the database connection
conn.close()