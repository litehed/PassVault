import psycopg2
from cryptography.fernet import Fernet

# Load your encryption key
with open("secret.key", "rb") as f:
    key = f.read()

cipher = Fernet(key)

# Database connection setup
cursor = None
conn = None

try:
    conn = psycopg2.connect(
        user="postgres",
        password="pEth4nGLe!",
        host="localhost",
        port="5432",
        database="thevault"
    )

    cursor = conn.cursor()
    select_query = "SELECT app_name, username, password FROM credentials;"
    cursor.execute(select_query)
    rows = cursor.fetchall()

    for row in rows:
        app_name, username, encrypted_pw = row
        decrypted_pw = cipher.decrypt(bytes(encrypted_pw)).decode()
        print(f"Service: {app_name}")
        print(f"Username: {username}")
        print(f"Password: {decrypted_pw}")
        print("-" * 30)

except (Exception, psycopg2.Error) as error:
    print("Error while fetching data:", error)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()