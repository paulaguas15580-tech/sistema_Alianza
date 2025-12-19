import sqlite3
import hashlib
import datetime
import os

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

def conectar_db():
    conn = sqlite3.connect(DB_NAME)
    return conn, conn.cursor()

# =================================================================
# MIGRACIONES Y TABLAS
# =================================================================

def crear_tablas():
    conn, cursor = conectar_db()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
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
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                clave_hash TEXT NOT NULL, 
                nivel_acceso INTEGER NOT NULL
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM Usuarios")
        if cursor.fetchone()[0] == 0:
            hash_admin = generar_hash('cyberpol2022') 
            cursor.execute("INSERT INTO Usuarios (usuario, clave_hash, nivel_acceso) VALUES (?, ?, ?)", ('Paul', hash_admin, 1))

        conn.commit()
    except Exception as e: print(f"Error DB: {e}")
    finally: conn.close()

def migrar_db():
    conn, cursor = conectar_db()
    try:
        cursor.execute("PRAGMA table_info(Clientes)")
        columnas = [info[1] for info in cursor.fetchall()]
        
        # Lista de columnas a verificar/agregar
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
                print(f"Migrando DB: Agregando columna '{col_name}'...")
                cursor.execute(f"ALTER TABLE Clientes ADD COLUMN {col_name} {col_type}")
                conn.commit()

        # Tabla Documentos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Documentos'")
        if not cursor.fetchone():
            print("Migrando DB: Creando tabla 'Documentos'...")
            cursor.execute("""
                CREATE TABLE Documentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Microcreditos'")
        if not cursor.fetchone():
            print("Migrando DB: Creando tabla 'Microcreditos'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Microcreditos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

        # Migración para observaciones_info si no existe
        cursor.execute("PRAGMA table_info(Microcreditos)")
        cols_micro = [info[1] for info in cursor.fetchall()]
        if 'observaciones_info' not in cols_micro:
            print("Migrando DB: Agregando columna 'observaciones_info' a Microcreditos...")
            cursor.execute("ALTER TABLE Microcreditos ADD COLUMN observaciones_info TEXT")
            conn.commit()
            
    except Exception as e: print(f"Error Migración: {e}")
    finally: conn.close()

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

def guardar_cliente_db(data):
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
        cursor.execute("""
            INSERT INTO Clientes (
                cedula, ruc, nombre, estado_civil, cargas_familiares, email, telefono, direccion, parroquia, 
                tipo_vivienda, referencia_vivienda, profesion, ingresos_mensuales, fuente_ingreso, terreno, valor_terreno, hipotecado, referencia1, referencia2, asesor, apertura, numero_carpeta, 
                "fecha nacimiento", producto, observaciones, 
                "cartera castigada", "valor cartera", "demanda judicial", "valor demanda", "problemas justicia", "detalle justicia",
                casa_dep, valor_casa_dep, hipotecado_casa_dep, local, valor_local, hipotecado_local,
                ingresos_mensuales_2, fuente_ingreso_2, score_buro, egresos, total_disponible, valor_apertura
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('cedula'), data.get('ruc'), data.get('nombre'), data.get('estado_civil'), data.get('cargas_familiares'), data.get('email'), data.get('telefono'), data.get('direccion'), data.get('parroquia'),
            data.get('tipo_vivienda'), data.get('referencia_vivienda'), data.get('profesion'), ingresos, data.get('fuente_ingreso'), data.get('terreno',0), valor_terreno, data.get('hipotecado'), data.get('referencia1'), data.get('referencia2'), data.get('asesor'), data.get('apertura'), data.get('numero_carpeta'),
            data.get('fecha_nacimiento'), data.get('producto'), data.get('observaciones'),
            data.get('cartera_castigada',0), val_cart, data.get('demanda_judicial',0), val_dem, data.get('problemas_justicia',0), data.get('detalle_justicia'),
            data.get('casa_dep',0), valor_casa, data.get('hipotecado_casa_dep'), data.get('local',0), valor_local, data.get('hipotecado_local'),
            ingresos_2, data.get('fuente_ingreso_2'), score_buro, egresos, total_disponible, limpiar_moneda(data.get('valor_apertura', 0))
        ))
        conn.commit()
        return True, "Guardado exitosamente."
    except sqlite3.IntegrityError: return False, "Cédula ya existe."
    except Exception as e: return False, f"Error: {e}"
    finally: conn.close()

