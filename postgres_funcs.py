import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

with open("secret.key", "rb") as f:
    key = f.read()

cipher = Fernet(key)


def save_credential(app_name: str, username: str, password_plain: str) -> bool:
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host="localhost",
            port="5432",
            database="thevault"
        )
        cursor = conn.cursor()
        encrypted_pw = cipher.encrypt(password_plain.encode())
        insert_query = """
            INSERT INTO credentials (app_name, username, password)
            VALUES (%s, %s, %s);
        """
        cursor.execute(insert_query, (app_name, username, encrypted_pw))
        conn.commit()
        print(cursor.rowcount, " Inserted Successfully!")
        return True
    except Exception as error:
        print("Database insert failed:", error)
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def fetch_credentials():
    conn = None
    cursor = None
    results = []
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host="localhost",
            port="5432",
            database="thevault"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT app_name, username, password FROM credentials;")
        rows = cursor.fetchall()
        for service, user, encrypted_pw in rows:
            decrypted_pw = cipher.decrypt(bytes(encrypted_pw)).decode()
            results.append((service, user, decrypted_pw))
    except Exception as e:
        print("Error fetching credentials:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return results
