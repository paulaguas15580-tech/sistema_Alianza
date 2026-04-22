from database import db_manager
conn = db_manager.get_connection()
cursor = db_manager.get_cursor(conn)
try:
    cursor.execute("ALTER TABLE Clientes ALTER COLUMN fecha_registro TYPE TEXT")
    conn.commit()
    print("Column fecha_registro altered to TEXT successfully")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
db_manager.release_connection(conn)
