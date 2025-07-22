import mysql.connector
import pandas as pd
from mysql.connector import Error
import bcrypt
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='mysql',
                database='sec_proj',
                port=3306,
                auth_plugin = 'mysql_native_password',
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise

    def get_table(self, table_name):
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            data = self.cursor.fetchall()
            return pd.DataFrame(data)
        except Error as e:
            logger.error(f"Error fetching table {table_name}: {e}")
            return pd.DataFrame()

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Error as e:
            logger.error(f"Error executing query: {e}")
            self.conn.rollback()
            return False

    def fetch_one(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Error as e:
            logger.error(f"Error fetching one: {e}")
            return None

    def fetch_all(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            logger.error(f"Error fetching all: {e}")
            return []

    def close_connection(self):
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

    # Security-related methods
    def log_audit_event(self, user_id, log_type, ip_address=None, user_agent=None, details=None):
        query = """
        INSERT INTO audit_log 
        (user_id, log_type, ip_address, user_agent, details) 
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (user_id, log_type, ip_address, user_agent, details)
        return self.execute_query(query, params)

    def increment_failed_login(self, username_or_email):
        query = """
        UPDATE users 
        SET failed_login_attempts = failed_login_attempts + 1 
        WHERE username = %s OR email = %s
        """
        params = (username_or_email, username_or_email)
        return self.execute_query(query, params)

    def lock_account(self, username_or_email):
        query = """
        UPDATE users 
        SET account_locked = TRUE 
        WHERE username = %s OR email = %s
        """
        params = (username_or_email, username_or_email)
        return self.execute_query(query, params)

    def reset_login_attempts(self, user_id):
        query = "UPDATE users SET failed_login_attempts = 0 WHERE user_id = %s"
        return self.execute_query(query, (user_id,))