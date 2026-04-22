import sqlite3
conn = sqlite3.connect('Alianza_Backup_Local.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(Clientes)")
cols = [r[1] for r in cursor.fetchall()]
print("Columns in SQLite Clientes:", cols)
conn.close()
