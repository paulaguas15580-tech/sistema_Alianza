import sqlite3
try:
    conn = sqlite3.connect('Alianza_Backup_Local.db')
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE Clientes RENAME COLUMN nombre TO nombres")
    conn.commit()
    print("Renamed nombre to nombres successfully in SQLite.")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
