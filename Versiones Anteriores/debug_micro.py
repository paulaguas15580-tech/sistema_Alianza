import sqlite3
import pandas as pd
from db_manager import DatabaseManager

# Helper to connect (copied from basededatos_v2.2.py logic roughly)
def get_data():
    conn = sqlite3.connect('Alianza_Backup_Local.db')
    cursor = conn.cursor()
    
    print("--- TABLES ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print([t[0] for t in tables])

    print("\n--- MICROCREDITOS SCHEMA ---")
    cursor.execute("PRAGMA table_info(Microcreditos)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)

    print("\n--- MICROCREDITOS DATA (First 10) ---")
    cursor.execute("SELECT id, cedula_cliente, status, sub_status, monto_aprobado FROM Microcreditos")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
        
    conn.close()

if __name__ == "__main__":
    get_data()
