# database.py
"""
Database Connection and Operations Layer
Handles all PostgreSQL operations
"""
import datetime

import psycopg2
from psycopg2 import sql, Error
from config import DB_CONFIG, ROLE_STUDENT, ROLE_LECTURER
import logging
from werkzeug.security import generate_password_hash, check_password_hash

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection wrapper"""

    _connection = None

    @staticmethod
    def connect():
        """Establish database connection"""
        try:
            if DatabaseConnection._connection is None:
                DatabaseConnection._connection = psycopg2.connect(**DB_CONFIG)
                logger.info("Database connection established")
            return DatabaseConnection._connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise Exception(f"Failed to connect to database: {e}")

    @staticmethod
    def disconnect():
        """Close database connection"""
        if DatabaseConnection._connection:
            DatabaseConnection._connection.close()
            DatabaseConnection._connection = None
            logger.info("Database connection closed")

    @staticmethod
    def execute_query(query, params=None):
        """
        Execute SELECT query
        Returns: List of tuples (rows)
        """
        try:
            conn = DatabaseConnection.connect()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            logger.error(f"Query execution error: {e}")
            raise Exception(f"Database query failed: {e}")

    @staticmethod
    def execute_update(query, params=None):
        """
        Execute INSERT, UPDATE, DELETE query
        Returns: Number of affected rows
        """
        try:
            conn = DatabaseConnection.connect()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            logger.info(f"Query executed: {rows_affected} rows affected")
            return rows_affected
        except Error as e:
            if 'conn' in locals() and conn:
                conn.rollback()
            logger.error(f"Update execution error: {e}")
            raise Exception(f"Database update failed: {e}")

    @staticmethod
    def execute_fetchone(query, params=None):
        """
        Execute query and fetch single row
        Returns: Single tuple or None
        """
        try:
            conn = DatabaseConnection.connect()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            logger.error(f"Fetchone error: {e}")
            raise Exception(f"Database query failed: {e}")


class UserOperations:
    """User/Login related database operations"""

    @staticmethod
    def validate_login(username, password):
        """
        Validate user login credentials
        Returns: (True, user_data) or (False, None)
        """
        try:
            query = """
                    SELECT u.user_id, u.username, u.email, r.role_name, u.password
                    FROM users u
                             JOIN roles r ON u.role_id = r.role_id
                    WHERE u.username = %s \
                    """
            result = DatabaseConnection.execute_fetchone(query, (username,))
            if result:
                stored_hash = result[4]  # password column is index 4
                if check_password_hash(stored_hash, password):
                    return True, {
                        'user_id': result[0],
                        'username': result[1],
                        'email': result[2],
                        'role': result[3]
                    }
                return False, None

        except Exception as e:
            logger.error(f"Login validation error: {e}")
            raise Exception(f"Could not verify your login right now: {e}")

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Change user password"""
        try:
            # Verify old password
            query = "SELECT password FROM users WHERE user_id = %s"
            res = DatabaseConnection.execute_fetchone(query, (user_id,))
            if not res or not check_password_hash(res[0], old_password):
                return False, "Old password is incorrect"

            # Update with new hashed password
            new_hashed = generate_password_hash(new_password)
            update_query = "UPDATE users SET password = %s WHERE user_id = %s"
            DatabaseConnection.execute_update(update_query, (new_hashed, user_id))
        except Exception as e:
            logger.error(f"Password change error: {e}")
            return False, "Failed to change password"

    @staticmethod
    def get_user_by_id(user_id):
        """Get user information"""
        try:
            query = "SELECT user_id, username, email, role_id FROM users WHERE user_id = %s"
            return DatabaseConnection.execute_fetchone(query, (user_id,))
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None

    @staticmethod
    def get_role_id(role_name):
        """Get role id by role name"""
        query = "SELECT role_id FROM roles WHERE role_name = %s"
        return DatabaseConnection.execute_fetchone(query, (role_name,))

    @staticmethod
    def is_username_taken(username):
        """Check if username already exists"""
        query = "SELECT 1 FROM users WHERE username = %s"
        return DatabaseConnection.execute_fetchone(query, (username,)) is not None

    @staticmethod
    def is_email_taken(email):
        """Check if email already exists"""
        query = "SELECT 1 FROM users WHERE email = %s"
        return DatabaseConnection.execute_fetchone(query, (email,)) is not None

    @staticmethod
    def register_account(username, email, password, role_name):
        """Register a new student or lecturer account"""
        try:
            if role_name not in (ROLE_STUDENT, ROLE_LECTURER):
                return False, "Only student or lecturer accounts can be registered here."

            if UserOperations.is_username_taken(username):
                return False, "That username is already taken."

            if UserOperations.is_email_taken(email):
                return False, "That email is already in use."

            role_row = UserOperations.get_role_id(role_name)
            if not role_row:
                return False, "The selected role is not available."

            query = """
                INSERT INTO users (username, email, password, role_id)
                VALUES (%s, %s, %s, %s)
                RETURNING user_id
            """
            conn = DatabaseConnection.connect()
            cursor = conn.cursor()
            try:
                hashed_pw = generate_password_hash(password)
                cursor.execute(query, (username, email, hashed_pw, role_row[0]))
                user_id = cursor.fetchone()[0]
                conn.commit()
                logger.info("Account registered: %s", user_id)

                # Get default department (e.g., the first one)
                dept_query = "SELECT department_id FROM departments ORDER BY department_id LIMIT 1"
                cursor.execute(dept_query)
                dept_row = cursor.fetchone()
                if not dept_row:
                    conn.rollback()
                    return False, "No departments exist. Please contact admin."

                department_id = dept_row[0]
                today = datetime.date.today().isoformat()

                if role_name == ROLE_STUDENT:
                    # Insert into students
                    insert_student = """
                                     INSERT INTO students (user_id, department_id, first_name, last_name, enrollment_date)
                                     VALUES (%s, %s, %s, %s, %s) \
                                     """
                    cursor.execute(insert_student, (user_id, department_id, "New", "Student", today))
                elif role_name == ROLE_LECTURER:
                    # Insert into lecturers
                    insert_lecturer = """
                                      INSERT INTO lecturers (user_id, department_id, first_name, last_name, hire_date)
                                      VALUES (%s, %s, %s, %s, %s) \
                                      """
                    cursor.execute(insert_lecturer, (user_id, department_id, "New", "Lecturer", today))
                conn.commit()
                return True, user_id
            except Error as e:
                conn.rollback()
                logger.error(f"Account registration error: {e}")
                return False, f"Could not create account: {e}"
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"Registration helper error: {e}")
            return False, str(e)


# Connection pooling helper
def get_connection():
    """Get active database connection"""
    return DatabaseConnection.connect()


def close_connection():
    """Close database connection"""
    DatabaseConnection.disconnect()