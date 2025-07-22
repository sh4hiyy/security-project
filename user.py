# from dbmanager import DBManager
# import bcrypt
# from sendemail import *
# class User(DBManager):
#   def __init__(self, user_id=None, username=None, email=None, profile_pic=None, password=None, name=None, phone_number=None, twofa=False, is_admin=False):
#     super().__init__()  # Call the parent class constructor (DatabaseManager)
#     self.user_id = user_id
#     self.username = username
#     self.email = email
#     self.profile_pic = profile_pic
#     self.password = password
#     self.name = name
#     self.phone_number = phone_number
#     self.twofa = twofa
#     self.is_admin = is_admin
#
#   def create_user(self):
#     salt = bcrypt.gensalt()
#     hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), salt).decode('utf-8')
#     try:
#       cursor = self.conn.cursor()
#
#       # Check for username availability
#       cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (self.username,))
#       username_count = cursor.fetchone()[0]
#
#       # Check for email availability
#       cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (self.email,))
#       email_count = cursor.fetchone()[0]
#
#       if username_count > 0:
#         return "Username already exists."
#       elif email_count > 0:
#         return "Email already registered."
#
#       # Insert user data if unique
#       cursor.execute(
#         """INSERT INTO users (username, email, profile_pic, password, name, phone_number, twofa, is_admin) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
#         (self.username, self.email, self.profile_pic, hashed_password, self.name, self.phone_number, self.twofa,
#          self.is_admin))
#       self.conn.commit()
#       self.user_id = cursor.lastrowid
#       cursor.close()
#       return None  # No errors, return None
#
#     except Exception as e:
#       print(f"Error creating user: {e}")
#       return "An error occurred during registration."
#
#   def edit_user(self):
#     if not self.user_id:
#       print("Error: User ID not set. Please load a user before editing.")
#       return
#     cursor = self.conn.cursor()
#     cursor.execute("""UPDATE users SET username = ?, email = ?, profile_pic = ?, name = ?, phone_number = ?, twofa = ?, is_admin = ? WHERE user_id = ?""", (self.username, self.email, self.profile_pic, self.name, self.phone_number, self.twofa, self.is_admin, self.user_id))
#     self.conn.commit()
#     cursor.close()
#
#   def edit_password(self):
#     try:
#       salt = bcrypt.gensalt()
#       hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), salt).decode('utf-8')
#
#       cursor = self.conn.cursor()
#       cursor.execute("""UPDATE users SET password = ? WHERE user_id = ?""", (hashed_password, self.user_id))
#       self.conn.commit()
#       cursor.close()
#       return None  # No errors
#
#     except Exception as e:
#       print(f"Error editing password: {e}")
#       return "An error occurred while updating password."
#
#   def delete_user(self):
#     if not self.user_id:
#       print("Error: User ID not set. Please load a user before deleting.")
#       return
#     cursor = self.conn.cursor()
#     cursor.execute("""DELETE FROM users WHERE user_id = ?""", (self.user_id,))
#     self.conn.commit()
#     cursor.close()
#
#   def verify_password(self, password):
#     password = password.encode('utf-8')
#     hashed_password = self.password.encode('utf-8')
#     return bcrypt.checkpw(password, hashed_password)
#
#   def login(self, credential, password):
#     cursor = self.conn.cursor()
#     cursor.execute("""SELECT * FROM users WHERE username = ? OR email = ?""",
#                    (credential, credential))  # Allow login by username or email
#     user_data = cursor.fetchone()
#     cursor.close()
#
#     if user_data:
#       self.password = user_data[4]
#       if self.verify_password(password):  # Call verify_password function
#         self.twofa = user_data[7]
#         if self.twofa == True:
#           self.user_id = user_data[0]
#           self.email = user_data[2]
#           return True, True
#
#         else:
#           self.user_id = user_data[0]
#           self.username = user_data[1]
#           self.email = user_data[2]
#           self.profile_pic = user_data[3]
#           # self.password = user_data[4]
#           self.name = user_data[5]
#           self.phone_number = user_data[6]
#           self.twofa = user_data[7]
#           self.is_admin = user_data[8]
#           return True, False
#
#       else:
#         return False, {"message": "Invalid password"}
#     else:
#       return False, {"message": "Username or email not found"}
#
#
#
#   def get_user_by_id(self):
#       cursor = self.conn.cursor()
#       cursor.execute("SELECT * FROM users WHERE user_id = ?", (self.user_id,))
#       user_data = cursor.fetchone()
#       cursor.close()
#       self.user_id = user_data[0]
#       self.username = user_data[1]
#       self.email = user_data[2]
#       self.profile_pic = user_data[3]
#       self.password = user_data[4]
#       self.name = user_data[5]
#       self.phone_number = user_data[6]
#       self.twofa = user_data[7]
#       self.is_admin = user_data[8]
#       return user_data
#
#   def get_user_by_username(self):
#     cursor = self.conn.cursor()
#     cursor.execute("SELECT * FROM users WHERE username = ?", (self.username,))
#     user_data = cursor.fetchone()
#     cursor.close()
#     self.user_id = user_data[0]
#     self.username = user_data[1]
#     self.email = user_data[2]
#     self.profile_pic = user_data[3]
#     self.password = user_data[4]
#     self.name = user_data[5]
#     self.phone_number = user_data[6]
#     self.twofa = user_data[7]
#     self.is_admin = user_data[8]
#     return user_data
#
#   def get_user_by_email(self):
#     cursor = self.conn.cursor()
#     cursor.execute("SELECT * FROM users WHERE email = ?", (self.email,))
#     user_data = cursor.fetchone()
#     cursor.close()
#     self.user_id = user_data[0]
#     self.username = user_data[1]
#     self.email = user_data[2]
#     self.profile_pic = user_data[3]
#     self.password = user_data[4]
#     self.name = user_data[5]
#     self.phone_number = user_data[6]
#     self.twofa = user_data[7]
#     self.is_admin = user_data[8]
#     return user_data
#
#   def verify_otp(self, otp, sent_otp):
#     if str(otp) == str(sent_otp):  # Replace with actual OTP validation logic
#       user_data = self.get_user_by_email()
#       self.user_id = user_data[0]
#       self.username = user_data[1]
#       self.email = user_data[2]
#       self.profile_pic = user_data[3]
#       self.password = user_data[4]
#       self.name = user_data[5]
#       self.phone_number = user_data[6]
#       self.twofa = user_data[7]
#       self.is_admin = user_data[8]
#       return True
#     else:
#       return False
#

