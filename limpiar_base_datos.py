import sqlite3
import os

def limpiar_todo():
    # Confirmación de seguridad
    confirmacion = input("PELIGRO! Esto borrara TODOS los clientes y datos. Estas seguro? (escribe 'SI'): ")
    if confirmacion != "SI":
        print("Operación cancelada.")
        return

    # Se busca la base de datos principal o la de respaldo local que usa el sistema
    # Prioridad: Alianza_Backup_Local.db (donde estan los datos reales segun analisis)
    db_name = "Alianza_Backup_Local.db"
    
    if not os.path.exists(db_name) and os.path.exists("Alianza.db"):
        db_name = "Alianza.db"
        print(f"[INFO] Usando '{db_name}' (Backup local no encontrado).")
        print(f"ℹ️ Usando '{db_name}' (Base de datos activa encontrada).")
    elif not os.path.exists(db_name):
        print("No se encontró la base de datos.")
        return

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # 1. Lista de tablas a vaciar (Ajustar según tus tablas reales)
        tablas = [
            "Clientes", 
            "Microcreditos", 
            "Intermediacion_Detalles", 
            "Caja",
            "Pagos",
            "sqlite_sequence" # IMPORTANTE: Esto reinicia los contadores de ID a 1
        ]
        
        print(f"Iniciando limpieza en {db_name}...")
        
        for tabla in tablas:
            try:
                cursor.execute(f"DELETE FROM {tabla}")
                print(f"[OK] Tabla '{tabla}' vaciada.")
            except sqlite3.OperationalError:
                print(f"[INFO] La tabla '{tabla}' no existe o ya estaba vacía.")
        
        conn.commit()
        conn.close()
        print("\n[FIN] LIMPIEZA COMPLETADA! La base de datos esta como nueva.")
        
    except Exception as e:
        print(f"Error durante la limpieza: {e}")

if __name__ == "__main__":
    limpiar_todo()
