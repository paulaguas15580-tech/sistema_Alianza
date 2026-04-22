from database import db_manager
conn = db_manager.get_connection()
cursor = db_manager.get_cursor(conn)
cursor.execute("SELECT apertura, numero_carpeta FROM Clientes WHERE cedula = '1716827801'")
print("Clientes table (Postgres) apertura/carpeta:", cursor.fetchall())
db_manager.release_connection(conn)
