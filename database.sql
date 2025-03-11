-- Create database if it doesn't exist
CREATE DATABASE library_db;

-- Connect to the database
\c library_db

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    membership VARCHAR(50) DEFAULT 'free',
    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    college VARCHAR(100),
    department VARCHAR(100),
    year VARCHAR(10),
    semester VARCHAR(10)
);

-- Create admins table
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Create books table
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    description TEXT,
    cover_image VARCHAR(255),
    book_file VARCHAR(255) NOT NULL,
    rating DECIMAL(3,2) DEFAULT 0,
    reads INTEGER DEFAULT 0,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    language VARCHAR(20) DEFAULT 'en'
);

-- Create subscription_plans table
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    features TEXT[]
); 