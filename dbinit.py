# import sqlite3
# from dbmanager import *
# def init_db():
#     conn = sqlite3.connect("ecothriftt.db")
#     cursor = conn.cursor()
#     # Users Table
#     cursor.execute('''DROP TABLE IF EXISTS users''')
#     cursor.execute('''DROP TABLE IF EXISTS listings''')
#     cursor.execute('''DROP TABLE IF EXISTS transactions''')
#     cursor.execute('''DROP TABLE IF EXISTS cases''')
#     cursor.execute('''DROP TABLE IF EXISTS faqs''')
#     cursor.execute('''CREATE TABLE IF NOT EXISTS users (
#                       user_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                       username TEXT NOT NULL UNIQUE,
#                       email TEXT NOT NULL UNIQUE,
#                       profile_pic TEXT,
#                       password TEXT NOT NULL,
#                       name TEXT,
#                       phone_number INTEGER UNIQUE,
#                       twofa BOOLEAN NOT NULL DEFAULT FALSE,
#                       is_admin BOOLEAN NOT NULL DEFAULT FALSE
#                     )''')
#
#     # Listings Table
#     cursor.execute('''CREATE TABLE IF NOT EXISTS listings (
#                       listing_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                       user_id INTEGER NOT NULL,
#                       title TEXT NOT NULL,
#                       description TEXT,
#                       category TEXT,
#                       price REAL NOT NULL,
#                       image_path TEXT,
#                       is_sold BOOLEAN NOT NULL DEFAULT FALSE,
#                       FOREIGN KEY (user_id) REFERENCES users(user_id)
#                     )''')
#
#     # Transactions Table
#     cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
#                       transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                       listing_id INTEGER NOT NULL,
#                       buyer_id INTEGER NOT NULL,
#                       transaction_date DATETIME NOT NULL,
#                       FOREIGN KEY (listing_id) REFERENCES listings(listing_id),
#                       FOREIGN KEY (buyer_id) REFERENCES users(user_id)
#                     )''')
#
#     conn.commit()
#     conn.close()
#
# init_db()
#
# db = DBManager()
# print('Users Table')
# print(DBManager().get_table("users").to_string(index=False))
#
# print('Listings Table')
# print(DBManager().get_table("listings").to_string(index=False))
#
# print('Transactions Table')
# print(DBManager().get_table("transactions").to_string(index=False))

# start


import mysql.connector
from mysql.connector import Error
import logging

logger = logging.getLogger(__name__)


def init_db():
    conn = None  # Initialize conn outside try block
    try:
        # Connect to MySQL server (without specifying a database)
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='dbmsPa55',
            port=3306,
            auth_plugin='mysql_native_password'  # Explicitly specify auth plugin
        )

        cursor = conn.cursor()
        cursor = conn.cursor()

        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS pytonlogin2")
        cursor.execute("USE pytonlogin2")

        # Create all tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                salt VARCHAR(100) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                phone VARCHAR(20),
                is_verified BOOLEAN DEFAULT FALSE,
                failed_login_attempts INT DEFAULT 0,
                account_locked BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INT AUTO_INCREMENT PRIMARY KEY,
                category_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                stock_quantity INT NOT NULL DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status ENUM('pending','processing','shipped','delivered','cancelled') DEFAULT 'pending',
                total_amount DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                user_id INT,
                amount DECIMAL(10,2) NOT NULL,
                method ENUM('credit_card','paypal','bank_transfer','paynow') NOT NULL,
                status ENUM('pending','completed','failed','refunded') NOT NULL,
                transaction_id VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_history (
                history_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                salt VARCHAR(100) NOT NULL,
                changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL UNIQUE,
                access_level ENUM('super_admin','support_admin') NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                log_type ENUM(
                    'login', 'logout', 'login_failed',
                    'password_change', 'admin_action',
                    'payment_processed', '2fa_attempt',
                    'data_deletion', 'system'
                ) NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_methods (
                method_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                method_type ENUM('email', 'sms', 'authenticator') NOT NULL,
                email VARCHAR(100),
                phone_number VARCHAR(20),
                secret_key VARCHAR(255),
                is_verified BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )''')

        # Create indexes
        cursor.execute('CREATE INDEX idx_user_email ON users(email)')
        cursor.execute('CREATE INDEX idx_user_phone ON users(phone)')
        cursor.execute('CREATE INDEX idx_product_category ON products(category_id)')
        cursor.execute('CREATE INDEX idx_product_name ON products(name)')
        cursor.execute('CREATE INDEX idx_order_user ON orders(user_id)')
        cursor.execute('CREATE INDEX idx_order_status ON orders(status)')
        cursor.execute('CREATE INDEX idx_order_date ON orders(order_date)')
        cursor.execute('CREATE INDEX idx_payment_order ON payments(order_id)')
        cursor.execute('CREATE INDEX idx_payment_user ON payments(user_id)')
        cursor.execute('CREATE INDEX idx_payment_status ON payments(status)')
        cursor.execute('CREATE INDEX idx_audit_log_user ON audit_log(user_id)')
        cursor.execute('CREATE INDEX idx_audit_log_type ON audit_log(log_type)')
        cursor.execute('CREATE INDEX idx_audit_log_time ON audit_log(created_at)')

        # Insert initial admin user if not exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
        if cursor.fetchone()[0] == 0:
            # Create admin user with default password "admin123"
            salt = 'random_salt_value'  # In practice, use bcrypt.gensalt()
            password_hash = 'hashed_password'  # In practice, use bcrypt.hashpw()

            cursor.execute('''
                INSERT INTO users 
                (username, email, password_hash, salt, first_name, last_name, is_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', ('admin', 'admin@example.com', password_hash, salt, 'Admin', 'User', True))

            admin_user_id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO admins (user_id, access_level) 
                VALUES (%s, %s)
                ''', (admin_user_id, 'super_admin'))

        conn.commit()
        logger.info("Database and tables created successfully")

    except Error as e:
        logger.error(f"Error initializing database: {e}")
        if "Authentication plugin" in str(e):
            logger.error("Authentication failed. Possible solutions:")
            logger.error(
                "1. Run in MySQL: ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'mysql';")
            logger.error("2. Or install the latest connector: pip install mysql-connector-python --upgrade")
        raise  # Re-raise the exception after logging
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    if __name__ == '__main__':
        init_db()