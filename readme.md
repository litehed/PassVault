# PassVault

**PassVault** is a simple desktop password manager built with Python and PySide6, using PostgreSQL for data storage and Fernet encryption for secure credential handling.

---

## Features

* Add and view credentials for different apps/services
* Credentials are securely encrypted using Fernet before storage
* Clean and simple GUI with PySide6
* Data stored in a PostgreSQL database
* Passwords decrypted only when viewed

---

## Requirements

* Python 3.9+
* PostgreSQL

### Python Packages

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install psycopg2 cryptography python-dotenv PySide6
```

---

## Setup

1. **Clone this repository:**

```bash
git clone https://github.com/litehed/PassVault.git
```

2. **Create the database and table:**

Make sure your PostgreSQL database `thevault` exists. Then create the two following tables:

```sql
CREATE TABLE credentials (
    id SERIAL PRIMARY KEY,
    app_name TEXT NOT NULL,
    username TEXT NOT NULL,
    password BYTEA NOT NULL
);


CREATE TABLE config (
    key TEXT PRIMARY KEY,
    salt BYTEA NOT NULL
);
```

---

## Running the App

```bash
python main.py
```

---

## Project Structure

```
passvault/
├── main.py               # Main GUI app
├── login_dialog.py       # Used to check master password before entering the vault
├── vault_widget.py       # Popup for adding new credentials
├── postgres_funcs.py     # Database functions (save & fetch)
├── keygen.py             # Used to generate Fernet key file
└── requirements.txt      # Python dependencies
```

---

## To Do / Ideas

- [x]  Master password for opening the app
- [ ]  Export/import credentials
- [ ]  Search and filter
- [ ]  Auto-copy to clipboard
- [ ]  Category support
- [ ]  Link password to app for simple copy