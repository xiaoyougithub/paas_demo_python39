-- Create database if not exists
CREATE DATABASE IF NOT EXISTS test;
USE test;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample users
INSERT INTO users (name, email) VALUES
    ('John Doe', 'john@example.com'),
    ('Jane Smith', 'jane@example.com'),
    ('Bob Johnson', 'bob@example.com'),
    ('Alice Brown', 'alice@example.com'),
    ('Charlie Wilson', 'charlie@example.com');

-- Insert sample orders
INSERT INTO orders (user_id, amount, status) VALUES
    (1, 99.99, 'completed'),
    (1, 150.50, 'pending'),
    (2, 75.25, 'completed'),
    (3, 200.00, 'cancelled'),
    (2, 50.00, 'pending'),
    (4, 125.75, 'completed'),
    (5, 300.00, 'pending'),
    (3, 89.99, 'completed'),
    (4, 175.50, 'pending'),
    (5, 250.00, 'completed');