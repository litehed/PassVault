import os
import bcrypt

MASTER_HASH_FILE = "master.hash"


def create_password(master_password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(master_password.encode(), salt)
    with open(MASTER_HASH_FILE, "wb") as f:
        f.write(hashed)


def verify_password(input_password: str) -> bool:
    if not os.path.exists(MASTER_HASH_FILE):
        return False
    with open(MASTER_HASH_FILE, "rb") as f:
        stored_hash = f.read()
    return bcrypt.checkpw(input_password.encode(), stored_hash)