def actualizar_cliente_db(id_cliente, data):
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
        cursor.execute("""
            UPDATE Clientes SET 
            cedula=?, ruc=?, nombre=?, estado_civil=?, cargas_familiares=?, email=?, telefono=?, direccion=?, parroquia=?, 
            tipo_vivienda=?, referencia_vivienda=?, profesion=?, ingresos_mensuales=?, fuente_ingreso=?, terreno=?, valor_terreno=?, hipotecado=?, referencia1=?, referencia2=?, asesor=?, apertura=?, numero_carpeta=?, 
            "fecha nacimiento"=?, producto=?, observaciones=?, 
            "cartera castigada"=?, "valor cartera"=?, "demanda judicial"=?, "valor demanda"=?, "problemas justicia"=?, "detalle justicia"=?,
            casa_dep=?, valor_casa_dep=?, hipotecado_casa_dep=?, local=?, valor_local=?, hipotecado_local=?,
            ingresos_mensuales_2=?, fuente_ingreso_2=?, score_buro=?, egresos=?, total_disponible=?, valor_apertura=?
            WHERE id=?
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
        return True, "Actualizado correctamente."
    except Exception as e: return False, f"Error: {e}"
    finally: conn.close()

def consultar_clientes_db():
    conn, cursor = conectar_db()
    try:
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM Clientes")
        return [dict(row) for row in cursor.fetchall()]
    finally: conn.close()

def buscar_clientes_db(termino):
    conn, cursor = conectar_db()
    t = '%' + termino + '%'
    cursor.row_factory = sqlite3.Row
    cursor.execute("SELECT * FROM Clientes WHERE nombre LIKE ? OR cedula LIKE ? OR ruc LIKE ? OR numero_carpeta LIKE ?", (t,t,t,t))
    return [dict(row) for row in cursor.fetchall()]

def eliminar_cliente_db(id_cliente):
    conn, cursor = conectar_db()
    cursor.execute("DELETE FROM Clientes WHERE id = ?", (id_cliente,))
    conn.commit()
    conn.close()
    return True, "Eliminado"

# =================================================================
# USUARIOS
# =================================================================

def verificar_credenciales(usuario, clave):
    conn, cursor = conectar_db()
    cursor.execute("SELECT clave_hash, nivel_acceso FROM Usuarios WHERE usuario = ?", (usuario,))
    res = cursor.fetchone()
    conn.close()
    if res and generar_hash(clave) == res[0]: return True, res[1]
    return False, 0

# =================================================================
# MICROCREDITOS
# =================================================================

def guardar_microcredito_db(data):
    # data: diccionario con claves de las columnas
    conn, cursor = conectar_db()
    try:
        if data.get('id'):
            cursor.execute("""
                UPDATE Microcreditos SET 
                observaciones=?, 
                observaciones_info=?,
                ref1_relacion=?, ref1_tiempo_conocer=?, ref1_direccion=?, ref1_tipo_vivienda=?, ref1_cargas=?, ref1_patrimonio=?, ref1_responsable=?,
                ref2_relacion=?, ref2_tiempo_conocer=?, ref2_direccion=?, ref2_tipo_vivienda=?, ref2_cargas=?, ref2_patrimonio=?, ref2_responsable=?
                WHERE id=?
            """, (
                data.get('observaciones'),
                data.get('observaciones_info'),
                data.get('ref1_relacion'), data.get('ref1_tiempo_conocer'), data.get('ref1_direccion'), data.get('ref1_tipo_vivienda'), data.get('ref1_cargas'), data.get('ref1_patrimonio'), data.get('ref1_responsable'),
                data.get('ref2_relacion'), data.get('ref2_tiempo_conocer'), data.get('ref2_direccion'), data.get('ref2_tipo_vivienda'), data.get('ref2_cargas'), data.get('ref2_patrimonio'), data.get('ref2_responsable'),
                data.get('id')
            ))
        else:
            cursor.execute("""
                INSERT INTO Microcreditos (
                    cedula_cliente, ruc, observaciones, observaciones_info,
                    ref1_relacion, ref1_tiempo_conocer, ref1_direccion, ref1_tipo_vivienda, ref1_cargas, ref1_patrimonio, ref1_responsable,
                    ref2_relacion, ref2_tiempo_conocer, ref2_direccion, ref2_tipo_vivienda, ref2_cargas, ref2_patrimonio, ref2_responsable
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                data.get('cedula_cliente'), data.get('ruc'), data.get('observaciones'), data.get('observaciones_info'),
                data.get('ref1_relacion'), data.get('ref1_tiempo_conocer'), data.get('ref1_direccion'), data.get('ref1_tipo_vivienda'), data.get('ref1_cargas'), data.get('ref1_patrimonio'), data.get('ref1_responsable'),
                data.get('ref2_relacion'), data.get('ref2_tiempo_conocer'), data.get('ref2_direccion'), data.get('ref2_tipo_vivienda'), data.get('ref2_cargas'), data.get('ref2_patrimonio'), data.get('ref2_responsable')
            ))
        conn.commit()
        return True, "Guardado correctamente"
    except Exception as e: return False, f"Error: {e}"
    finally: conn.close()

def obtener_microcredito(cedula):
    conn, cursor = conectar_db()
    cursor.row_factory = sqlite3.Row
    cursor.execute("SELECT * FROM Microcreditos WHERE cedula_cliente = ?", (cedula,))
    res = cursor.fetchone()
    conn.close()
    return dict(res) if res else None

# =================================================================
# DOCUMENTOS
# =================================================================
def guardar_archivo_db(cedula, nombre_archivo, ruta_archivo, tipo_doc):
    conn, cursor = conectar_db()
    try:
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO Documentos (cedula_cliente, nombre_archivo, tipo_documento, ruta_archivo, fecha_subida) VALUES (?,?,?,?,?)",
                       (cedula, nombre_archivo, tipo_doc, ruta_archivo, fecha))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally: conn.close()
