import hashlib
import datetime
import os
from db_manager import DatabaseManager
import psycopg2.extras
import sqlite3 # Mantenido solo para atrapar excepciones específicas si quedara alguna

DB_NAME = 'Alianza.db'

# =================================================================
# UTILIDADES
# =================================================================

def generar_hash(clave):
    return hashlib.sha256(clave.encode()).hexdigest()

def limpiar_moneda(valor_str):
    """Quita $ y comas para guardar en DB como número."""
    if not valor_str: return 0.0
    if isinstance(valor_str, (int, float)): return float(valor_str)
    limpio = str(valor_str).replace('$', '').replace(',', '').strip()
    try: return float(limpio)
    except: return 0.0

def formatear_float_str(valor):
    """Convierte float a string '1,200.00'."""
    try:
        return "{:,.2f}".format(float(valor))
    except: return ""

# Configuración PostgreSQL (Misma instancia que basededatos.py)
try:
    db_manager = DatabaseManager(
        host="localhost", 
        database="alianza_db",
        user="postgres",
        password="clave_segura"
    )
except:
    db_manager = None

def conectar_db():
    if not db_manager:
        raise ConnectionError("No hay conexión con el servidor de base de datos.")
    conn = db_manager.get_connection()
    return conn, db_manager.get_cursor(conn)

# Helpers delegados
def sql_type(t): return db_manager.sql_type(t)
def get_column_names(c, t): return db_manager.get_column_names(c, t)
def check_table_exists(c, t): return db_manager.check_table_exists(c, t)

# =================================================================
# MIGRACIONES Y TABLAS
# =================================================================

