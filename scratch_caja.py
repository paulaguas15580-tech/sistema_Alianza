import sqlite3
conn = sqlite3.connect('Alianza_Backup_Local.db')
cursor = conn.cursor()
cursor.execute("SELECT valor_apertura, numero_apertura FROM Caja WHERE cedula = '1716827801'")
print("Caja table:", cursor.fetchall())
conn.close()
