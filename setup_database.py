import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
from datetime import datetime, timedelta

# Initial database connection parameters (without specific database)
INITIAL_DB_CONFIG = {
    'user': 'postgres',
    'password': '1234',  # Change this to your actual password
    'host': 'localhost',
    'port': '5432'
}

# Final database configuration (with specific database)
DB_CONFIG = {
    'dbname': 'library_db',
    **INITIAL_DB_CONFIG
}

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(**INITIAL_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'library_db'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute('CREATE DATABASE library_db')
            print("Database 'library_db' created successfully")
        else:
            print("Database 'library_db' already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating database: {e}")
        raise

def create_tables():
    """Create all necessary tables"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'user',
                membership VARCHAR(50) DEFAULT 'free',
                joined_date DATE DEFAULT CURRENT_DATE,
                next_billing_date DATE,
                college VARCHAR(255),
                department VARCHAR(255),
                year VARCHAR(10),
                semester VARCHAR(10)
            )
        ''')
        print("Users table created successfully")
        
        # Create admins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'admin'
            )
        ''')
        print("Admins table created successfully")
        
        # Create books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                genre VARCHAR(100) NOT NULL,
                description TEXT,
                cover_image VARCHAR(255),
                book_file VARCHAR(255),
                added_date DATE DEFAULT CURRENT_DATE,
                reads INTEGER DEFAULT 0,
                rating DECIMAL(3,1) DEFAULT 0
            )
        ''')
        print("Books table created successfully")
        
        # Create subscription_plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                features JSONB NOT NULL
            )
        ''')
        print("Subscription plans table created successfully")
        
        # Create activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id SERIAL PRIMARY KEY,
                time VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("Activities table created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

def insert_initial_data():
    """Insert initial data into the tables"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Insert default admin
        cursor.execute('''
            INSERT INTO admins (email, password, name, role)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        ''', ('admin@library.com', 'adminpass123', 'Admin User', 'admin'))
        print("Default admin user created")
        
        # Insert default subscription plans
        subscription_plans = {
            'free': {
                'name': 'Free Resources',
                'price': 0,
                'features': [
                    'Access to textbooks',
                    'Access to guiding books',
                    'Access to dictionaries',
                    'Access to magazines',
                    'Basic download limit'
                ]
            },
            'monthly': {
                'name': 'Premium Monthly',
                'price': 49,
                'features': [
                    'All Free Resources',
                    'Module-wise notes',
                    'Download study materials',
                    'Access to novels',
                    'Complete syllabus access',
                    'Unlimited downloads'
                ]
            },
            'yearly': {
                'name': 'Premium Yearly',
                'price': 499,
                'features': [
                    'All Monthly Features',
                    'Priority access to new resources',
                    '2 months free',
                    'Offline reading',
                    'Premium support'
                ]
            }
        }
        
        for plan_id, plan in subscription_plans.items():
            cursor.execute('''
                INSERT INTO subscription_plans (name, price, features)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO NOTHING
            ''', (plan['name'], plan['price'], json.dumps(plan['features'])))
        print("Default subscription plans created")
        
        # Insert sample books
        sample_books = [
            {
                'title': 'Python Programming',
                'author': 'John Smith',
                'genre': 'Programming',
                'description': 'A comprehensive guide to Python programming language',
                'cover_image': 'covers/python_programming.jpg',
                'book_file': 'books/python_programming.pdf',
                'reads': 150,
                'rating': 4.5
            },
            {
                'title': 'Data Structures and Algorithms',
                'author': 'Sarah Johnson',
                'genre': 'Computer Science',
                'description': 'Essential concepts of DSA with practical examples',
                'cover_image': 'covers/dsa.jpg',
                'book_file': 'books/dsa.pdf',
                'reads': 120,
                'rating': 4.8
            },
            {
                'title': 'Web Development Basics',
                'author': 'Michael Brown',
                'genre': 'Web Development',
                'description': 'Introduction to HTML, CSS, and JavaScript',
                'cover_image': 'covers/web_dev.jpg',
                'book_file': 'books/web_dev.pdf',
                'reads': 200,
                'rating': 4.3
            }
        ]
        
        for book in sample_books:
            cursor.execute('''
                INSERT INTO books 
                (title, author, genre, description, cover_image, book_file, reads, rating)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (title) DO NOTHING
            ''', (
                book['title'], book['author'], book['genre'], book['description'],
                book['cover_image'], book['book_file'], book['reads'], book['rating']
            ))
        print("Sample books created")
        
        # Insert sample user
        cursor.execute('''
            INSERT INTO users 
            (email, password, name, role, membership, joined_date, next_billing_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        ''', (
            'user@example.com',
            'userpass123',
            'John Doe',
            'user',
            'free',
            datetime.now().date(),
            (datetime.now() + timedelta(days=30)).date()
        ))
        print("Sample user created")
        
        # Insert initial activities
        activities = [
            ('Just now', 'System initialized'),
            ('Just now', 'Default admin user created'),
            ('Just now', 'Sample books added to library')
        ]
        
        for activity in activities:
            cursor.execute('''
                INSERT INTO activities (time, description)
                VALUES (%s, %s)
            ''', activity)
        print("Initial activities logged")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error inserting initial data: {e}")
        raise

def setup_database():
    """Main function to set up the entire database"""
    try:
        print("Starting database setup...")
        
        # Create database
        create_database()
        
        # Create tables
        create_tables()
        
        # Insert initial data
        insert_initial_data()
        
        print("\nDatabase setup completed successfully!")
        print("\nYou can now run the application using:")
        print("python app.py")
        print("\nDefault credentials:")
        print("Admin - Email: admin@library.com, Password: adminpass123")
        print("User  - Email: user@example.com, Password: userpass123")
        
    except Exception as e:
        print(f"\nError during database setup: {e}")
        print("Please check your PostgreSQL installation and credentials.")
        return False
    
    return True

if __name__ == "__main__":
    setup_database() 