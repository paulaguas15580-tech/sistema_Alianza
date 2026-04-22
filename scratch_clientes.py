import sqlite3
conn = sqlite3.connect('Alianza_Backup_Local.db')
cursor = conn.cursor()
cursor.execute("SELECT numero_carpeta, valor_apertura FROM Clientes WHERE cedula = '1716827801'")
print("Clientes table:", cursor.fetchall())
conn.close()