def crear_tablas():
    conn, cursor = conectar_db()
    try:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS Clientes (
                id {sql_type("SERIAL PRIMARY KEY")}, 
                cedula TEXT UNIQUE NOT NULL,  
                ruc TEXT,
                nombre TEXT NOT NULL,
                estado_civil TEXT,
                cargas_familiares INTEGER,
                email TEXT,
                telefono TEXT,
                direccion TEXT,
                parroquia TEXT,
                tipo_vivienda TEXT,
                profesion TEXT,
                ingresos_mensuales REAL,
                referencia1 TEXT,
                referencia2 TEXT,
                asesor TEXT,
                apertura TEXT,
                numero_carpeta TEXT,
                "fecha nacimiento" TEXT,
                producto TEXT,
                observaciones TEXT,
                "cartera castigada" INTEGER DEFAULT 0,
                "valor cartera" REAL,
                "demanda judicial" INTEGER DEFAULT 0,
                "valor demanda" REAL,
                "problemas justicia" INTEGER DEFAULT 0,
                "detalle justicia" TEXT
            )
        """)
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS Usuarios (
                id {sql_type("SERIAL PRIMARY KEY")},
                usuario TEXT UNIQUE NOT NULL,
                clave_hash TEXT NOT NULL, 
                nivel_acceso INTEGER NOT NULL
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM Usuarios")
        if cursor.fetchone()[0] == 0:
            hash_admin = generar_hash('cyberpol2022') 
            cursor.execute("INSERT INTO Usuarios (usuario, clave_hash, nivel_acceso) VALUES (%s, %s, %s)", ('Paul', hash_admin, 1))

        conn.commit()
    except Exception as e: print(f"Error DB: {e}")
    finally: db_manager.release_connection(conn)

def migrar_db():
    conn, cursor = conectar_db()
    try:
        # Verificar si existe la column_name de Clientes
        columnas = get_column_names(cursor, 'Clientes')
        
        # Lista de columnas a verificar/agregar en Clientes
        cols_to_add = [
            ('referencia_vivienda', 'TEXT'),
            ('situacion_financiera', 'TEXT'),
            ('terreno', 'INTEGER DEFAULT 0'),
            ('valor_terreno', 'REAL'),
            ('hipotecado', 'TEXT'),
            ('fuente_ingreso', 'TEXT'),
            ('ingresos_mensuales_2', 'REAL'),
            ('fuente_ingreso_2', 'TEXT'),
            ('casa_dep', 'INTEGER DEFAULT 0'),
            ('valor_casa_dep', 'REAL'),
            ('hipotecado_casa_dep', 'TEXT'),
            ('local', 'INTEGER DEFAULT 0'),
            ('valor_local', 'REAL'),
            ('hipotecado_local', 'TEXT'),
            ('score_buro', 'INTEGER'),
            ('egresos', 'REAL'),
            ('total_disponible', 'REAL'),
            ('valor_apertura', 'REAL')
        ]

        for col_name, col_type in cols_to_add:
            if col_name not in columnas:
                print(f"Migrando DB: Agregando columna '{col_name}' a Clientes...")
                cursor.execute(f"ALTER TABLE Clientes ADD COLUMN {col_name} {col_type}")
                conn.commit()

        # Migración Usuarios
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuarios'")
        cols_user = [row[0] for row in cursor.fetchall()]
        if 'estado' not in cols_user:
            print("Migrando DB: Agregando 'estado' a Usuarios...")
            cursor.execute("ALTER TABLE Usuarios ADD COLUMN estado INTEGER DEFAULT 1")
            conn.commit()
        if 'rol' not in cols_user:
            print("Migrando DB: Agregando 'rol' a Usuarios...")
            cursor.execute("ALTER TABLE Usuarios ADD COLUMN rol TEXT")
            cursor.execute("UPDATE Usuarios SET rol = 'Administrador' WHERE nivel_acceso = 1")
            cursor.execute("UPDATE Usuarios SET rol = 'Usuario' WHERE nivel_acceso = 2")
            conn.commit()

        # Tabla Auditoria
        if not check_table_exists(cursor, 'Auditoria'):
            print("Migrando DB: Creando tabla 'Auditoria'...")
            cursor.execute(f"""
                CREATE TABLE Auditoria (
                    id {sql_type("SERIAL PRIMARY KEY")},
                    id_usuario TEXT,
                    accion TEXT,
                    id_cliente TEXT,
                    detalles TEXT,
                    timestamp TEXT
                )
            """)
            conn.commit()

        # Tabla Documentos
        if not check_table_exists(cursor, 'Documentos'):
            print("Migrando DB: Creando tabla 'Documentos'...")
            cursor.execute(f"""
                CREATE TABLE Documentos (
                    id {sql_type("SERIAL PRIMARY KEY")},
                    cedula_cliente TEXT NOT NULL,
                    nombre_archivo TEXT NOT NULL,
                    tipo_documento TEXT,
                    ruta_archivo TEXT NOT NULL,
                    fecha_subida TEXT NOT NULL,
                    FOREIGN KEY (cedula_cliente) REFERENCES Clientes(cedula)
                )
            """)
            conn.commit()

        # Tabla Microcreditos
        if not check_table_exists(cursor, 'Microcreditos'):
            print("Migrando DB: Creando tabla 'Microcreditos'...")
            cursor.execute(f"""
                CREATE TABLE Microcreditos (
                    id {sql_type("SERIAL PRIMARY KEY")},
                    cedula_cliente TEXT NOT NULL,
                    ruc TEXT,
                    observaciones TEXT,
                    observaciones_info TEXT,
                    
                    ref1_relacion TEXT, ref1_tiempo_conocer TEXT, ref1_direccion TEXT, ref1_tipo_vivienda TEXT, ref1_cargas TEXT, ref1_patrimonio TEXT, ref1_responsable TEXT,
                    ref2_relacion TEXT, ref2_tiempo_conocer TEXT, ref2_direccion TEXT, ref2_tipo_vivienda TEXT, ref2_cargas TEXT, ref2_patrimonio TEXT, ref2_responsable TEXT,
                    
                    FOREIGN KEY (cedula_cliente) REFERENCES Clientes(cedula)
                )
            """)
            conn.commit()
        else:
            # Si ya existe, verificar columnas faltantes
            cols_micro = get_column_names(cursor, 'Microcreditos')
            
            micro_cols_to_add = [
                ('observaciones_info', 'TEXT'),
                ('ref1_fecha', 'TEXT'), ('ref1_hora', 'TEXT'), ('ref1_nombre', 'TEXT'), ('ref1_telefono', 'TEXT'),
                ('ref2_fecha', 'TEXT'), ('ref2_hora', 'TEXT'), ('ref2_nombre', 'TEXT'), ('ref2_telefono', 'TEXT'),
                ('status', 'TEXT'), ('sub_status', 'TEXT'),
                ('fecha_desembolsado', 'TEXT'), ('fecha_negado', 'TEXT'), ('fecha_desistimiento', 'TEXT'), ('fecha_comite', 'TEXT')
            ]
            
            for col_name, col_type in micro_cols_to_add:
                if col_name not in cols_micro:
                    print(f"Migrando DB: Agregando columna '{col_name}' a Microcreditos...")
                    cursor.execute(f"ALTER TABLE Microcreditos ADD COLUMN {col_name} {col_type}")
                    conn.commit()

        # Tabla Rehabilitacion
        if not check_table_exists(cursor, 'Rehabilitacion'):
            print("Migrando DB: Creando tabla 'Rehabilitacion'...")
            cursor.execute(f"""
                CREATE TABLE Rehabilitacion (
                    id {sql_type("SERIAL PRIMARY KEY")},
                    cedula_cliente TEXT UNIQUE NOT NULL,
                    fecha_inicio TEXT,
                    terminos TEXT,
                    resultado TEXT,
                    finalizado INTEGER DEFAULT 0,
                    FOREIGN KEY (cedula_cliente) REFERENCES Clientes(cedula)
                )
            """)
            conn.commit()

        # Tabla visitas_microcredito
        if not check_table_exists(cursor, 'visitas_microcredito'):
            print("Migrando DB: Creando tabla 'visitas_microcredito'...")
            cursor.execute(f"""
                CREATE TABLE visitas_microcredito (
                    id {sql_type("SERIAL PRIMARY KEY")},
                    cedula_cliente TEXT NOT NULL,
                    fecha TEXT,
                    observaciones TEXT,
                    FOREIGN KEY (cedula_cliente) REFERENCES Clientes(cedula)
                )
            """)
            conn.commit()

        # Migración Usuario Admin -> Paul
        cursor.execute("SELECT id FROM Usuarios WHERE usuario='admin'")
        admin_user = cursor.fetchone()
        if admin_user:
            print("Migrando usuario admin a Paul...")
            new_hash = generar_hash('cyberpol2022')
            cursor.execute("UPDATE Usuarios SET usuario=%s, clave_hash=%s WHERE id=%s", ('Paul', new_hash, admin_user[0]))
            conn.commit()
            
    except Exception as e: print(f"Error Migración: {e}")
    finally: db_manager.release_connection(conn)

def registrar_auditoria(usuario, accion, id_cliente=None, detalles=None):
    """Registra una acción en la tabla de Auditoria"""
    conn, cursor = conectar_db()
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO Auditoria (id_usuario, accion, id_cliente, detalles, timestamp) VALUES (%s,%s,%s,%s,%s)",
                       (usuario, accion, id_cliente, detalles, ts))
        conn.commit()
    except Exception as e: print(f"Error auditoría: {e}")
    finally: db_manager.release_connection(conn)

# Inicializar DB al importar
crear_tablas()
migrar_db()

# =================================================================
# CRUD CLIENTES
# =================================================================

def validar_datos(cedula, nombre, apertura, ingresos_str, val_cart_str, val_dem_str):
    if not nombre or not nombre.strip(): return "El Nombre es obligatorio."
    if cedula.strip() and (len(cedula.strip()) != 10 or not cedula.strip().isdigit()):
        return "La Cédula debe tener 10 dígitos numéricos."
    
    try:
        limpiar_moneda(ingresos_str)
        limpiar_moneda(val_cart_str)
        limpiar_moneda(val_dem_str)
    except: return "Revise los campos numéricos."

    if apertura and apertura.strip():
        try: datetime.datetime.strptime(apertura, "%d/%m/%Y")
        except ValueError: return "Fecha Apertura incorrecta (DD/MM/YYYY)."
    return True

def guardar_cliente_db(data, usuario="Sistema"):
    # data es un diccionario
    val = validar_datos(data.get('cedula',''), data.get('nombre',''), data.get('apertura',''), 
                        data.get('ingresos_mensuales',''), data.get('valor_cartera',''), data.get('valor_demanda',''))
    if val is not True: return False, val
    
    ingresos = limpiar_moneda(data.get('ingresos_mensuales', 0))
    ingresos_2 = limpiar_moneda(data.get('ingresos_mensuales_2', 0))
    egresos = limpiar_moneda(data.get('egresos', 0))
    valor_terreno = limpiar_moneda(data.get('valor_terreno', 0)) if data.get('terreno') else 0
    valor_casa = limpiar_moneda(data.get('valor_casa_dep', 0)) if data.get('casa_dep') else 0
    valor_local = limpiar_moneda(data.get('valor_local', 0)) if data.get('local') else 0
    val_cart = limpiar_moneda(data.get('valor_cartera', 0)) if data.get('cartera_castigada') else 0
    val_dem = limpiar_moneda(data.get('valor_demanda', 0)) if data.get('demanda_judicial') else 0
    total_disponible = ingresos + ingresos_2 - egresos

    score_buro = data.get('score_buro')
    if score_buro:
        try:
            score_buro = int(score_buro)
            if score_buro < 1 or score_buro > 999: return False, "Score Buró debe estar entre 1 y 999"
        except: return False, "Score Buró debe ser un número"

    conn, cursor = conectar_db()
    try:
        cursor.execute(f"""
            INSERT INTO Clientes (
                cedula, ruc, nombre, estado_civil, cargas_familiares, email, telefono, direccion, parroquia, 
                tipo_vivienda, referencia_vivienda, profesion, ingresos_mensuales, fuente_ingreso, terreno, valor_terreno, hipotecado, referencia1, referencia2, asesor, apertura, numero_carpeta, 
                "fecha nacimiento", producto, observaciones, 
                "cartera castigada", "valor cartera", "demanda judicial", "valor demanda", "problemas justicia", "detalle justicia",
                casa_dep, valor_casa_dep, hipotecado_casa_dep, local, valor_local, hipotecado_local,
                ingresos_mensuales_2, fuente_ingreso_2, score_buro, egresos, total_disponible, valor_apertura
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('cedula'), data.get('ruc'), data.get('nombre'), data.get('estado_civil'), data.get('cargas_familiares'), data.get('email'), data.get('telefono'), data.get('direccion'), data.get('parroquia'),
            data.get('tipo_vivienda'), data.get('referencia_vivienda'), data.get('profesion'), ingresos, data.get('fuente_ingreso'), data.get('terreno',0), valor_terreno, data.get('hipotecado'), data.get('referencia1'), data.get('referencia2'), data.get('asesor'), data.get('apertura'), data.get('numero_carpeta'),
            data.get('fecha_nacimiento'), data.get('producto'), data.get('observaciones'),
            data.get('cartera_castigada',0), val_cart, data.get('demanda_judicial',0), val_dem, data.get('problemas_justicia',0), data.get('detalle_justicia'),
            data.get('casa_dep',0), valor_casa, data.get('hipotecado_casa_dep'), data.get('local',0), valor_local, data.get('hipotecado_local'),
            ingresos_2, data.get('fuente_ingreso_2'), score_buro, egresos, total_disponible, limpiar_moneda(data.get('valor_apertura', 0))
        ))
        conn.commit()
        registrar_auditoria(usuario, "Guardar Cliente", id_cliente=data.get('cedula'), detalles=f"Cliente {data.get('nombre')} guardado via Flet.")
        return True, "Guardado exitosamente."
    except sqlite3.IntegrityError: return False, "Cédula ya existe."
    except Exception as e: return False, f"Error: {e}"
    finally: db_manager.release_connection(conn)

