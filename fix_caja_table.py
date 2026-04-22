from database import db_manager, crear_tablas, migrar_db

def fix_caja():
    conn = db_manager.get_connection()
    cursor = db_manager.get_cursor(conn)
    try:
        # Check if the table exists and if it has cedula_cliente instead of cedula
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'caja'")
        cols = [r[0] for r in cursor.fetchall()]
        
        if 'cedula_cliente' in cols and 'cedula' not in cols:
            print("Renaming legacy Caja table...")
            cursor.execute("ALTER TABLE Caja RENAME TO Caja_legacy")
            conn.commit()
            print("Renamed to Caja_legacy successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        db_manager.release_connection(conn)

    print("Re-running creating tables to recreate Caja...")
    crear_tablas()
    migrar_db()
    print("Done!")

if __name__ == '__main__':
    fix_caja()
