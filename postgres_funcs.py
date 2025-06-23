import psycopg2
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


SALT = b"\x00\xfa5+T>\xd39\x10R\x0f\xaaA\xc4[|"  # temp


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=300000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def save_credential(app_name: str, username: str, password_plain: str, db_pass: str) -> bool:
    conn = None
    cursor = None
    try:
        key = derive_key_from_password(db_pass, SALT)
        cipher = Fernet(key)

        conn = psycopg2.connect(
            user="postgres",
            password=db_pass,
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


def fetch_credentials(db_pass: str):
    conn = None
    cursor = None
    results = []
    try:
        key = derive_key_from_password(db_pass, SALT)
        cipher = Fernet(key)

        conn = psycopg2.connect(
            user="postgres",
            password=db_pass,
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
