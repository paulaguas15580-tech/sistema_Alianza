
import sqlite3

db_path = "Alianza_Backup_Local.db"
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(PagosBuro)")
    columns = cursor.fetchall()
    print(f"Columns in 'PagosBuro' table:")
    for col in columns:
        print(col)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
