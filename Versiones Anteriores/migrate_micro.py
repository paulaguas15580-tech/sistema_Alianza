
import sqlite3
import os

DB_NAME = "Alianza.db"

def add_columns():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cols = [
        ("fecha_desembolso_real", "TEXT"),
        ("monto_aprobado", "REAL"),
        ("tasa_interes", "REAL"),
        ("plazo_meses", "INTEGER"),
        ("valor_cuota", "REAL"),
        ("dia_pago", "INTEGER")
    ]
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Microcreditos'")
        if not cursor.fetchone():
            print("Table Microcreditos does not exist yet. Please create it first or run the app.")
            return

        cursor.execute("PRAGMA table_info(Microcreditos)")
        existing_cols = [row[1] for row in cursor.fetchall()]
        
        for col_name, col_type in cols:
            if col_name not in existing_cols:
                print(f"Adding column {col_name}...")
                cursor.execute(f"ALTER TABLE Microcreditos ADD COLUMN {col_name} {col_type}")
            else:
                print(f"Column {col_name} already exists.")
                
        conn.commit()
        print("Migration complete.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if os.path.exists(DB_NAME):
        add_columns()
    else:
        print(f"DB {DB_NAME} not found.")