def actualizar_cliente_db(id_cliente, data, usuario="Sistema"):
    val = validar_datos(data.get('cedula',''), data.get('nombre',''), data.get('apertura',''), 
                        data.get('ingresos_mensuales',''), data.get('valor_cartera',''), data.get('valor_demanda',''))
    if val is not True: return False, val
    
    ingresos = limpiar_moneda(data.get('ingresos_mensuales', 0))
    ingresos_2 = limpiar_moneda(data.get('ingresos_mensuales_2', 0))
    egresos = limpiar_moneda(data.get('egresos', 0))
    valor_terreno = limpiar_moneda(data.get('valor_terreno', 0)) if data.get('terreno') else 0
    valor_casa = limpiar_moneda(data.get('valor_casa_dep', 0)) if data.get('casa_dep') else 0
    valor_local = limpiar_moneda(data.get('valor_local', 0)) if data.get('local') else 0
    val_cart = limpiar_moneda(data.get('valor_cartera', 0)) if data.get('cartera_castigada') else 0
    val_dem = limpiar_moneda(data.get('valor_demanda', 0)) if data.get('demanda_judicial') else 0
    total_disponible = ingresos + ingresos_2 - egresos

    score_buro = data.get('score_buro')
    if score_buro:
        try:
            score_buro = int(score_buro)
            if score_buro < 1 or score_buro > 999: return False, "Score Buró debe estar entre 1 y 999"
        except: return False, "Score Buró debe ser un número"

    conn, cursor = conectar_db()
    try:
        cursor.execute(f"""
            UPDATE Clientes SET 
            cedula=%s, ruc=%s, nombre=%s, estado_civil=%s, cargas_familiares=%s, email=%s, telefono=%s, direccion=%s, parroquia=%s, 
            tipo_vivienda=%s, referencia_vivienda=%s, profesion=%s, ingresos_mensuales=%s, fuente_ingreso=%s, terreno=%s, valor_terreno=%s, hipotecado=%s, referencia1=%s, referencia2=%s, asesor=%s, apertura=%s, numero_carpeta=%s, 
            "fecha nacimiento"=%s, producto=%s, observaciones=%s, 
            "cartera castigada"=%s, "valor cartera"=%s, "demanda judicial"=%s, "valor demanda"=%s, "problemas justicia"=%s, "detalle justicia"=%s,
            casa_dep=%s, valor_casa_dep=%s, hipotecado_casa_dep=%s, local=%s, valor_local=%s, hipotecado_local=%s,
            ingresos_mensuales_2=%s, fuente_ingreso_2=%s, score_buro=%s, egresos=%s, total_disponible=%s, valor_apertura=%s
            WHERE id=%s
        """, (
            data.get('cedula'), data.get('ruc'), data.get('nombre'), data.get('estado_civil'), data.get('cargas_familiares'), data.get('email'), data.get('telefono'), data.get('direccion'), data.get('parroquia'),
            data.get('tipo_vivienda'), data.get('referencia_vivienda'), data.get('profesion'), ingresos, data.get('fuente_ingreso'), data.get('terreno',0), valor_terreno, data.get('hipotecado'), data.get('referencia1'), data.get('referencia2'), data.get('asesor'), data.get('apertura'), data.get('numero_carpeta'),
            data.get('fecha_nacimiento'), data.get('producto'), data.get('observaciones'),
            data.get('cartera_castigada',0), val_cart, data.get('demanda_judicial',0), val_dem, data.get('problemas_justicia',0), data.get('detalle_justicia'),
            data.get('casa_dep',0), valor_casa, data.get('hipotecado_casa_dep'), data.get('local',0), valor_local, data.get('hipotecado_local'),
            ingresos_2, data.get('fuente_ingreso_2'), score_buro, egresos, total_disponible, limpiar_moneda(data.get('valor_apertura', 0)),
            id_cliente
        ))
        conn.commit()
        registrar_auditoria(usuario, "Actualizar Cliente", id_cliente=data.get('cedula'), detalles=f"Cliente {data.get('nombre')} actualizado via Flet.")
        return True, "Actualizado correctamente."
    except Exception as e: return False, f"Error: {e}"
    finally: db_manager.release_connection(conn)

