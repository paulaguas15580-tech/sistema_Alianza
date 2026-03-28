
import sqlite3

db_path = "Alianza_Backup_Local.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

columns_to_add = [
    ("hora", "TEXT"),
    ("pago_efectivo", "REAL DEFAULT 0"),
    ("pago_transferencia", "REAL DEFAULT 0"),
    ("pago_tarjeta", "REAL DEFAULT 0"),
    ("concepto", "TEXT") # The code also uses 'concepto'
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE PagosBuro ADD COLUMN {col_name} {col_type}")
        print(f"Added column: {col_name}")
    except sqlite3.OperationalError as e:
        print(f"Column {col_name} already exists or error: {e}")

conn.commit()
conn.close()
print("PagosBuro repair complete.")
