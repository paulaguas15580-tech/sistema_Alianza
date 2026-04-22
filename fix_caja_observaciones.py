import psycopg2
from database import db_manager

def run_migration():
    conn = db_manager.get_connection()
    cursor = db_manager.get_cursor(conn)
    
    try:
        cursor.execute("ALTER TABLE Caja ADD COLUMN observaciones TEXT")
        print("Agregada columna observaciones a Caja.")
    except Exception as e:
        print(f"Error o ya existe: {e}")
        conn.rollback()

    try:
        cursor.execute("ALTER TABLE Caja ADD COLUMN estado_impreso TEXT")
        print("Agregada columna estado_impreso a Caja.")
    except Exception as e:
        print(f"Error o ya existe: {e}")
        conn.rollback()

    conn.commit()
    db_manager.release_connection(conn)

if __name__ == '__main__':
    run_migration()