def consultar_clientes_db():
    conn, cursor = conectar_db()
    try:
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM Clientes")
        return [dict(row) for row in cursor.fetchall()]
    finally: db_manager.release_connection(conn)

def buscar_clientes_db(termino):
    conn, cursor = conectar_db()
    t = '%' + termino + '%'
    cursor.row_factory = sqlite3.Row
    cursor.execute("SELECT * FROM Clientes WHERE nombre LIKE %s OR cedula LIKE %s OR ruc LIKE %s OR numero_carpeta LIKE %s", (t,t,t,t))
    return [dict(row) for row in cursor.fetchall()]

def eliminar_cliente_db(id_cliente):
    conn, cursor = conectar_db()
    cursor.execute("DELETE FROM Clientes WHERE id = %s", (id_cliente,))
    conn.commit()
    db_manager.release_connection(conn)
    return True, "Eliminado"

# =================================================================
# USUARIOS
# =================================================================

def verificar_credenciales(usuario, clave):
    conn, cursor = conectar_db()
    cursor.execute("SELECT clave_hash, nivel_acceso FROM Usuarios WHERE usuario = %s", (usuario,))
    res = cursor.fetchone()
    db_manager.release_connection(conn)
    if res and generar_hash(clave) == res[0]: return True, res[1]
    return False, 0

