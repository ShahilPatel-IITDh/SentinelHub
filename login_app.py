import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# Function to show data
def view_data():
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    print("\n📊 Database Data:")
    for row in rows:
        print(row)


# Login function
def login():
    username = input("Enter username: ")
    password = input("Enter password: ")

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()

    if user:
        print("✅ Login Successful")
        view_data()
    else:
        print("❌ Invalid Login")
        print("🚫 Access Denied")


# Run program
login()

conn.close()
