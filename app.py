from flask import Flask, render_template, redirect, url_for, request, flash, session
from functools import wraps
from datetime import datetime, timedelta, date
import os
from werkzeug.utils import secure_filename
import database as db  # Import our database module
import fitz  # PyMuPDF for PDF handling
import io
from PIL import Image
import psycopg2
from psycopg2.extras import DictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
app.permanent_session_lifetime = timedelta(days=7)

# Optional: Configure session to be more secure
app.config['SESSION_COOKIE_SECURE'] = True  # For HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# File upload configurations
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directories if they don't exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'covers'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'books'), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'user')

        try:
            conn = get_db_connection()
            if conn is None:
                flash('Database connection error', 'error')
                return render_template('login.html')

            cur = conn.cursor(cursor_factory=DictCursor)
            
            # Select from appropriate table based on user type
            table = 'admins' if user_type == 'admin' else 'users'
            cur.execute(f"SELECT * FROM {table} WHERE email = %s", (email,))
            user = cur.fetchone()

            if user:
                # For testing purposes, add a print statement
                print(f"Found user: {user['email']}, checking password...")
                
                # If using plain text passwords temporarily (for testing)
                if user['password'] == password:  # Remove this in production
                    session.permanent = True
                    session['user'] = user['email']
                    session['name'] = user['name']
                    session['role'] = user_type
                    flash('Logged in successfully!', 'success')
                    return redirect(url_for('admin_dashboard' if user_type == 'admin' else 'home'))
                
                # For hashed passwords (use this in production)
                # if check_password_hash(user['password'], password):
                #     session.permanent = True
                #     session['user'] = user['email']
                #     session['name'] = user['name']
                #     session['role'] = user_type
                #     flash('Logged in successfully!', 'success')
                #     return redirect(url_for('admin_dashboard' if user_type == 'admin' else 'home'))
            
            flash('Invalid email or password', 'error')
            
        except Exception as e:
            print(f"Login error: {e}")
            flash('An error occurred during login', 'error')
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals() and conn:
                conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if user already exists
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Email already registered', 'error')
                return redirect(url_for('register'))
            
            # Insert new user
            hashed_password = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed_password)
            )
            
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Registration error: {e}")
            flash('An error occurred during registration', 'error')
    
    return render_template('register.html')

@app.route('/home')
@login_required
def home():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        
        cur.execute("""
            SELECT b.*, COALESCE(b.cover_image, 'images/default-cover.png') as cover_image
            FROM books b
            ORDER BY b.added_date DESC
        """)
        
        books = []
        for row in cur.fetchall():
            book = dict(row)
            # Ensure cover_image has a value
            if not book['cover_image']:
                book['cover_image'] = 'images/default-cover.png'
            # Convert numeric types
            book['rating'] = float(book['rating']) if book['rating'] else 0.0
            book['reads'] = int(book['reads']) if book['reads'] else 0
            books.append(book)
        
        cur.close()
        conn.close()
        
        return render_template('home.html', books=books)
    except Exception as e:
        print(f"Error in home route: {e}")
        flash('Error loading books', 'error')
        return render_template('home.html', books=[])

@app.route('/admin')
@admin_required
def admin_dashboard():
    if session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get dashboard statistics
    stats = db.get_dashboard_statistics()
    
    # Get books and activities
    books = db.get_all_books()
    recent_activities = db.get_recent_activities()
    
    dashboard_data = {
        'users_count': stats['users_count'],
        'books_count': stats['books_count'],
        'books': books,
        'active_subscriptions': stats['active_subscriptions'],
        'revenue': stats['revenue'],
        'recent_activities': recent_activities
    }
    
    return render_template('admin_dashboard.html', **dashboard_data)

