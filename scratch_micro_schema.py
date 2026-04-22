from database import db_manager
conn = db_manager.get_connection()
cursor = db_manager.get_cursor(conn)
cursor.execute("SELECT * FROM Microcreditos LIMIT 0")
colnames = [desc[0] for desc in cursor.description]
print("Microcreditos columns:", colnames)
db_manager.release_connection(conn)
