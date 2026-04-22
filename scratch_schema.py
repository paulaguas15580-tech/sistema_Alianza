from database import db_manager
conn = db_manager.get_connection()
cursor = db_manager.get_cursor(conn)
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'clientes'")
print([r[0] for r in cursor.fetchall()])
db_manager.release_connection(conn)
