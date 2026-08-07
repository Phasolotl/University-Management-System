# migrate_passwords.py
import psycopg2
from werkzeug.security import generate_password_hash
from config import DB_CONFIG

def migrate_passwords():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Fetch all users
    cur.execute("SELECT user_id, password FROM users")
    users = cur.fetchall()

    for user_id, password in users:
        # If the password is already hashed (starts with 'pbkdf2:' or 'scrypt:'), skip
        if password.startswith(('pbkdf2:', 'scrypt:')):
            continue
        # Otherwise, hash it
        hashed = generate_password_hash(password)
        cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (hashed, user_id))
        print(f"Updated user {user_id}")

    conn.commit()
    cur.close()
    conn.close()
    print("Password migration complete.")

if __name__ == "__main__":
    migrate_passwords()