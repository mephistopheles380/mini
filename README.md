# Library Management System

A Flask-based library management system with PostgreSQL database.

## Setup Instructions

### 1. Database Setup

First, make sure PostgreSQL is installed on your system. Then create a new database:

```sql
CREATE DATABASE library_db;
```

### 2. Configure Database Connection

Edit the `database.py` file and update the `DB_CONFIG` dictionary with your PostgreSQL credentials:

```python
DB_CONFIG = {
    'dbname': 'ldb',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}
```

### 3. Install Dependencies

```bash
# First, uninstall if you have any existing psycopg2 installation
pip uninstall psycopg2-binary psycopg2

# Then install the binary package
pip install --only-binary :all: psycopg2-binary
```

### 4. Run the Application

```bash
python app.py
```

The application will initialize the database tables and populate them with sample data on the first run.

### 5. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000/
```

## Default Credentials

### Admin User
- Email: admin@library.com
- Password: adminpass123

### Regular User
- Email: user@example.com  
- Password: userpass123

## Database Schema

The application uses the following database tables:

1. `users` - Store user information
2. `admins` - Store admin information
3. `books` - Store book information
4. `subscription_plans` - Store subscription plan details
5. `activities` - Store system activities

## Features

- User authentication and registration
- Admin dashboard for managing books and users
- Book browsing with search and filter functionality
- Subscription plans management
- User profile management 