import psycopg2

def reset_database():
    print("Iniciando conexion a la base de datos para RESETEO a Produccion...")
    try:
        conn = psycopg2.connect(
            host="192.168.100.100",
            database="alianza_db",
            user="postgres",
            password="alianza2026",
            port="5432"
        )
        cur = conn.cursor()
        
        # Obtener todas las tablas del esquema public
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        
        tablas_todas = [row[0] for row in cur.fetchall()]
        tablas_a_limpiar = [t for t in tablas_todas if t.lower() != 'usuarios']
        
        print(f"Tablas a limpiar: {', '.join(tablas_a_limpiar)}")
        
        if tablas_a_limpiar:
            # Formatear la lista para el comando TRUNCATE
            tablas_str = ', '.join([f'"{t}"' for t in tablas_a_limpiar])
            
            # Ejecutar TRUNCATE con RESTART IDENTITY y CASCADE
            query = f"TRUNCATE {tablas_str} RESTART IDENTITY CASCADE;"
            print(f"Ejecutando: {query}")
            cur.execute(query)
            conn.commit()
            print("Limpieza completada con exito. Las tablas estan vacias y los contadores (IDs) reiniciados.")
        else:
            print("No se encontraron tablas operativas para limpiar.")
            
    except Exception as e:
        print("Error durante la limpieza:")
        print(repr(e))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    reset_database()
