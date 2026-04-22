from database import db_manager
conn = db_manager.get_connection()
cursor = db_manager.get_cursor(conn)
cursor.execute("SELECT numero_carpeta, valor_apertura FROM Clientes WHERE cedula = '1716827801'")
print("Clientes table (Postgres):", cursor.fetchall())
db_manager.release_connection(conn)