# =================================================================
# MICROCREDITOS
# =================================================================

def guardar_microcredito_db(data, usuario="Sistema"):
    # data: diccionario con claves de las columnas
    conn, cursor = conectar_db()
    try:
        if data.get('id'):
            cursor.execute(f"""
                UPDATE Microcreditos SET 
                observaciones=%s, 
                observaciones_info=%s,
                ref1_relacion=%s, ref1_tiempo_conocer=%s, ref1_direccion=%s, ref1_tipo_vivienda=%s, ref1_cargas=%s, ref1_patrimonio=%s, ref1_responsable=%s,
                ref2_relacion=%s, ref2_tiempo_conocer=%s, ref2_direccion=%s, ref2_tipo_vivienda=%s, ref2_cargas=%s, ref2_patrimonio=%s, ref2_responsable=%s,
                ref1_fecha=%s, ref1_hora=%s, ref1_nombre=%s, ref1_telefono=%s,
                ref2_fecha=%s, ref2_hora=%s, ref2_nombre=%s, ref2_telefono=%s,
                status=%s, sub_status=%s,
                fecha_desembolsado=%s, fecha_negado=%s, fecha_desistimiento=%s, fecha_comite=%s
                WHERE id=%s
            """, (
                data.get('observaciones'),
                data.get('observaciones_info'),
                data.get('ref1_relacion'), data.get('ref1_tiempo_conocer'), data.get('ref1_direccion'), data.get('ref1_tipo_vivienda'), data.get('ref1_cargas'), data.get('ref1_patrimonio'), data.get('ref1_responsable'),
                data.get('ref2_relacion'), data.get('ref2_tiempo_conocer'), data.get('ref2_direccion'), data.get('ref2_tipo_vivienda'), data.get('ref2_cargas'), data.get('ref2_patrimonio'), data.get('ref2_responsable'),
                data.get('ref1_fecha'), data.get('ref1_hora'), data.get('ref1_nombre'), data.get('ref1_telefono'),
                data.get('ref2_fecha'), data.get('ref2_hora'), data.get('ref2_nombre'), data.get('ref2_telefono'),
                data.get('status'), data.get('sub_status'),
                data.get('fecha_desembolsado'), data.get('fecha_negado'), data.get('fecha_desistimiento'), data.get('fecha_comite'),
                data.get('id')
            ))
            registrar_auditoria(usuario, "Actualizar Microcrédito", id_cliente=data.get('cedula_cliente'), detalles="Actualización de datos de verificación.")
        else:
            cursor.execute(f"""
                INSERT INTO Microcreditos (
                    cedula_cliente, ruc, observaciones, observaciones_info,
                    ref1_relacion, ref1_tiempo_conocer, ref1_direccion, ref1_tipo_vivienda, ref1_cargas, ref1_patrimonio, ref1_responsable,
                    ref2_relacion, ref2_tiempo_conocer, ref2_direccion, ref2_tipo_vivienda, ref2_cargas, ref2_patrimonio, ref2_responsable,
                    ref1_fecha, ref1_hora, ref1_nombre, ref1_telefono,
                    ref2_fecha, ref2_hora, ref2_nombre, ref2_telefono,
                    status, sub_status,
                    fecha_desembolsado, fecha_negado, fecha_desistimiento, fecha_comite
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                data.get('cedula_cliente'), data.get('ruc'), data.get('observaciones'), data.get('observaciones_info'),
                data.get('ref1_relacion'), data.get('ref1_tiempo_conocer'), data.get('ref1_direccion'), data.get('ref1_tipo_vivienda'), data.get('ref1_cargas'), data.get('ref1_patrimonio'), data.get('ref1_responsable'),
                data.get('ref2_relacion'), data.get('ref2_tiempo_conocer'), data.get('ref2_direccion'), data.get('ref2_tipo_vivienda'), data.get('ref2_cargas'), data.get('ref2_patrimonio'), data.get('ref2_responsable'),
                data.get('ref1_fecha'), data.get('ref1_hora'), data.get('ref1_nombre'), data.get('ref1_telefono'),
                data.get('ref2_fecha'), data.get('ref2_hora'), data.get('ref2_nombre'), data.get('ref2_telefono'),
                data.get('status'), data.get('sub_status'),
                data.get('fecha_desembolsado'), data.get('fecha_negado'), data.get('fecha_desistimiento'), data.get('fecha_comite')
            ))
            registrar_auditoria(usuario, "Guardar Microcrédito", id_cliente=data.get('cedula_cliente'), detalles="Ingreso de nuevos datos de verificación.")
        conn.commit()
        return True, "Guardado correctamente"
    except Exception as e: return False, f"Error: {e}"
    finally: db_manager.release_connection(conn)

def obtener_microcredito(cedula):
    conn, cursor = conectar_db()
    cursor.row_factory = sqlite3.Row
    cursor.execute("SELECT * FROM Microcreditos WHERE cedula_cliente = %s", (cedula,))
    res = cursor.fetchone()
    db_manager.release_connection(conn)
    return dict(res) if res else None

# =================================================================
# DOCUMENTOS
# =================================================================
def guardar_archivo_db(cedula, nombre_archivo, ruta_archivo, tipo_doc):
    conn, cursor = conectar_db()
    try:
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO Documentos (cedula_cliente, nombre_archivo, tipo_documento, ruta_archivo, fecha_subida) VALUES (%s,%s,%s,%s,%s)",
                       (cedula, nombre_archivo, tipo_doc, ruta_archivo, fecha))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally: db_manager.release_connection(conn)
