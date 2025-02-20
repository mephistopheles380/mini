from flask import Flask, render_template, redirect, url_for, request, flash, session
from functools import wraps
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize empty lists for books and activities
books = []
recent_activities = []

# Sample in-memory database with complete user information
users_db = {
    'user@example.com': {
        'password': 'userpass123',
        'name': 'John Doe',
        'email': 'user@example.com',
        'role': 'user',
        'membership': 'monthly',
        'joined_date': '2024-01-01',
        'next_billing_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    }
}

admin_db = {
    'admin@library.com': {
        'password': 'adminpass123',
        'name': 'Admin User',
        'role': 'admin'
    }
}

# Subscription plans data
subscription_plans = {
    'monthly': {
        'name': 'Monthly',
        'price': 199,
        'features': [
            'Access to all eBooks',
            'Read online & offline',
            'Monthly new releases',
            'Basic support'
        ]
    },
    'quarterly': {
        'name': 'Quarterly',
        'price': 499,
        'features': [
            'All Monthly features',
            'Priority access to new releases',
            'Premium support',
            'Exclusive author interviews'
        ]
    },
    'annual': {
        'name': 'Annual',
        'price': 1499,
        'features': [
            'All Quarterly features',
            'Free audiobooks',
            '24/7 Premium support',
            'Early access to pre-releases',
            'Virtual book club membership'
        ]
    }
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
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

@app.route('/login')
def login():
    if 'user' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    user_type = request.form.get('user_type')

    if user_type == 'user':
        if email in users_db and users_db[email]['password'] == password:
            session['user'] = email
            session['role'] = 'user'
            session['name'] = users_db[email]['name']
            return redirect(url_for('home'))
    elif user_type == 'admin':
        if email in admin_db and admin_db[email]['password'] == password:
            session['user'] = email
            session['role'] = 'admin'
            session['name'] = admin_db[email]['name']
            return redirect(url_for('admin_dashboard'))

    flash('Invalid credentials')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        if email in users_db:
            flash('Email already registered')
            return redirect(url_for('register'))

        # Create new user with complete information
        users_db[email] = {
            'password': password,
            'name': name,
            'email': email,
            'role': 'user',
            'membership': 'monthly',
            'joined_date': datetime.now().strftime('%Y-%m-%d'),
            'next_billing_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/home')
@login_required
def home():
    if session['role'] != 'user':
        return redirect(url_for('login'))
    return render_template('home.html', books=books)

@app.route('/admin')
@admin_required
def admin_dashboard():
    if session['role'] != 'admin':
        return redirect(url_for('login'))
    
    dashboard_data = {
        'users_count': len(users_db),
        'books_count': len(books),
        'books': books,
        'active_subscriptions': sum(1 for user in users_db.values() if user.get('membership')),
        'revenue': calculate_revenue(),
        'recent_activities': recent_activities
    }
    
    return render_template('admin_dashboard.html', **dashboard_data)

def calculate_revenue():
    total = 0
    for user in users_db.values():
        if user.get('membership'):
            plan_price = subscription_plans[user['membership'].lower()]['price']
            total += plan_price
    return total

@app.route('/profile')
@login_required
def profile():
    user_email = session['user']
    user_data = users_db[user_email]
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
    password = request.form.get('password')

    # Update user information
    users_db[user_email]['name'] = name
    
    # Update email if changed
    if email != user_email:
        users_db[email] = users_db.pop(user_email)
        session['user'] = email

    # Update password if provided
    if password:
        users_db[email]['password'] = password

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

# File upload configurations
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directories if they don't exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'covers'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'books'), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_book', methods=['POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        description = request.form.get('description')
        
        # Handle cover image
        cover_image = request.files['cover_image']
        cover_filename = None
        if cover_image and allowed_file(cover_image.filename):
            cover_filename = secure_filename(f"{title}_{cover_image.filename}")
            cover_path = os.path.join(app.config['UPLOAD_FOLDER'], 'covers', cover_filename)
            cover_image.save(cover_path)
        
        # Handle book file
        book_file = request.files['book_file']
        book_filename = None
        if book_file and allowed_file(book_file.filename):
            book_filename = secure_filename(f"{title}_{book_file.filename}")
            book_path = os.path.join(app.config['UPLOAD_FOLDER'], 'books', book_filename)
            book_file.save(book_path)
        
        # Add book to database
        new_book = {
            'id': str(len(books) + 1),
            'title': title,
            'author': author,
            'genre': genre,
            'description': description,
            'cover_image': f"covers/{cover_filename}" if cover_filename else None,
            'book_file': f"books/{book_filename}" if book_filename else None,
            'added_date': datetime.now().strftime('%Y-%m-%d'),
            'reads': 0,
            'rating': 0
        }
        
        books.append(new_book)
        
        # Add to recent activities
        activity = {
            'time': 'Just now',
            'description': f'Added new book: {title}'
        }
        recent_activities.insert(0, activity)
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

@app.route('/delete_book/<book_id>')
@admin_required
def delete_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        # Remove files
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], book['cover_image'])
        book_path = os.path.join(app.config['UPLOAD_FOLDER'], book['book_file'])
        
        try:
            os.remove(cover_path)
            os.remove(book_path)
        except:
            pass
        
        # Remove from database
        books.remove(book)
        
        # Add to recent activities
        activity = {
            'time': 'Just now',
            'description': f'Deleted book: {book["title"]}'
        }
        recent_activities.insert(0, activity)
        
        flash('Book deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/subscription')
@login_required
def subscription():
    user_email = session['user']
    user_data = users_db[user_email]
    return render_template('subscription.html', 
                         user_data=user_data,
                         subscription_plans=subscription_plans)

if __name__ == '__main__':
    app.run(debug=True)