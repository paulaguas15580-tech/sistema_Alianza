import basededatos
import sys

# Force pure sqlite if needed, but basededatos should handle it.
# basededatos.db_manager.mode = "SQLITE" 

try:
    cedula = '1713573002'
    print(f"Testing query for cedula: {cedula}")
    
    conn, cursor = basededatos.conectar_db()
    
    # Check Clientes
    cursor.execute("SELECT * FROM Clientes WHERE cedula = %s", (cedula,))
    client = cursor.fetchone()
    print(f"Cliente found: {dict(client) if client else 'None'}")
    
    # Check Caja
    cursor.execute("SELECT * FROM Caja WHERE cedula = %s", (cedula,))
    caja_rows = cursor.fetchall()
    print(f"Caja rows found: {len(caja_rows)}")
    for row in caja_rows:
        # Convert to dict for printing if it's a Row object
        d = dict(row) if hasattr(row, 'keys') else row
        print(f"Row: {d}")
        if 'fecha_contrato' in d:
             print(f"  -> fecha_contrato: '{d['fecha_contrato']}'")
        else:
             print("  -> fecha_contrato column MISSING")

except Exception as e:
    print(f"Error: {e}")