import re
import bcrypt
from datetime import datetime
from dbmanager import DBManager
from sendemail import Email
import logging

logger = logging.getLogger(__name__)

class User(DBManager):
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 30  # minutes

    def __init__(self, user_id=None, username=None, email=None, password=None,
                first_name=None, last_name=None, phone=None, is_verified=False, is_admin=False, profile_pic=None):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password  # Plain text for new users
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.is_verified = is_verified
        self.salt = None
        self.password_hash = None
        self.failed_login_attempts = 0
        self.account_locked = False
        self.created_at = None
        self.is_admin = is_admin
        self.profile_pic = profile_pic

    def validate_password_complexity(self, password):
        """Check password meets complexity rules."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain an uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "Password must contain a lowercase letter"
        if not re.search(r"[0-9]", password):
            return False, "Password must contain a digit"
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain a special character"
        return True, "Password is valid"

    def hash_password(self, password):
        """Generate salt and hash password."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8'), salt.decode('utf-8')

    def create_user(self, ip_address=None, user_agent=None):
        """Create a new user with security checks."""
        try:
            # Validate password
            is_valid, msg = self.validate_password_complexity(self.password)
            if not is_valid:
                return msg

            # Check if username/email exists
            query = "SELECT COUNT(*) FROM users WHERE username = %s OR email = %s"
            result = self.fetch_one(query, (self.username, self.email))
            if result['COUNT(*)'] > 0:
                return "Username or email already exists"

            # Hash password
            self.password_hash, self.salt = self.hash_password(self.password)

            # Insert user
            query = """
                INSERT INTO users 
                (username, email, password_hash, salt, first_name, last_name, phone, is_verified) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
            params = (
                self.username, self.email, self.password_hash, self.salt,
                self.first_name, self.last_name, self.phone, self.is_verified
            )
            if self.execute_query(query, params):
                self.user_id = self.cursor.lastrowid
                return None  # Success
            return "Failed to create user"

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return "An error occurred during registration"

    def verify_password(self, password):
        """Check password against stored hash."""
        if not self.password_hash:
            return False

        # Fetch hash if not set
        if not self.salt:
            query = "SELECT password_hash, salt FROM users WHERE user_id = %s"
            result = self.fetch_one(query, (self.user_id,))
            if not result:
                return False
            self.password_hash = result['password_hash']
            self.salt = result['salt']

        # Verify
        hashed = bcrypt.hashpw(password.encode('utf-8'), self.salt.encode('utf-8'))
        return hashed.decode('utf-8') == self.password_hash

    def login(self, credential, password, ip_address=None, user_agent=None):
        """Authenticate user with security checks."""
        try:
            # Fetch user data
            query = """
                SELECT user_id, username, email, password_hash, salt, 
                       failed_login_attempts, account_locked,
                       TIMESTAMPDIFF(MINUTE, created_at, NOW()) as lockout_time
                FROM users 
                WHERE username = %s OR email = %s
                """
            user_data = self.fetch_one(query, (credential, credential))

            if not user_data:
                return False, "Invalid username or email"

            # Check if account is locked
            if user_data['account_locked']:
                if user_data['lockout_time'] < self.LOCKOUT_DURATION:
                    return False, "Account locked. Please try again later."
                else:
                    # Unlock if lockout expired
                    self.execute_query(
                        "UPDATE users SET account_locked = FALSE, failed_login_attempts = 0 WHERE user_id = %s",
                        (user_data['user_id'],)
                    )

            # Verify password
            self.password_hash = user_data['password_hash']
            self.salt = user_data['salt']
            if not self.verify_password(password):
                # Increment failed attempts
                self.execute_query(
                    "UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE user_id = %s",
                    (user_data['user_id'],)
                )

                # Lock account if max attempts reached
                if user_data['failed_login_attempts'] + 1 >= self.MAX_LOGIN_ATTEMPTS:
                    self.execute_query(
                        "UPDATE users SET account_locked = TRUE WHERE user_id = %s",
                        (user_data['user_id'],)
                    )
                    return False, "Account locked due to too many failed attempts"

                return False, "Invalid password"

            # Login successful - reset attempts
            self.execute_query(
                "UPDATE users SET failed_login_attempts = 0 WHERE user_id = %s",
                (user_data['user_id'],)
            )

            # Set user attributes
            self.user_id = user_data['user_id']
            self.username = user_data['username']
            self.email = user_data['email']
            self.failed_login_attempts = 0
            self.account_locked = False

            return True, None

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, "An error occurred during login"