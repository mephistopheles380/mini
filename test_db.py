import psycopg2
from database import DB_CONFIG

def test_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Successfully connected to the database!")
        conn.close()
    except Exception as e:
        print(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    test_connection() 