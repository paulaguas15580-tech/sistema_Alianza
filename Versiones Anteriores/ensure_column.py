import sqlite3

try:
    conn = sqlite3.connect('Alianza_Backup_Local.db')
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(Clientes)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'producto' not in columns:
        print("Adding 'producto' column...")
        cursor.execute("ALTER TABLE Clientes ADD COLUMN producto TEXT")
        conn.commit()
        print("'producto' column added.")
    else:
        print("'producto' column already exists.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
