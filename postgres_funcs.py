import psycopg2
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import secrets


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=300000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def get_or_create_salt(db_pass: str) -> bytes:
    try:
        with psycopg2.connect(
            user="postgres",
            password=db_pass,
            host="localhost",
            port="5432",
            database="thevault"
        ) as conn, conn.cursor() as cursor:
                cursor.execute(
                    "SELECT salt FROM config WHERE key = %s", ('salt',))
                result = cursor.fetchone()

                if result:
                    salt_value = result[0]
                    return bytes(salt_value)
                else:
                    new_salt = secrets.token_bytes(16)
                    cursor.execute(
                        "INSERT INTO config (key, salt) VALUES (%s, %s)",
                        ('salt', new_salt)
                    )
                    conn.commit()
                    print("Generated and stored new salt")
                    return new_salt

    except psycopg2.Error as e:
        print(f"Database error while handling salt: {e}")
        raise


def save_credential(app_name: str, username: str, password_plain: str, db_pass: str) -> bool:
    try:
        key = derive_key_from_password(db_pass, get_or_create_salt(db_pass))
        cipher = Fernet(key)

        with psycopg2.connect(
            user="postgres",
            password=db_pass,
            host="localhost",
            port="5432",
            database="thevault"
        ) as conn, conn.cursor() as cursor:
                encrypted_pw = cipher.encrypt(password_plain.encode())
                insert_query = """
                    INSERT INTO credentials (app_name, username, password)
                    VALUES (%s, %s, %s);
                """
                cursor.execute(
                    insert_query, (app_name, username, encrypted_pw))
                conn.commit()
                print(cursor.rowcount, " Inserted Successfully!")
                return True
    except Exception as error:
        print("Database insert failed:", error)
        return False


def fetch_credentials(db_pass: str) -> list:
    results = []
    try:
        key = derive_key_from_password(db_pass, get_or_create_salt(db_pass))
        cipher = Fernet(key)

        with psycopg2.connect(
            user="postgres",
            password=db_pass,
            host="localhost",
            port="5432",
            database="thevault"
        ) as conn, conn.cursor() as cursor:
                cursor.execute("SELECT app_name, username, password FROM credentials;")
                rows = cursor.fetchall()
                for service, user, encrypted_pw in rows:
                    decrypted_pw = cipher.decrypt(bytes(encrypted_pw)).decode()
                    results.append((service, user, decrypted_pw))
    except Exception as e:
        print("Error fetching credentials:", e)
    
    return results
