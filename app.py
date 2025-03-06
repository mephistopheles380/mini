from flask import Flask, render_template, redirect, url_for, request, flash, session
from functools import wraps
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize empty lists for books and activities
books = [
    {
        'id': '1',
        'title': 'Python Programming',
        'author': 'John Smith',
        'genre': 'Programming',
        'description': 'A comprehensive guide to Python programming language',
        'cover_image': 'covers/python_programming.jpg',
        'book_file': 'books/python_programming.pdf',
        'added_date': '2024-01-15',
        'reads': 150,
        'rating': 4.5
    },
    {
        'id': '2',
        'title': 'Data Structures and Algorithms',
        'author': 'Sarah Johnson',
        'genre': 'Computer Science',
        'description': 'Essential concepts of DSA with practical examples',
        'cover_image': 'covers/dsa.jpg',
        'book_file': 'books/dsa.pdf',
        'added_date': '2024-01-20',
        'reads': 120,
        'rating': 4.8
    },
    {
        'id': '3',
        'title': 'Web Development Basics',
        'author': 'Michael Brown',
        'genre': 'Web Development',
        'description': 'Introduction to HTML, CSS, and JavaScript',
        'cover_image': 'covers/web_dev.jpg',
        'book_file': 'books/web_dev.pdf',
        'added_date': '2024-02-01',
        'reads': 200,
        'rating': 4.3
    },
    {
        'id': '4',
        'title': 'Database Management Systems',
        'author': 'Emily Davis',
        'genre': 'Database',
        'description': 'Complete guide to modern database systems',
        'cover_image': 'covers/dbms.jpg',
        'book_file': 'books/dbms.pdf',
        'added_date': '2024-02-10',
        'reads': 90,
        'rating': 4.6
    },
    {
        'id': '5',
        'title': 'Machine Learning Fundamentals',
        'author': 'David Wilson',
        'genre': 'Artificial Intelligence',
        'description': 'Basic concepts and applications of ML',
        'cover_image': 'covers/ml.jpg',
        'book_file': 'books/ml.pdf',
        'added_date': '2024-02-15',
        'reads': 180,
        'rating': 4.7
    },
    {
        'id': '6',
        'title': 'Operating Systems',
        'author': 'Robert Taylor',
        'genre': 'Computer Science',
        'description': 'Understanding modern operating systems',
        'cover_image': 'covers/os.jpg',
        'book_file': 'books/os.pdf',
        'added_date': '2024-02-20',
        'reads': 110,
        'rating': 4.4
    },
    {
        'id': '7',
        'title': 'Software Engineering Principles',
        'author': 'Lisa Anderson',
        'genre': 'Software Engineering',
        'description': 'Best practices in software development',
        'cover_image': 'covers/se.jpg',
        'book_file': 'books/se.pdf',
        'added_date': '2024-02-25',
        'reads': 85,
        'rating': 4.2
    },
    {
        'id': '8',
        'title': 'Computer Networks',
        'author': 'James Miller',
        'genre': 'Networking',
        'description': 'Understanding computer networking concepts',
        'cover_image': 'covers/networks.jpg',
        'book_file': 'books/networks.pdf',
        'added_date': '2024-03-01',
        'reads': 95,
        'rating': 4.5
    },
    {
        'id': '9',
        'title': 'Cybersecurity Basics',
        'author': 'Alex Turner',
        'genre': 'Security',
        'description': 'Introduction to cybersecurity concepts',
        'cover_image': 'covers/security.jpg',
        'book_file': 'books/security.pdf',
        'added_date': '2024-03-05',
        'reads': 130,
        'rating': 4.6
    },
    {
        'id': '10',
        'title': 'Cloud Computing',
        'author': 'Rachel Green',
        'genre': 'Cloud Technology',
        'description': 'Modern cloud computing technologies',
        'cover_image': 'covers/cloud.jpg',
        'book_file': 'books/cloud.pdf',
        'added_date': '2024-03-10',
        'reads': 140,
        'rating': 4.4
    }
]

recent_activities = [
    {
        'time': '2 mins ago',
        'description': 'Added new book: Cloud Computing'
    },
    {
        'time': '10 mins ago',
        'description': 'Updated book: Python Programming'
    },
    {
        'time': '1 hour ago',
        'description': 'New user registered'
    },
    {
        'time': '2 hours ago',
        'description': 'Added new book: Cybersecurity Basics'
    },
    {
        'time': '1 day ago',
        'description': 'Book "Machine Learning Fundamentals" viewed 50 times'
    }
]

# Sample in-memory database with complete user information
users_db = {
    'user@example.com': {
        'password': 'userpass123',
        'name': 'John Doe',
        'email': 'user@example.com',
        'role': 'user',
        'membership': 'monthly',
        'joined_date': '2024-01-01',
        'next_billing_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'college': 'Sample College',
        'department': 'Computer Science',
        'year': '2',
        'semester': '4'
    },
    'user2@example.com': {  # Added second user
        'password': 'userpass456',
        'name': 'Jane Smith',
        'email': 'user2@example.com',
        'role': 'user',
        'membership': 'free',
        'joined_date': '2024-02-01',
        'next_billing_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'college': 'Tech University',
        'department': 'Information Technology',
        'year': '3',
        'semester': '5'
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
    # Clear the session
    session.clear()
    flash('You have been logged out successfully', 'success')
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
    user_email = session.get('user')
    if user_email not in users_db:
        flash('User not found', 'error')
        return redirect(url_for('logout'))
    
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

@app.route('/search')
def search():
    query = request.args.get('q', '')
    sort = request.args.get('sort', 'title')
    
    # Filter books based on search query
    filtered_books = [
        book for book in books 
        if query.lower() in book['title'].lower() or 
           query.lower() in book['author'].lower() or 
           query.lower() in book['genre'].lower()
    ]
    
    # Sort books based on sort parameter
    if sort == 'title':
        filtered_books.sort(key=lambda x: x['title'])
    elif sort == 'author':
        filtered_books.sort(key=lambda x: x['author'])
    elif sort == 'popularity':
        filtered_books.sort(key=lambda x: x['reads'], reverse=True)
    elif sort == 'rating':
        filtered_books.sort(key=lambda x: x['rating'], reverse=True)
    
    # Get unique genres for filter sidebar
    genres = sorted(set(book['genre'] for book in books))
    
    return render_template('search_results.html', 
                         books=filtered_books,
                         genres=genres,
                         query=query)

if __name__ == '__main__':
    app.run(debug=True)