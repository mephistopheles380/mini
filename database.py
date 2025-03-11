import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta, date
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'library_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '1234'),  # Make sure this matches your PostgreSQL password
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """Create a database connection"""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn

def init_db():
    """Initialize the database by creating tables if they don't exist"""
    try:
        conn = get_db_connection()
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
        
        # Create subscription_plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                features JSONB NOT NULL
            )
        ''')
        
        # Create activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id SERIAL PRIMARY KEY,
                time VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.close()
        conn.close()
        print("Database tables created successfully")
        
        # Initialize default data
        init_default_data()
        
    except Exception as e:
        print(f"Error initializing database: {e}")

def init_default_data():
    """Initialize the database with default data"""
    try:
        # Add default subscription plans
        subscription_plans = {
            'free': {
                'name': 'Free Resources',
                'price': 0,
                'features': json.dumps([
                    'Access to textbooks',
                    'Access to guiding books',
                    'Access to dictionaries',
                    'Access to magazines',
                    'Basic download limit'
                ])
            },
            'monthly': {
                'name': 'Premium Monthly',
                'price': 49,
                'features': json.dumps([
                    'All Free Resources',
                    'Module-wise notes',
                    'Download study materials',
                    'Access to novels',
                    'Complete syllabus access',
                    'Unlimited downloads'
                ])
            },
            'yearly': {
                'name': 'Premium Yearly',
                'price': 499,
                'features': json.dumps([
                    'All Monthly Features',
                    'Priority access to new resources',
                    '2 months free',
                    'Offline reading',
                    'Premium support'
                ])
            }
        }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if plans exist
        cursor.execute("SELECT COUNT(*) FROM subscription_plans")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Add subscription plans
            for plan_id, plan in subscription_plans.items():
                cursor.execute(
                    "INSERT INTO subscription_plans (name, price, features) VALUES (%s, %s, %s)",
                    (plan['name'], plan['price'], plan['features'])
                )
            
            # Add admin user
            cursor.execute(
                "INSERT INTO admins (email, password, name, role) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                ('admin@library.com', 'adminpass123', 'Admin User', 'admin')
            )
            
            # Add default books
            default_books = [
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
            
            for book in default_books:
                cursor.execute(
                    """
                    INSERT INTO books 
                    (title, author, genre, description, cover_image, book_file, reads, rating) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (book['title'], book['author'], book['genre'], book['description'], 
                     book['cover_image'], book['book_file'], book['reads'], book['rating'])
                )
            
            # Add some recent activities
            activities = [
                {
                    'time': '2 mins ago',
                    'description': 'Added new book: Python Programming'
                },
                {
                    'time': '10 mins ago',
                    'description': 'New user registered'
                }
            ]
            
            for activity in activities:
                cursor.execute(
                    "INSERT INTO activities (time, description) VALUES (%s, %s)",
                    (activity['time'], activity['description'])
                )
        
        cursor.close()
        conn.close()
        print("Default data initialized successfully")
        
    except Exception as e:
        print(f"Error initializing default data: {e}")

# ---- User functions ----
def get_user_by_email(email):
    """Get user by email"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, email, password, name, role, membership, 
                   joined_date, next_billing_date, college, 
                   department, year, semester 
            FROM users 
            WHERE email = %s
        """, (email,))
        
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return dict(user) if user else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_admin_by_email(email):
    """Get admin by email"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
    admin = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return dict(admin) if admin else None

def register_user(email, password, name):
    """Register a new user"""
    next_billing_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO users 
            (email, password, name, membership, next_billing_date) 
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (email, password, name, 'free', next_billing_date)
        )
        user_id = cursor.fetchone()[0]
        
        # Log activity
        add_activity(f"New user registered: {name}")
        
        cursor.close()
        conn.close()
        return user_id
    except psycopg2.errors.UniqueViolation:
        cursor.close()
        conn.close()
        return None

def update_user_profile(current_email, data):
    """Update user profile"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        update_fields = []
        values = []
        
        # Build dynamic update query based on provided data
        if data.get('name'):
            update_fields.append("name = %s")
            values.append(data['name'])
        
        if data.get('email'):
            update_fields.append("email = %s")
            values.append(data['email'])
        
        if data.get('college'):
            update_fields.append("college = %s")
            values.append(data['college'])
            
        if data.get('department'):
            update_fields.append("department = %s")
            values.append(data['department'])
            
        if data.get('year'):
            update_fields.append("year = %s")
            values.append(data['year'])
            
        if data.get('semester'):
            update_fields.append("semester = %s")
            values.append(data['semester'])
        
        if data.get('password'):
            update_fields.append("password = %s")
            values.append(data['password'])
        
        if update_fields:
            query = f"""
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE email = %s
                RETURNING email
            """
            values.append(current_email)
            
            cursor.execute(query, values)
            updated_email = cursor.fetchone()[0]
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return updated_email
            
        return current_email
        
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return None

def update_user_subscription(user_email, membership):
    """Update user subscription"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate next billing date based on subscription type
    if membership == 'monthly':
        next_billing_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    elif membership == 'yearly':
        next_billing_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    else:  # Free subscription
        next_billing_date = None
    
    cursor.execute(
        "UPDATE users SET membership = %s, next_billing_date = %s WHERE email = %s",
        (membership, next_billing_date, user_email)
    )
    
    cursor.close()
    conn.close()
    return True

# ---- Book functions ----
def get_all_books():
    """Get all books"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT * FROM books ORDER BY title")
    books = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [dict(book) for book in books]

def get_book_by_id(book_id):
    """Get book by ID"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return dict(book) if book else None

def search_books(query="", sort="title", genre=""):
    """Search books with filtering and sorting"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    sql = "SELECT * FROM books WHERE 1=1"
    params = []
    
    # Apply search query filter
    if query:
        sql += """ AND (
            LOWER(title) LIKE %s OR 
            LOWER(author) LIKE %s OR 
            LOWER(genre) LIKE %s
        )"""
        search_term = f"%{query.lower()}%"
        params.extend([search_term, search_term, search_term])
    
    # Apply genre filter
    if genre:
        sql += " AND LOWER(genre) = %s"
        params.append(genre.lower())
    
    # Apply sorting
    if sort == "title":
        sql += " ORDER BY title"
    elif sort == "author":
        sql += " ORDER BY author"
    elif sort == "popularity":
        sql += " ORDER BY reads DESC"
    elif sort == "rating":
        sql += " ORDER BY rating DESC"
    
    cursor.execute(sql, params)
    books = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [dict(book) for book in books]

def get_all_genres():
    """Get all unique genres"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT genre FROM books ORDER BY genre")
    genres = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return genres

def add_book(title, author, genre, description, cover_image, book_file):
    """Add a new book"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO books 
        (title, author, genre, description, cover_image, book_file) 
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """,
        (title, author, genre, description, cover_image, book_file)
    )
    book_id = cursor.fetchone()[0]
    
    # Log activity
    add_activity(f"Added new book: {title}")
    
    cursor.close()
    conn.close()
    return book_id

def delete_book(book_id):
    """Delete a book"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get book title before deletion
    cursor.execute("SELECT title FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    
    if book:
        title = book[0]
        
        # Delete the book
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        
        # Log activity
        add_activity(f"Deleted book: {title}")
        
        cursor.close()
        conn.close()
        return True
    
    cursor.close()
    conn.close()
    return False

def increment_book_reads(book_id):
    """Increment the read count for a book"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE books 
            SET reads = reads + 1 
            WHERE id = %s
        """, (book_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error incrementing book reads: {e}")
        return False

# ---- Subscription functions ----
def get_all_subscription_plans():
    """Get all subscription plans"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT * FROM subscription_plans ORDER BY price")
    plans = cursor.fetchall()
    
    result = {}
    for plan in plans:
        plan_dict = dict(plan)
        # Check if features is already a list or needs to be parsed
        if isinstance(plan_dict['features'], str):
            try:
                plan_dict['features'] = json.loads(plan_dict['features'])
            except json.JSONDecodeError:
                # If JSON parsing fails, keep it as a string
                pass
        
        # Use name to create key in lowercase
        key = plan_dict['name'].lower().replace(' ', '_')
        result[key] = plan_dict
    
    cursor.close()
    conn.close()
    
    return result

# ---- Activity functions ----
def get_recent_activities(limit=10):
    """Get recent activities"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute(
        "SELECT * FROM activities ORDER BY timestamp DESC LIMIT %s",
        (limit,)
    )
    activities = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [dict(activity) for activity in activities]

def add_activity(description):
    """Add a new activity"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO activities (time, description) VALUES (%s, %s)",
        ('Just now', description)
    )
    
    cursor.close()
    conn.close()
    return True

# ---- Dashboard statistics ----
def get_dashboard_statistics():
    """Get statistics for admin dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get users count
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    
    # Get books count
    cursor.execute("SELECT COUNT(*) FROM books")
    books_count = cursor.fetchone()[0]
    
    # Get active subscriptions
    cursor.execute("SELECT COUNT(*) FROM users WHERE membership != 'free'")
    active_subscriptions = cursor.fetchone()[0]
    
    # Calculate revenue
    cursor.execute("""
        SELECT SUM(sp.price) 
        FROM users u 
        JOIN subscription_plans sp ON LOWER(sp.name) LIKE LOWER(CONCAT('%', u.membership, '%'))
        WHERE u.membership != 'free'
    """)
    revenue = cursor.fetchone()[0] or 0
    
    cursor.close()
    conn.close()
    
    return {
        'users_count': users_count,
        'books_count': books_count,
        'active_subscriptions': active_subscriptions,
        'revenue': revenue
    }

# Create database on import
if __name__ == "__main__":
    init_db() 