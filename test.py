import psycopg2
from cryptography.fernet import Fernet


with open("secret.key", "rb") as f:
    key = f.read()

cipher = Fernet(key)


conn = None
cursor = None

try:
    conn = psycopg2.connect(user="postgres", password="pEth4nGLe!",
                            host="localhost", port="5432", database="thevault")
    cursor = conn.cursor()
    insert_query = """INSERT INTO credentials (app_name, username, password) VALUES (%s, %s, %s)"""

    app_name = "GitHub"
    username = "ethan.leitner"
    password_plain = "supersecure123"

    password = cipher.encrypt(password_plain.encode())

    # Tuple of values to insert
    record = (app_name, username, password)

    # Execute and commit
    cursor.execute(insert_query, record)
    conn.commit()
    print("Password inserted successfully!")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL:", error)

finally:
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()
