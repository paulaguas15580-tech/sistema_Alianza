from database import db_manager

def fix_schema():
    conn = db_manager.get_connection()
    cursor = db_manager.get_cursor(conn)
    
    missing_cols = {
        'estado_civil': 'TEXT',
        'cargas_familiares': 'INTEGER',
        'email': 'TEXT',
        'telefono': 'TEXT',
        'direccion': 'TEXT',
        'parroquia': 'TEXT',
        'tipo_vivienda': 'TEXT',
        'profesion': 'TEXT',
        'ingresos_mensuales': 'REAL',
        'referencia1': 'TEXT',
        'referencia2': 'TEXT',
        'apertura': 'TEXT',
        'numero_carpeta': 'TEXT',
        '"fecha nacimiento"': 'TEXT',
        'producto': 'TEXT',
        '"cartera castigada"': 'INTEGER DEFAULT 0',
        '"valor cartera"': 'REAL',
        '"demanda judicial"': 'INTEGER DEFAULT 0',
        '"valor demanda"': 'REAL',
        '"problemas justicia"': 'INTEGER DEFAULT 0',
        '"detalle justicia"': 'TEXT'
    }

    try:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'clientes'")
        existing_cols = [r[0] for r in cursor.fetchall()]
        
        for col, col_type in missing_cols.items():
            # information schema returns lower case without quotes
            col_check = col.replace('"', '').lower()
            if col_check not in existing_cols:
                print(f"Agregando {col}...")
                cursor.execute(f"ALTER TABLE Clientes ADD COLUMN {col} {col_type}")
        conn.commit()
        print("Schema fixed successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Error fixing schema: {e}")
    finally:
        db_manager.release_connection(conn)

if __name__ == '__main__':
    fix_schema()
