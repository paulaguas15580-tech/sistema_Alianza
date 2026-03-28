
import sqlite3

db_path = "Alianza_Backup_Local.db"
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables in {db_path}:")
    for t in tables:
        print(t[0])
    conn.close()
except Exception as e:
    print(f"Error: {e}")