@app.route('/profile')
@login_required
def profile():
    user_email = session.get('user')
    user_data = db.get_user_by_email(user_email)
    
    if not user_data:
        flash('User not found', 'error')
        return redirect(url_for('logout'))
    
    # Set default values if they don't exist
    default_values = {
        'college': '',
        'department': '',
        'year': '',
        'semester': '',
        'membership': 'free',
        'joined_date': datetime.now().strftime('%Y-%m-%d'),
        'next_billing_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    }
    
    for key, value in default_values.items():
        if key not in user_data or not user_data[key]:
            user_data[key] = value
    
    subscription_plans = db.get_all_subscription_plans()
    
    return render_template('profile.html', 
                         user_data=user_data, 
                         subscription_plans=subscription_plans,
                         edit_mode=False)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user_email = session['user']
    name = request.form.get('name')
    email = request.form.get('email')
    college = request.form.get('college')
    department = request.form.get('department')
    year = request.form.get('year')
    semester = request.form.get('semester')
    password = request.form.get('password')

    # Update user profile
    success = db.update_user_profile(user_email, {
        'name': name,
        'email': email,
        'college': college,
        'department': department,
        'year': year,
        'semester': semester,
        'password': password if password else None
    })
    
    if success:
        session['user'] = email  # Update session with new email if changed
        session['name'] = name
        flash('Profile updated successfully!', 'success')
    else:
        flash('Profile update failed!', 'error')
    
    return redirect(url_for('profile'))

@app.route('/add_book', methods=['POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            author = request.form.get('author')
            genre = request.form.get('genre')
            description = request.form.get('description')
            
            # Handle book file
            book_file = request.files['book_file']
            if not book_file or not allowed_file(book_file.filename):
                flash('Invalid file format. Please upload a PDF file.', 'error')
                return redirect(url_for('admin_dashboard'))
            
            # Save book file
            book_filename = secure_filename(f"{title}_{book_file.filename}")
            book_path = os.path.join(app.config['UPLOAD_FOLDER'], 'books', book_filename)
            book_file.save(book_path)
            
            # Generate cover from PDF
            cover_path = process_pdf_cover(book_path, title)
            if not cover_path:
                flash('Failed to generate cover image, but book was uploaded.', 'warning')
            
            # Add to database
            book_id = db.add_book(
                title=title,
                author=author,
                genre=genre,
                description=description,
                cover_image=cover_path,
                book_file=f"books/{book_filename}"
            )
            
            if book_id:
                flash('Book added successfully!', 'success')
            else:
                flash('Failed to add book to database!', 'error')
                
        except Exception as e:
            flash(f'Error adding book: {str(e)}', 'error')
            
        return redirect(url_for('admin_dashboard'))

@app.route('/delete_book/<book_id>')
@admin_required
def delete_book(book_id):
    # Get book details before deletion to handle file removal
    book = db.get_book_by_id(book_id)
    
    if book:
        # Remove files
        if book['cover_image']:
            cover_path = os.path.join(app.config['UPLOAD_FOLDER'], book['cover_image'])
            try:
                os.remove(cover_path)
            except:
                pass
        
        if book['book_file']:
            book_path = os.path.join(app.config['UPLOAD_FOLDER'], book['book_file'])
            try:
                os.remove(book_path)
            except:
                pass
        
        # Delete from database
        success = db.delete_book(book_id)
        
        if success:
            flash('Book deleted successfully!', 'success')
        else:
            flash('Failed to delete book!', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/subscription')
@login_required
def subscription():
    user_email = session.get('user')
    user_data = db.get_user_by_email(user_email)
    
    if not user_data:
        flash('User not found', 'error')
        return redirect(url_for('logout'))
    
    # Set default membership if none exists
    if not user_data.get('membership'):
        user_data['membership'] = 'free'
    
    subscription_plans = db.get_all_subscription_plans()
    
    return render_template('subscription.html', 
                         user_data=user_data,
                         subscription_plans=subscription_plans)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    sort = request.args.get('sort', 'title')
    selected_genre = request.args.get('genre', '')
    
    # Get books using database search function
    filtered_books = db.search_books(query, sort, selected_genre)
    
    # Get unique genres for filter sidebar
    genres = db.get_all_genres()
    
    return render_template('search_results.html', 
                         books=filtered_books,
                         genres=genres,
                         query=query,
                         selected_genre=selected_genre)

@app.route('/update_subscription', methods=['POST'])
@login_required
def update_subscription():
    user_email = session['user']
    membership = request.form.get('membership')
    
    success = db.update_user_subscription(user_email, membership)
    
    if success:
        flash('Subscription updated successfully!', 'success')
    else:
        flash('Failed to update subscription!', 'error')
    
    return redirect(url_for('subscription'))

@app.route('/book/<int:book_id>')
@login_required
def view_book(book_id):
    book = db.get_book_by_id(book_id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('home'))
    
    # Log book view
    db.increment_book_reads(book_id)
    
    return render_template('book_viewer.html', book=book)

@app.template_filter('string')
def string_filter(value):
    """Convert date to string format"""
    if isinstance(value, (date, datetime)):
        return value.strftime('%Y-%m-%d')
    return str(value)

def process_pdf_cover(pdf_path, title):
    """Generate cover image from PDF first page"""
    try:
        pdf_document = fitz.open(pdf_path)
        if pdf_document.page_count == 0:
            raise ValueError("PDF has no pages")
            
        first_page = pdf_document[0]
        pix = first_page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        cover_filename = secure_filename(f"{title}_cover.jpg")
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], 'covers', cover_filename)
        
        # Resize and crop to standard book cover dimensions (2:3 ratio)
        width, height = img.size
        target_ratio = 2/3
        current_ratio = width/height
        
        if current_ratio > target_ratio:
            # Image is too wide
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            img = img.crop((left, 0, left + new_width, height))
        elif current_ratio < target_ratio:
            # Image is too tall
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            img = img.crop((0, top, width, top + new_height))
            
        img = img.resize((800, 1200), Image.Resampling.LANCZOS)
        img.save(cover_path, "JPEG", quality=90)
        
        pdf_document.close()
        return f"covers/{cover_filename}"
    except Exception as e:
        print(f"Error processing PDF cover: {e}")
        return None

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'library_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Create necessary directories
def create_directories():
    directories = [
        os.path.join(app.static_folder, 'images'),
        os.path.join(app.static_folder, 'uploads', 'books'),
        os.path.join(app.static_folder, 'uploads', 'covers')
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Create default cover image
def create_default_cover():
    from PIL import Image, ImageDraw
    default_cover_path = os.path.join(app.static_folder, 'images', 'default-cover.png')
    if not os.path.exists(default_cover_path):
        img = Image.new('RGB', (200, 300), color='#f0f0f0')
        d = ImageDraw.Draw(img)
        d.text((100, 150), "No Cover", fill='#666666', anchor="mm")
        img.save(default_cover_path)

# Initialize app
def init_app():
    create_directories()
    create_default_cover()

# Add this temporary route to create a test user
@app.route('/setup_test_user')
def setup_test_user():
    try:
        conn = get_db_connection()
        if conn is None:
            return 'Database connection failed', 500

        cur = conn.cursor()
        
        # Create users table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create admins table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert a test user
        cur.execute("""
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, ('Test User', 'test@example.com', 'password123'))
        
        # Insert a test admin
        cur.execute("""
            INSERT INTO admins (name, email, password)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, ('Admin User', 'admin@example.com', 'admin123'))
        
        conn.commit()
        return 'Test users created successfully!'
    except Exception as e:
        print(f"Setup error: {e}")
        return f'Error: {str(e)}', 500
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == '__main__':
    # Initialize the database
    db.init_db()
    init_app()
    app.run(debug=True)