import sqlite3
import os

try:
    conn = sqlite3.connect('Alianza.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Clientes)")
    columns = [row[1] for row in cursor.fetchall()]
    print("Columns in Clientes:", columns)
    
    required = ['score_buro', 'ingresos_mensuales_2', 'egresos', 'total_disponible']
    missing = [c for c in required if c not in columns]
    
    if missing:
        print("MISSING COLUMNS:", missing)
    else:
        print("All required columns exist.")
        
    conn.close()
except Exception as e:
    print(e)
