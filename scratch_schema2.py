from database import db_manager
conn = db_manager.get_connection()
cursor = db_manager.get_cursor(conn)
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'clientes'")
for r in cursor.fetchall():
    print(r)
db_manager.release_connection(conn)
