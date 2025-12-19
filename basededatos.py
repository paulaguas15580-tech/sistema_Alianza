import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3 
import hashlib 
import datetime
import os
import shutil
import subprocess
from PIL import Image, ImageTk 
import webbrowser
import customtkinter as ctk

# --- CONFIGURACIÓN CUSTOMTKINTER ---
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# =================================================================
# VARIABLES GLOBALES
# =================================================================

USUARIO_ACTIVO = None
NIVEL_ACCESO = 0 
CEDULA_CLIENTE_SELECCIONADO = None
ID_CLIENTE_SELECCIONADO = None 

DB_NAME = 'Alianza.db'

# =================================================================
# FUNCIÓN HELPER PARA LOGO
# =================================================================

def agregar_logo(ventana, logo_path="Logo Face.jpg", width=150, height=140):
    """Agrega el logo en la esquina superior derecha de la ventana"""
    try:
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            
            logo_label = tk.Label(ventana, image=logo_img, bg="#FAFAD2")
            logo_label.image = logo_img  # Keep reference to prevent garbage collection
            logo_label.pack(side='top', anchor='ne', padx=10, pady=10)
            return logo_label
    except Exception as e:
        print(f"Error cargando logo: {e}")
    return None

# =================================================================
# 1. BASE DE DATOS
# =================================================================

def generar_hash(clave):
    return hashlib.sha256(clave.encode()).hexdigest()

def conectar_db():
    conn = sqlite3.connect(DB_NAME)
    return conn, conn.cursor()

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
        # Verificar si existe la columna 'referencia_vivienda'
        cursor.execute("PRAGMA table_info(Clientes)")
        columnas = [info[1] for info in cursor.fetchall()]
        
        if 'referencia_vivienda' not in columnas:
            print("Migrando DB: Agregando columna 'referencia_vivienda'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN referencia_vivienda TEXT")
            conn.commit()
            print("Migración completada.")
            
        if 'situacion_financiera' not in columnas:
            print("Migrando DB: Agregando columna 'situacion_financiera'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN situacion_financiera TEXT")
            conn.commit()
            print("Migración completada.")
            
        if 'terreno' not in columnas:
            print("Migrando DB: Agregando columna 'terreno'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN terreno INTEGER DEFAULT 0")
            conn.commit()
            print("Migración completada.")

        if 'valor_terreno' not in columnas:
            print("Migrando DB: Agregando columna 'valor_terreno'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN valor_terreno REAL")
            conn.commit()
            print("Migración completada.")
            
        if 'hipotecado' not in columnas:
            print("Migrando DB: Agregando columna 'hipotecado'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN hipotecado TEXT")
            conn.commit()
            print("Migración completada.")
            
        if 'fuente_ingreso' not in columnas:
            print("Migrando DB: Agregando columna 'fuente_ingreso'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN fuente_ingreso TEXT")
            conn.commit()
            
        if 'ingresos_mensuales_2' not in columnas:
            print("Migrando DB: Agregando columna 'ingresos_mensuales_2'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN ingresos_mensuales_2 REAL")
            conn.commit()
        if 'fuente_ingreso_2' not in columnas:
            print("Migrando DB: Agregando columna 'fuente_ingreso_2'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN fuente_ingreso_2 TEXT")
            conn.commit()
            
        if 'casa_dep' not in columnas:
            print("Migrando DB: Agregando columna 'casa_dep'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN casa_dep INTEGER DEFAULT 0")
            conn.commit()
        if 'valor_casa_dep' not in columnas:
            print("Migrando DB: Agregando columna 'valor_casa_dep'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN valor_casa_dep REAL")
            conn.commit()
        if 'hipotecado_casa_dep' not in columnas:
            print("Migrando DB: Agregando columna 'hipotecado_casa_dep'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN hipotecado_casa_dep TEXT")
            conn.commit()
            
        if 'local' not in columnas:
            print("Migrando DB: Agregando columna 'local'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN local INTEGER DEFAULT 0")
            conn.commit()
        if 'valor_local' not in columnas:
            print("Migrando DB: Agregando columna 'valor_local'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN valor_local REAL")
            conn.commit()
        if 'hipotecado_local' not in columnas:
            print("Migrando DB: Agregando columna 'hipotecado_local'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN hipotecado_local TEXT")
            conn.commit()
            
        if 'score_buro' not in columnas:
            print("Migrando DB: Agregando columna 'score_buro'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN score_buro INTEGER")
            conn.commit()
            print("Migración completada new fields.")
            
        if 'egresos' not in columnas:
            print("Migrando DB: Agregando columna 'egresos'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN egresos REAL")
            conn.commit()
            
        if 'total_disponible' not in columnas:
            print("Migrando DB: Agregando columna 'total_disponible'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN total_disponible REAL")
            conn.commit()

        if 'valor_apertura' not in columnas:
            print("Migrando DB: Agregando columna 'valor_apertura'...")
            cursor.execute("ALTER TABLE Clientes ADD COLUMN valor_apertura REAL")
            conn.commit()
        
        # Verificar si existe la tabla Documentos
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
            print("Tabla 'Documentos' creada exitosamente.")
            
        # Verificar si existe la tabla Microcreditos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Microcreditos'")
        if not cursor.fetchone():
            print("Migrando DB: Creando tabla 'Microcreditos'...")
            cursor.execute("""
                CREATE TABLE Microcreditos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cedula_cliente TEXT NOT NULL,
                    ruc TEXT,
                    observaciones TEXT,
                    observaciones_info TEXT,
                    
                    ref1_relacion TEXT,
                    ref1_tiempo_conocer TEXT,
                    ref1_direccion TEXT,
                    ref1_tipo_vivienda TEXT,
                    ref1_cargas TEXT,
                    ref1_patrimonio TEXT,
                    ref1_responsable TEXT,
                    
                    ref2_relacion TEXT,
                    ref2_tiempo_conocer TEXT,
                    ref2_direccion TEXT,
                    ref2_tipo_vivienda TEXT,
                    ref2_cargas TEXT,
                    ref2_patrimonio TEXT,
                    ref2_responsable TEXT,
                    
                    FOREIGN KEY (cedula_cliente) REFERENCES Clientes(cedula)
                )
            """)
            conn.commit()
            print("Tabla 'Microcreditos' creada exitosamente.")
        else:
            # Si ya existe, verificar si falta observaciones_info
            cursor.execute("PRAGMA table_info(Microcreditos)")
            cols_micro = [info[1] for info in cursor.fetchall()]
            if 'observaciones_info' not in cols_micro:
                print("Migrando DB: Agregando columna 'observaciones_info' a Microcreditos...")
                cursor.execute("ALTER TABLE Microcreditos ADD COLUMN observaciones_info TEXT")
                conn.commit()
            
            # Verificar campos de llamadas (Fecha, Hora, Nombre, Telf)
            new_call_cols = [
                ('ref1_fecha', 'TEXT'), ('ref1_hora', 'TEXT'), ('ref1_nombre', 'TEXT'), ('ref1_telefono', 'TEXT'),
                ('ref2_fecha', 'TEXT'), ('ref2_hora', 'TEXT'), ('ref2_nombre', 'TEXT'), ('ref2_telefono', 'TEXT')
            ]
            for col_name, col_type in new_call_cols:
                if col_name not in cols_micro:
                    print(f"Migrando DB: Agregando columna '{col_name}' a Microcreditos...")
                    cursor.execute(f"ALTER TABLE Microcreditos ADD COLUMN {col_name} {col_type}")
                    conn.commit()
            
        # Migración Usuario Admin -> Paul
        cursor.execute("SELECT id FROM Usuarios WHERE usuario='admin'")
        admin_user = cursor.fetchone()
        if admin_user:
            print("Migrando usuario admin a Paul...")
            new_hash = generar_hash('cyberpol2022')
            cursor.execute("UPDATE Usuarios SET usuario=?, clave_hash=? WHERE id=?", ('Paul', new_hash, admin_user[0]))
            conn.commit()
            print("Usuario actualizado.")

    except Exception as e: print(f"Error Migración: {e}")
    finally: conn.close()

crear_tablas()
migrar_db()

# --- UTILIDADES DE FORMATO ---

def limpiar_moneda(valor_str):
    """Quita $ y comas para guardar en DB como número."""
    if not valor_str: return 0.0
    limpio = valor_str.replace('$', '').replace(',', '').strip()
    try: return float(limpio)
    except: return 0.0

def formatear_float_str(valor):
    """Convierte float a string '1,200.00'."""
    try:
        return "{:,.2f}".format(float(valor))
    except: return ""

# --- VALIDACIONES ---

def validar_datos(cedula, nombre, apertura, ingresos_str, val_cart_str, val_dem_str):
    if not nombre.strip(): return "El Nombre es obligatorio."
    if cedula.strip() and (len(cedula.strip()) != 10 or not cedula.strip().isdigit()):
        return "La Cédula debe tener 10 dígitos numéricos."
    
    try:
        limpiar_moneda(ingresos_str)
        limpiar_moneda(val_cart_str)
        limpiar_moneda(val_dem_str)
    except: return "Revise los campos numéricos."

    if apertura.strip():
        try: datetime.datetime.strptime(apertura, "%d/%m/%Y")
        except ValueError: return "Fecha Apertura incorrecta (DD/MM/YYYY)."
    return True

# --- CRUD ---

def guardar_cliente(*args):
    (cedula, ruc, nombre, est_civil, cargas, email, telf, dire, parr, viv, ref_viv,
     prof, ing_str, fuente_ing, terreno_val, val_terreno_str, hipotecado, ref1, ref2, asesor, aper, num_carpeta, nac, prod, obs, 
     cart, val_cart_str, dem, val_dem_str, just, det_just,
     casa_val, val_casa_str, hip_casa, local_val, val_local_str, hip_local,
     ing_str_2, fuente_ing_2, score_buro_str, egresos_str) = args

    val = validar_datos(cedula, nombre, aper, ing_str, val_cart_str, val_dem_str)
    if val is not True: return False, val
    
    ingresos = limpiar_moneda(ing_str)
    ingresos_2 = limpiar_moneda(ing_str_2)
    egresos = limpiar_moneda(egresos_str)
    valor_terreno = limpiar_moneda(val_terreno_str) if terreno_val else 0
    valor_casa = limpiar_moneda(val_casa_str) if casa_val else 0
    valor_local = limpiar_moneda(val_local_str) if local_val else 0
    val_cart = limpiar_moneda(val_cart_str) if cart else 0
    val_dem = limpiar_moneda(val_dem_str) if dem else 0
    
    # Calcular total disponible
    total_disponible = ingresos + ingresos_2 - egresos
    
    # Validar score_buro
    score_buro = None
    if score_buro_str.strip():
        try:
            score_buro = int(score_buro_str)
            if score_buro < 1 or score_buro > 999:
                return False, "Score Buró debe estar entre 1 y 999"
        except ValueError:
            return False, "Score Buró debe ser un número"
    
    conn, cursor = conectar_db()
    try:
        cursor.execute("""
            INSERT INTO Clientes (
                cedula, ruc, nombre, estado_civil, cargas_familiares, email, telefono, direccion, parroquia, 
                tipo_vivienda, referencia_vivienda, profesion, ingresos_mensuales, fuente_ingreso, terreno, valor_terreno, hipotecado, referencia1, referencia2, asesor, apertura, numero_carpeta, 
                "fecha nacimiento", producto, observaciones, 
                "cartera castigada", "valor cartera", "demanda judicial", "valor demanda", "problemas justicia", "detalle justicia",
                casa_dep, valor_casa_dep, hipotecado_casa_dep, local, valor_local, hipotecado_local,
                ingresos_mensuales_2, fuente_ingreso_2, score_buro, egresos, total_disponible
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cedula, ruc, nombre, est_civil, cargas, email, telf, dire, parr, viv, ref_viv,
              prof, ingresos, fuente_ing, terreno_val, valor_terreno, hipotecado, ref1, ref2, asesor, aper, num_carpeta, nac, prod, obs, 
              cart, val_cart, dem, val_dem, just, det_just,
              casa_val, valor_casa, hip_casa, local_val, valor_local, hip_local,
              ingresos_2, fuente_ing_2, score_buro, egresos, total_disponible))
        conn.commit()
        return True, "Guardado exitosamente."
    except sqlite3.IntegrityError: return False, "Cédula ya existe."
    except Exception as e: return False, f"Error: {e}"
    finally: conn.close()

def consultar_clientes():
    conn, cursor = conectar_db()
    try:
        cursor.execute("SELECT * FROM Clientes")
        return cursor.fetchall()
    finally: conn.close()

def actualizar_cliente(id_cliente, *args):
    (cedula, ruc, nombre, est_civil, cargas, email, telf, dire, parr, viv, ref_viv,
     prof, ing_str, fuente_ing, terreno_val, val_terreno_str, hipotecado, ref1, ref2, asesor, aper, num_carpeta, nac, prod, obs, 
     cart, val_cart_str, dem, val_dem_str, just, det_just,
     casa_val, val_casa_str, hip_casa, local_val, val_local_str, hip_local,
     ing_str_2, fuente_ing_2, score_buro_str, egresos_str) = args

    val = validar_datos(cedula, nombre, aper, ing_str, val_cart_str, val_dem_str)
    if val is not True: return False, val
    
    ingresos = limpiar_moneda(ing_str)
    ingresos_2 = limpiar_moneda(ing_str_2)
    egresos = limpiar_moneda(egresos_str)
    valor_terreno = limpiar_moneda(val_terreno_str) if terreno_val else 0
    valor_casa = limpiar_moneda(val_casa_str) if casa_val else 0
    valor_local = limpiar_moneda(val_local_str) if local_val else 0
    val_cart = limpiar_moneda(val_cart_str)
    val_dem = limpiar_moneda(val_dem_str)
    
    # Calcular total disponible
    total_disponible = ingresos + ingresos_2 - egresos
    
    # Validar score_buro
    score_buro = None
    if score_buro_str.strip():
        try:
            score_buro = int(score_buro_str)
            if score_buro < 1 or score_buro > 999:
                return False, "Score Buró debe estar entre 1 y 999"
        except ValueError:
            return False, "Score Buró debe ser un número"
    
    conn, cursor = conectar_db()
    try:
        cursor.execute("""
            UPDATE Clientes SET 
            cedula=?, ruc=?, nombre=?, estado_civil=?, cargas_familiares=?, email=?, telefono=?, direccion=?, parroquia=?, 
            tipo_vivienda=?, referencia_vivienda=?, profesion=?, ingresos_mensuales=?, fuente_ingreso=?, terreno=?, valor_terreno=?, hipotecado=?, referencia1=?, referencia2=?, asesor=?, apertura=?, numero_carpeta=?, 
            "fecha nacimiento"=?, producto=?, observaciones=?, 
            "cartera castigada"=?, "valor cartera"=?, "demanda judicial"=?, "valor demanda"=?, "problemas justicia"=?, "detalle justicia"=?,
            casa_dep=?, valor_casa_dep=?, hipotecado_casa_dep=?, local=?, valor_local=?, hipotecado_local=?,
            ingresos_mensuales_2=?, fuente_ingreso_2=?, score_buro=?, egresos=?, total_disponible=?
            WHERE id=?
        """, (cedula, ruc, nombre, est_civil, cargas, email, telf, dire, parr, viv, ref_viv,
              prof, ingresos, fuente_ing, terreno_val, valor_terreno, hipotecado, ref1, ref2, asesor, aper, num_carpeta, nac, prod, obs, 
              cart, val_cart, dem, val_dem, just, det_just,
              casa_val, valor_casa, hip_casa, local_val, valor_local, hip_local,
              ingresos_2, fuente_ing_2, score_buro, egresos, total_disponible, id_cliente))
        conn.commit()
        return True, "Actualizado correctamente."
    except Exception as e: return False, f"Error: {e}"
    finally: conn.close()

def eliminar_cliente(id_cliente):
    conn, cursor = conectar_db()
    cursor.execute("DELETE FROM Clientes WHERE id = ?", (id_cliente,))
    conn.commit()
    conn.close()
    return True, "Eliminado"

def buscar_clientes(termino):
    conn, cursor = conectar_db()
    t = '%' + termino + '%'
    cursor.execute("SELECT * FROM Clientes WHERE nombre LIKE ? OR cedula LIKE ? OR ruc LIKE ? OR numero_carpeta LIKE ?", (t,t,t,t))
    return cursor.fetchall()

# --- USUARIOS ---
def crear_usuario_db(usuario, clave, nivel):
    conn, cursor = conectar_db()
    try:
        cursor.execute("INSERT INTO Usuarios (usuario, clave_hash, nivel_acceso) VALUES (?, ?, ?)", (usuario, generar_hash(clave), nivel))
        conn.commit(); return True, "Ok"
    except: return False, "Error"
    finally: conn.close()

def verificar_credenciales(usuario, clave):
    conn, cursor = conectar_db()
    cursor.execute("SELECT clave_hash, nivel_acceso FROM Usuarios WHERE usuario = ?", (usuario,))
    res = cursor.fetchone()
    conn.close()
    if res and generar_hash(clave) == res[0]: return True, res[1]
    return False, 0

# =================================================================
# 2. INTERFAZ GRÁFICA
# =================================================================

# --- EVENTOS DE FORMATO MONEDA EN INTERFAZ ---
def on_focus_out_moneda(event):
    widget = event.widget
    texto = widget.get()
    try:
        val = limpiar_moneda(texto)
        if val > 0:
            widget.delete(0, tk.END)
            widget.insert(0, "{:,.2f}".format(val))
    except: pass

def on_focus_in_moneda(event):
    widget = event.widget
    texto = widget.get()
    try:
        val = limpiar_moneda(texto)
        if val == 0: widget.delete(0, tk.END)
        else:
            widget.delete(0, tk.END)
            widget.insert(0, str(val).replace('.0', '')) 
    except: pass

def saltar_campo(event):
    event.widget.tk_focusNext().focus()
    return "break"


    return (
        e_cedula.get().strip(), e_ruc.get().strip(), e_nombre.get().strip(),
        c_civil.get(), e_cargas.get().strip(), e_email.get().strip(), e_telf.get().strip(),
        e_dir.get().strip(), e_parroquia.get().strip(), c_vivienda.get(), e_ref_vivienda.get().strip(),
        e_profesion.get().strip(), e_ingresos.get().strip(), c_fuente_ingreso.get(), var_terreno.get(), e_valor_terreno.get().strip(), c_hipotecado.get(),
        e_ref1.get().strip(), e_ref2.get().strip(), e_asesor.get().strip(),
        e_apertura.get().strip(), e_carpeta.get().strip(), e_nacimiento.get().strip(), 
        c_producto.get().strip(), t_obs.get("1.0", tk.END).strip(), 
        var_cartera.get(), e_val_cartera.get().strip(),
        var_demanda.get(), e_val_demanda.get().strip(),
        var_justicia.get(), e_det_justicia.get().strip(),
        var_casa.get(), e_valor_casa.get().strip(), c_hip_casa.get(),
        var_local.get(), e_valor_local.get().strip(), c_hip_local.get(),
        e_ingresos_2.get().strip(), c_fuente_ingreso_2.get(),
        e_score_buro.get().strip(),
        e_egresos.get().strip()
    )

def limpiar_campos_ui():
    global ID_CLIENTE_SELECCIONADO
    elementos = [e_cedula, e_ruc, e_nombre, e_cargas, e_email, e_telf, e_dir, e_parroquia, e_ref_vivienda,
                 e_profesion, e_ingresos, e_ref1, e_ref2, e_asesor, e_apertura, e_carpeta, e_nacimiento, 
                 e_val_cartera, e_val_demanda, e_det_justicia, e_valor_terreno, e_valor_casa, e_valor_local, e_ingresos_2, e_score_buro, e_egresos]
    for e in elementos: e.delete(0, tk.END)
    
    t_obs.delete("1.0", tk.END)
    c_civil.set(''); c_vivienda.set(''); c_producto.set(''); c_hipotecado.set(''); c_hip_casa.set(''); c_hip_local.set('')
    c_fuente_ingreso.set(''); c_fuente_ingreso_2.set('')
    var_cartera.set(0); var_demanda.set(0); var_justicia.set(0); var_terreno.set(0); var_casa.set(0); var_local.set(0)
    toggle_legal_fields(); toggle_terreno(); toggle_casa(); toggle_local(); toggle_fuente_ingreso(); toggle_fuente_ingreso_2()
    
    # Limpiar total disponible
    lbl_total_disponible_valor.config(text="$ 0.00")
    
    ID_CLIENTE_SELECCIONADO = None
    btn_accion.config(text="💾 Guardar Nuevo", command=accion_guardar)
    btn_cancelar.grid_forget()
    if NIVEL_ACCESO == 1: btn_eliminar.grid(row=0, column=2, padx=10) 
    e_cedula.focus()

def mostrar_datos_tree():
    for i in tree.get_children(): tree.delete(i)
    data = consultar_clientes()
    for row in data:
        ing_fmt = "$ " + formatear_float_str(row[12])
        # ID, Cedula, Nombre, Telf, Ingresos, Sit.Financiera (CHECKBOX), Producto, Carpeta(N.Apertura), Asesor
        sf = "Terreno: Si" if (len(row) > 29 and row[29] == 1) else ""
        visual = (row[0], row[1], row[3], row[7], ing_fmt, sf, row[19], row[17], row[15])
        tree.insert('', tk.END, values=visual)

def accion_guardar():
    exito, msg = guardar_cliente(*obtener_campos_ui())
    if exito:
        messagebox.showinfo("Éxito", msg)
        limpiar_campos_ui(); mostrar_datos_tree()
    else: messagebox.showerror("Error", msg)

def accion_actualizar():
    if not ID_CLIENTE_SELECCIONADO: return
    exito, msg = actualizar_cliente(ID_CLIENTE_SELECCIONADO, *obtener_campos_ui())
    if exito:
        messagebox.showinfo("Éxito", msg)
        limpiar_campos_ui(); mostrar_datos_tree()
    else: messagebox.showerror("Error", msg)

def accion_eliminar():
    if not ID_CLIENTE_SELECCIONADO: return
    if messagebox.askyesno("Borrar", "¿Confirma?"):
        eliminar_cliente(ID_CLIENTE_SELECCIONADO)
        limpiar_campos_ui(); mostrar_datos_tree()

def accion_buscar():
    term = e_busqueda.get().strip()
    if not term: return mostrar_datos_tree()
    res = buscar_clientes(term)
    for i in tree.get_children(): tree.delete(i)
    for run in res:
        ing_fmt = "$ " + formatear_float_str(run[12])
        sf = "Terreno: Si" if (len(run) > 29 and run[29] == 1) else ""
        visual = (run[0], run[1], run[3], run[7], ing_fmt, sf, run[19], run[17], run[15])
        tree.insert('', tk.END, values=visual)

def cargar_seleccion(event):
    global ID_CLIENTE_SELECCIONADO
    sel = tree.selection()
    if not sel: return
    
    id_sel = tree.item(sel[0], 'values')[0]
    
    conn, cursor = conectar_db()
    cursor.execute("SELECT * FROM Clientes WHERE id = ?", (id_sel,))
    val = cursor.fetchone()
    conn.close()
    
    if not val: return

    ID_CLIENTE_SELECCIONADO = val[0]
    
    elementos = [e_cedula, e_ruc, e_nombre, e_cargas, e_email, e_telf, e_dir, e_parroquia, e_ref_vivienda,
                 e_profesion, e_ingresos, e_ref1, e_ref2, e_asesor, e_apertura, e_carpeta, e_nacimiento, 
                 e_val_cartera, e_val_demanda, e_det_justicia, e_valor_terreno, e_valor_casa, e_valor_local]
    for e in elementos: e.delete(0, tk.END)
    t_obs.delete("1.0", tk.END)
    
    try:
        e_cedula.insert(0, val[1])
        if val[2]: e_ruc.insert(0, val[2])
        e_nombre.insert(0, val[3])
        if val[4]: c_civil.set(val[4])
        if val[5]: e_cargas.insert(0, val[5])
        if val[6]: e_email.insert(0, val[6])
        if val[7]: e_telf.insert(0, val[7])
        if val[8]: e_dir.insert(0, val[8])
        if val[9]: e_parroquia.insert(0, val[9])
        if val[10]: c_vivienda.set(val[10])
        if val[11]: e_profesion.insert(0, val[11])
        
        if val[12]: e_ingresos.insert(0, formatear_float_str(val[12]))
        
        if len(val) > 38 and val[38]: c_fuente_ingreso.set(val[38])
            
        if val[13]: e_ref1.insert(0, val[13])
        if val[14]: e_ref2.insert(0, val[14])
        if val[15]: e_asesor.insert(0, val[15])
        if val[16]: e_apertura.insert(0, val[16])
        if val[17]: e_carpeta.insert(0, val[17])
        if val[18]: e_nacimiento.insert(0, val[18])
        if val[19]: c_producto.set(val[19])
        if val[20]: t_obs.insert("1.0", val[20])
        
        var_cartera.set(val[21])
        if val[22]: e_val_cartera.insert(0, formatear_float_str(val[22]))
        
        var_demanda.set(val[23])
        if val[24]: e_val_demanda.insert(0, formatear_float_str(val[24]))
        
        var_justicia.set(val[25])
        if val[26]: e_det_justicia.insert(0, val[26])
        
        toggle_legal_fields()

        if len(val) > 27 and val[27]: e_ref_vivienda.insert(0, val[27])
        # Ignoramos val[28] que era situacion_financiera texto antiguo
        if len(val) > 29: var_terreno.set(val[29] if val[29] else 0)
        if len(val) > 30 and val[30]: e_valor_terreno.insert(0, formatear_float_str(val[30]))
        if len(val) > 31 and val[31]: c_hipotecado.set(val[31])
        
        if len(val) > 32: var_casa.set(val[32] if val[32] else 0)
        if len(val) > 33 and val[33]: e_valor_casa.insert(0, formatear_float_str(val[33]))
        if len(val) > 34 and val[34]: c_hip_casa.set(val[34])
        
        if len(val) > 35: var_local.set(val[35] if val[35] else 0)
        if len(val) > 36 and val[36]: e_valor_local.insert(0, formatear_float_str(val[36]))
        if len(val) > 37 and val[37]: c_hip_local.set(val[37])
        
        if len(val) > 39 and val[39]: e_ingresos_2.insert(0, formatear_float_str(val[39]))
        if len(val) > 40 and val[40]: c_fuente_ingreso_2.set(val[40])
        
        if len(val) > 41 and val[41]: e_score_buro.insert(0, str(val[41]))
        
        if len(val) > 42 and val[42]: e_egresos.insert(0, formatear_float_str(val[42]))
        
        # Actualizar total disponible
        if len(val) > 43 and val[43]:
            lbl_total_disponible_valor.config(text="$ " + formatear_float_str(val[43]))
        else:
            calcular_total_disponible()

        toggle_terreno(); toggle_casa(); toggle_local(); toggle_fuente_ingreso(); toggle_fuente_ingreso_2()

    except Exception as e: print(f"Error carga: {e}")

    btn_accion.config(text="📝 Actualizar", command=accion_actualizar)
    btn_cancelar.grid(row=0, column=0, padx=10)

def toggle_legal_fields(*args):
    if var_cartera.get() == 1: 
        e_val_cartera.grid()
        lbl_dolar_cartera.grid()
    else: 
        e_val_cartera.grid_remove()
        lbl_dolar_cartera.grid_remove()
    
    if var_demanda.get() == 1: 
        e_val_demanda.grid()
        lbl_dolar_demanda.grid()
    else: 
        e_val_demanda.grid_remove()
        lbl_dolar_demanda.grid_remove()

    if var_justicia.get() == 1: 
        e_det_justicia.grid()
    else: 
        e_det_justicia.grid_remove()

def toggle_terreno(*args):
    if var_terreno.get() == 1:
        e_valor_terreno.pack(side='left', padx=5)
        f_terreno_hip.pack(anchor='w', padx=20)
    else:
        e_valor_terreno.pack_forget()
        f_terreno_hip.pack_forget()

def toggle_casa(*args):
    if var_casa.get() == 1:
        e_valor_casa.pack(side='left', padx=5)
        f_casa_hip.pack(anchor='w', padx=20)
    else:
        e_valor_casa.pack_forget()
        f_casa_hip.pack_forget()

def toggle_local(*args):
    if var_local.get() == 1:
        e_valor_local.pack(side='left', padx=5)
        f_local_hip.pack(anchor='w', padx=20)
    else:
        e_valor_local.pack_forget()
        f_local_hip.pack_forget()

def toggle_fuente_ingreso(*args):
    try:
        val = limpiar_moneda(e_ingresos.get())
        if val > 0: f_fuente_ingreso.pack(anchor='w', pady=(0,5))
        else: f_fuente_ingreso.pack_forget()
    except: f_fuente_ingreso.pack_forget()

def toggle_fuente_ingreso_2(*args):
    try:
        val = limpiar_moneda(e_ingresos_2.get())
        if val > 0: f_fuente_ingreso_2.pack(anchor='w', pady=(0,5))
        else: f_fuente_ingreso_2.pack_forget()
    except: f_fuente_ingreso_2.pack_forget()

def calcular_total_disponible(*args):
    """Calcula y muestra el total disponible: Ingresos 1 + Ingresos 2 - Egresos"""
    try:
        ing1 = limpiar_moneda(e_ingresos.get())
        ing2 = limpiar_moneda(e_ingresos_2.get())
        egr = limpiar_moneda(e_egresos.get())
        total = ing1 + ing2 - egr
        lbl_total_disponible_valor.config(text="$ " + formatear_float_str(total))
    except:
        lbl_total_disponible_valor.config(text="$ 0.00")

# --- VENTANA USUARIOS ---
def win_gestion_usuarios():
    top = tk.Toplevel()
    top.title("Usuarios"); top.geometry("500x350")
    
    def ref_u():
        for i in tr.get_children(): tr.delete(i)
        conn = sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("SELECT id, usuario, nivel_acceso FROM Usuarios")
        for u in c.fetchall(): tr.insert('', tk.END, values=(u[0], u[1], "Admin" if u[2]==1 else "Std"))
        conn.close()

    def add_u():
        crear_usuario_db(eu.get(), ep.get(), 1 if cr.get()=="Admin" else 2)
        ref_u(); eu.delete(0,tk.END); ep.delete(0,tk.END)

    def del_u():
        s = tr.selection()
        if s:
            conn = sqlite3.connect(DB_NAME); c=conn.cursor()
            c.execute("DELETE FROM Usuarios WHERE id=?", (tr.item(s[0],'values')[0],))
            conn.commit(); conn.close(); ref_u()
    
    f = ttk.Frame(top, padding=5); f.pack(fill='x')
    ttk.Label(f, text="U:").pack(side='left'); eu = ttk.Entry(f, width=10); eu.pack(side='left')
    eu.bind('<Return>', lambda e: ep.focus())
    ttk.Label(f, text="P:").pack(side='left'); ep = ttk.Entry(f, width=10); ep.pack(side='left')
    ep.bind('<Return>', lambda e: cr.focus())
    cr = ttk.Combobox(f, values=["Admin", "Std"], width=8); cr.current(1); cr.pack(side='left')
    cr.bind('<Return>', lambda e: add_u())
    ttk.Button(f, text="+", command=add_u).pack(side='left')
    tr = ttk.Treeview(top, columns=('id','us','rol'), show='headings'); tr.pack(fill='both', expand=True)
    tr.heading('id', text='ID'); tr.heading('us', text='Usuario'); tr.heading('rol', text='Rol')
    ttk.Button(top, text="Borrar", command=del_u).pack()
    ref_u()

# --- MÓDULO INFORMES Y DOCUMENTOS ---

def abrir_modulo_informes():
    global win_informes, e_cedula_buscar, e_nombre_cliente, tree_docs, cedula_actual
    
    cedula_actual = None
    
    win_informes = ctk.CTkToplevel()
    win_informes.title("Informes y Documentos")
    win_informes.geometry("1100x650")
    win_informes.after(100, lambda: win_informes.state('zoomed'))
    
    COLOR_FONDO = "#FAFAD2"
    win_informes.configure(fg_color=COLOR_FONDO)
    
    # Barra superior
    nav_frame = ctk.CTkFrame(win_informes, fg_color=COLOR_FONDO, height=40)
    nav_frame.pack(side='top', fill='x', pady=(5,0))
    ctk.CTkButton(nav_frame, text="Volver al Menú", command=win_informes.destroy, 
                  fg_color=COLOR_FONDO, text_color="#d9534f", hover_color="#EEE8AA", 
                  font=('Arial', 12, 'bold')).pack(side='right', padx=20)
    
    # Título
    ctk.CTkLabel(win_informes, text="GESTIÓN DE DOCUMENTOS", text_color="#1860C3", font=('Arial', 16, 'bold')).pack(pady=10)
    
    # Frame principal (Contenedor horizontal)
    main_frame = ctk.CTkFrame(win_informes, fg_color=COLOR_FONDO)
    main_frame.pack(fill='both', expand=True, padx=20, pady=10)

    # Panel Izquierdo (Contenido)
    left_panel = ctk.CTkFrame(main_frame, fg_color=COLOR_FONDO)
    left_panel.pack(side='left', fill='both', expand=True, padx=(0, 20))
    
    # SECCIÓN BÚSQUEDA DE CLIENTE
    search_frame = ctk.CTkFrame(left_panel, fg_color="white", border_width=1, border_color="grey")
    search_frame.pack(fill='x', pady=(0,10))
    
    ctk.CTkLabel(search_frame, text=" Buscar Cliente ", text_color="grey", font=('Arial', 10, 'bold')).place(x=10, y=-8)
    
    sf_in = ctk.CTkFrame(search_frame, fg_color="transparent")
    sf_in.pack(fill='x', padx=10, pady=15)
    
    ctk.CTkLabel(sf_in, text="Cédula:", text_color="black").pack(side='left')
    e_cedula_buscar = ctk.CTkEntry(sf_in, width=150, fg_color="white", text_color="black", border_color="grey")
    e_cedula_buscar.pack(side='left', padx=5)
    
    ctk.CTkLabel(sf_in, text="RUC:", text_color="black").pack(side='left', padx=(15,0))
    e_ruc_buscar = ctk.CTkEntry(sf_in, width=150, fg_color="white", text_color="black", border_color="grey")
    e_ruc_buscar.pack(side='left', padx=5)
    
    ctk.CTkLabel(sf_in, text="Cliente:", text_color="black").pack(side='left', padx=(15,0))
    e_nombre_cliente = ctk.CTkEntry(sf_in, width=350, fg_color="white", text_color="black", border_color="grey")
    e_nombre_cliente.pack(side='left', padx=5)
    
    # SECCIÓN DOCUMENTOS
    docs_frame = ctk.CTkFrame(left_panel, fg_color="white", border_width=1, border_color="grey")
    docs_frame.pack(fill='both', expand=True, pady=(0,10))
    
    ctk.CTkLabel(docs_frame, text=" Documentos del Cliente ", text_color="grey", font=('Arial', 10, 'bold')).place(x=10, y=-8)

    df_in = ctk.CTkFrame(docs_frame, fg_color="transparent")
    df_in.pack(fill='both', expand=True, padx=10, pady=15)
    
    # Botones
    btn_frame = ctk.CTkFrame(df_in, fg_color="transparent")
    btn_frame.pack(fill='x', pady=(0,10))
    
    ctk.CTkButton(btn_frame, text="📎 Subir Archivo PDF", command=subir_documento, fg_color="#465EA6", hover_color="#1860C3").pack(side='left', padx=5)
    ctk.CTkButton(btn_frame, text="👁️ Ver Documento", command=ver_documento, fg_color="#465EA6", hover_color="#1860C3").pack(side='left', padx=5)
    ctk.CTkButton(btn_frame, text="🗑️ Eliminar Documento", command=eliminar_documento, fg_color="#d9534f", hover_color="#c9302c").pack(side='left', padx=5)
    
    # TreeView documentos
    tree_frame = ctk.CTkFrame(df_in, fg_color="white")
    tree_frame.pack(fill='both', expand=True)
    
    cols = ("ID", "Tipo", "Nombre Archivo", "Fecha")
    tree_docs = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)
    
    tree_docs.heading("ID", text="ID")
    tree_docs.heading("Tipo", text="Tipo")
    tree_docs.heading("Nombre Archivo", text="Nombre Archivo")
    tree_docs.heading("Fecha", text="Fecha Subida")
    
    tree_docs.column("ID", width=50)
    tree_docs.column("Tipo", width=150)
    tree_docs.column("Nombre Archivo", width=300)
    tree_docs.column("Fecha", width=150)
    
    scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree_docs.yview)
    scrollbar.pack(side='right', fill='y')
    tree_docs.configure(yscrollcommand=scrollbar.set)
    tree_docs.pack(fill='both', expand=True)

    # Logo (Panel Derecho)
    try:
        img = Image.open("Logo Face.jpg")
        logo_docs = ctk.CTkImage(light_image=img, dark_image=img, size=(225, 210))
        lbl = ctk.CTkLabel(main_frame, image=logo_docs, text="")
        lbl.pack(side='right', padx=20, anchor='n')
    except: 
        ctk.CTkLabel(main_frame, text="LOGO", text_color="grey").pack(side='right', padx=20, anchor='n')

    
    def buscar_cliente_auto(event=None):
        global cedula_actual
        
        ced = e_cedula_buscar.get().strip()
        ruc = e_ruc_buscar.get().strip()
        nom = e_nombre_cliente.get().strip()
        
        criteria = None
        val = None
        
        if len(ced) == 10 and ced.isdigit():
            criteria = "cedula"
            val = ced
        elif len(ruc) >= 10 and ruc.isdigit():
             criteria = "ruc"
             val = ruc
        elif len(nom) >= 3:
             criteria = "nombre"
             val = nom
        
        if not criteria: return # Or clear if empty?

        conn, cursor = conectar_db()
        res = None
        
        if criteria == "cedula":
             cursor.execute("SELECT nombre, cedula, ruc FROM Clientes WHERE cedula = ?", (val,))
             res = cursor.fetchone()
        elif criteria == "ruc":
             cursor.execute("SELECT nombre, cedula, ruc FROM Clientes WHERE ruc = ?", (val,))
             res = cursor.fetchone()
        elif criteria == "nombre":
             cursor.execute("SELECT nombre, cedula, ruc FROM Clientes WHERE nombre LIKE ? LIMIT 1", (f"%{val}%",))
             res = cursor.fetchone()
        
        conn.close()
        
        if res:
            widget = event.widget if event else None
            # res: 0:nombre, 1:cedula, 2:ruc
            
            if criteria != "nombre" or (widget != e_nombre_cliente):
                e_nombre_cliente.delete(0, tk.END); e_nombre_cliente.insert(0, res[0])
            
            if criteria != "ruc" or (widget != e_ruc_buscar):
                e_ruc_buscar.delete(0, tk.END); 
                if res[2]: e_ruc_buscar.insert(0, res[2])
                
            if criteria != "cedula" or (widget != e_cedula_buscar):
                 e_cedula_buscar.delete(0, tk.END); e_cedula_buscar.insert(0, res[1])
            
            cedula_actual = res[1]
            cargar_documentos(cedula_actual)
        else:
            cedula_actual = None
            limpiar_lista_documentos()
            # Optional: e_nombre_cliente.insert(0, "No encontrado") ... but tricky with typing
    
    e_cedula_buscar.bind('<KeyRelease>', buscar_cliente_auto)
    e_ruc_buscar.bind('<KeyRelease>', buscar_cliente_auto)
    e_nombre_cliente.bind('<KeyRelease>', buscar_cliente_auto)

def limpiar_lista_documentos():
    for item in tree_docs.get_children():
        tree_docs.delete(item)

def cargar_documentos(cedula):
    limpiar_lista_documentos()
    conn, cursor = conectar_db()
    cursor.execute("SELECT id, tipo_documento, nombre_archivo, fecha_subida FROM Documentos WHERE cedula_cliente = ? ORDER BY fecha_subida DESC", (cedula,))
    documentos = cursor.fetchall()
    conn.close()
    
    for doc in documentos:
        tree_docs.insert('', tk.END, values=doc)

def subir_documento():
    global cedula_actual
    
    if not cedula_actual:
        messagebox.showwarning("Advertencia", "Debe seleccionar un cliente válido primero")
        return
    
    # Abrir diálogo para seleccionar archivo PDF
    archivo = filedialog.askopenfilename(
        title="Seleccionar documento PDF",
        filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
    )
    
    if not archivo:
        return
    
    # Verificar que sea PDF
    if not archivo.lower().endswith('.pdf'):
        messagebox.showerror("Error", "Solo se permiten archivos PDF")
        return
    
    # Solicitar tipo de documento
    tipo_win = tk.Toplevel(win_informes)
    tipo_win.title("Tipo de Documento")
    tipo_win.geometry("400x150")
    tipo_win.transient(win_informes)
    tipo_win.grab_set()
    
    ttk.Label(tipo_win, text="Seleccione el tipo de documento:", font=('Arial', 10)).pack(pady=10)
    
    tipo_var = tk.StringVar()
    tipo_combo = ttk.Combobox(tipo_win, textvariable=tipo_var, width=30, state='readonly')
    tipo_combo['values'] = ("Buró de Crédito", "Escrituras", "Cédula", "Papeleta de Votación", "Planilla de Servicios Básicos", "Certificado Laboral", "Otros")
    tipo_combo.current(0)
    tipo_combo.pack(pady=10)
    
    def confirmar_tipo():
        tipo = tipo_var.get()
        tipo_win.destroy()
        guardar_documento_db(cedula_actual, archivo, tipo)
    
    ttk.Button(tipo_win, text="Confirmar", command=confirmar_tipo).pack(pady=10)
    tipo_win.wait_window()

def guardar_documento_db(cedula, archivo_origen, tipo):
    try:
        # Crear directorio si no existe
        directorio_base = "Documentos"
        directorio_cliente = os.path.join(directorio_base, cedula)
        
        if not os.path.exists(directorio_base):
            os.makedirs(directorio_base)
        if not os.path.exists(directorio_cliente):
            os.makedirs(directorio_cliente)
        
        # Copiar archivo
        nombre_archivo = os.path.basename(archivo_origen)
        ruta_destino = os.path.join(directorio_cliente, nombre_archivo)
        
        # Si ya existe, agregar timestamp
        if os.path.exists(ruta_destino):
            nombre_base, extension = os.path.splitext(nombre_archivo)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"{nombre_base}_{timestamp}{extension}"
            ruta_destino = os.path.join(directorio_cliente, nombre_archivo)
        
        shutil.copy2(archivo_origen, ruta_destino)
        
        # Guardar en base de datos
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn, cursor = conectar_db()
        cursor.execute("""
            INSERT INTO Documentos (cedula_cliente, nombre_archivo, tipo_documento, ruta_archivo, fecha_subida)
            VALUES (?, ?, ?, ?, ?)
        """, (cedula, nombre_archivo, tipo, ruta_destino, fecha_actual))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Éxito", "Documento subido correctamente")
        cargar_documentos(cedula)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al subir documento: {e}")

def ver_documento():
    seleccion = tree_docs.selection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Debe seleccionar un documento")
        return
    
    doc_id = tree_docs.item(seleccion[0])['values'][0]
    
    conn, cursor = conectar_db()
    cursor.execute("SELECT ruta_archivo FROM Documentos WHERE id = ?", (doc_id,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        ruta = resultado[0]
        if os.path.exists(ruta):
            try:
                # Abrir con el visor predeterminado
                os.startfile(ruta)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el documento: {e}")
        else:
            messagebox.showerror("Error", "El archivo no existe en la ruta especificada")

def eliminar_documento():
    global cedula_actual
    
    seleccion = tree_docs.selection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Debe seleccionar un documento")
        return
    
    if not messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este documento?"):
        return
    
    doc_id = tree_docs.item(seleccion[0])['values'][0]
    
    conn, cursor = conectar_db()
    cursor.execute("SELECT ruta_archivo FROM Documentos WHERE id = ?", (doc_id,))
    resultado = cursor.fetchone()
    
    if resultado:
        ruta = resultado[0]
        # Eliminar archivo físico
        if os.path.exists(ruta):
            try:
                os.remove(ruta)
            except Exception as e:
                print(f"Error al eliminar archivo: {e}")
        
        # Eliminar de base de datos
        cursor.execute("DELETE FROM Documentos WHERE id = ?", (doc_id,))
        conn.commit()
    
    conn.close()
    messagebox.showinfo("Éxito", "Documento eliminado")
    cargar_documentos(cedula_actual)

# --- APP PRINCIPAL ---

def login_fn(app, u_entry, p_entry):
    global USUARIO_ACTIVO, NIVEL_ACCESO
    
    u = u_entry.get()
    p = p_entry.get()
    
    ok, lvl = verificar_credenciales(u, p)
    if ok:
        USUARIO_ACTIVO = u; NIVEL_ACCESO = lvl
        
        # Clear current window (Login)
        for widget in app.winfo_children():
            widget.destroy()
            
        # Open Menu in same window
        abrir_menu_principal(app)
    else:
        messagebox.showerror("Error", "Datos incorrectos")


def abrir_menu_principal(app_root=None):
    global menu_app
    
    if app_root:
        menu_app = app_root
    else:
        # Fallback if called separately (shouldn't happen in new flow)
        menu_app = ctk.CTk()
    
    menu_app.title("Menú Principal - Alianza C3F")
    
    # 30cm x 20cm aprox (96 DPI: 1cm=37.8px) -> 1134x756
    width = 1134
    height = 756
    
    # Centrar en pantalla
    screen_width = menu_app.winfo_screenwidth()
    screen_height = menu_app.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    menu_app.geometry(f"{width}x{height}+{x}+{y}")
    # menu_app.state('zoomed') 
    menu_app.after(100, lambda: menu_app.state('zoomed')) # Increased delay slightly

    # Configuración Grid
    menu_app.grid_columnconfigure(0, weight=1)
    menu_app.grid_rowconfigure(2, weight=1)

    # Header
    ctk.CTkLabel(menu_app, text="Sistema Alianza C3F", font=("Arial", 30, "bold"), text_color="#1860C3").grid(row=0, column=0, pady=20)

    # Logo
    try:
        img = Image.open("Logo Face.jpg")
        width, height = img.size
        new_size = (int(width * 0.5), int(height * 0.5))
        logo_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=new_size)
        lbl_logo = ctk.CTkLabel(menu_app, image=logo_ctk, text="")
        lbl_logo.grid(row=1, column=0, pady=10)
    except Exception as e:
        print(f"Error cargando logo: {e}")
    
    # Grid de Botones
    frame_botones = ctk.CTkFrame(menu_app, fg_color="transparent")
    frame_botones.grid(row=2, column=0, sticky="nsew", padx=50, pady=20)
    
    frame_botones.grid_columnconfigure(0, weight=1)
    frame_botones.grid_columnconfigure(1, weight=1)
    frame_botones.grid_columnconfigure(2, weight=1)

    # Definir botones (Texto, Función)
    botones = [
        ("Gestión de Clientes", abrir_modulo_clientes),
        ("Rehabilitación", abrir_modulo_rehabilitacion),
        ("Microcrédito", abrir_modulo_microcredito),
        ("Intermediación", abrir_modulo_intermediacion),
        ("Cartera", abrir_modulo_cartera),
        ("Documentos", abrir_modulo_informes),
        ("Consultas", abrir_modulo_consultas),
        ("Informes", abrir_modulo_informes),
    ]
    
    if NIVEL_ACCESO == 1:
        botones.append(("Usuarios", lambda: messagebox.showinfo("Info", "Módulo Usuarios")))
    
    # Boton Salir cierra la app completa
    botones.append(("Salir Sistema", menu_app.destroy))
    
    row = 0
    col = 0
    
    for texto, funcion in botones:
        btn = ctk.CTkButton(
            frame_botones, 
            text=texto, 
            command=funcion,
            font=("Arial", 16, "bold"),
            height=50,
            width=250,
            fg_color="#465EA6",
            hover_color="#1860C3"
        )
        btn.grid(row=row, column=col, padx=10, pady=15) # Reduced horizontal padding slightly
        
        col += 1
        if col > 2: # 3 Columns (0, 1, 2)
            col = 0
            row += 1

    # Footer
    label_footer = ctk.CTkLabel(menu_app, text=f"Usuario: {USUARIO_ACTIVO} | Nivel: {NIVEL_ACCESO}", text_color="grey")
    label_footer.grid(row=3, column=0, pady=10)
    
    # Ensure window update
    menu_app.update()

def abrir_modulo_clientes():
    global app, e_cedula, e_ruc, e_nombre, c_civil, e_cargas, e_email, e_telf, e_dir, e_parroquia
    global c_vivienda, e_ref_vivienda, e_profesion, e_ingresos, e_ref1, e_ref2, e_asesor, e_apertura, e_carpeta, e_nacimiento
    global c_producto, t_obs, var_cartera, var_demanda, var_justicia, btn_accion, btn_cancelar, btn_eliminar
    global e_busqueda, tree, e_val_cartera, e_val_demanda, e_det_justicia, var_terreno, e_valor_terreno
    global lbl_dolar_cartera, lbl_dolar_demanda
    global c_hipotecado, f_terreno_hip
    global var_casa, e_valor_casa, c_hip_casa, f_casa_hip
    global var_local, e_valor_local, c_hip_local, f_local_hip
    global c_fuente_ingreso, f_fuente_ingreso
    global e_ingresos_2, c_fuente_ingreso_2, f_fuente_ingreso_2
    global e_score_buro
    global e_egresos, lbl_total_disponible_valor

    app = ctk.CTkToplevel()
    app.title("Módulo de Clientes")
    app.geometry("1350x850")
    app.after(100, lambda: app.state('zoomed'))

    # --- TEMA Y COLORES ---
    # Mantener el color de fondo pedido por el usuario
    COLOR_FONDO = "#FAFAD2" # LightGoldenrodYellow
    COLOR_TEXTO = "#000000" # Negro
    COLOR_BTN_BG = "#465EA6"
    COLOR_BTN_HOVER = "#1860C3"
    
    app.configure(fg_color=COLOR_FONDO)
    
    # --- BARRA DE NAVEGACIÓN (Solo cerrar) ---
    nav_frame = ctk.CTkFrame(app, fg_color=COLOR_FONDO, height=40)
    nav_frame.pack(side='top', fill='x', pady=(5,0))
    ctk.CTkButton(nav_frame, text="Volver al Menú", command=app.destroy, 
                  fg_color=COLOR_FONDO, text_color="#d9534f", hover_color="#EEE8AA", 
                  font=('Arial', 12, 'bold')).pack(side='right', padx=20)



    # Variables de control
    var_cartera = tk.IntVar(); var_demanda = tk.IntVar(); var_justicia = tk.IntVar()
    var_terreno = tk.IntVar(); var_casa = tk.IntVar(); var_local = tk.IntVar()
    var_cartera.trace_add('write', toggle_legal_fields)
    var_demanda.trace_add('write', toggle_legal_fields)
    var_justicia.trace_add('write', toggle_legal_fields)
    var_terreno.trace_add('write', toggle_terreno)
    var_casa.trace_add('write', toggle_casa)
    var_local.trace_add('write', toggle_local)

    # --- TOP ---
    top_frame = ctk.CTkFrame(app, fg_color=COLOR_FONDO)
    top_frame.pack(fill='x', padx=10, pady=5)
    
    # "LabelFrame" simulation using Frame
    f_form = ctk.CTkFrame(top_frame, fg_color="white", border_width=1, border_color="grey") # White bg for contrast inside form
    f_form.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    ctk.CTkLabel(top_frame, text="Ficha del Cliente", font=('Arial', 12, 'bold'), text_color=COLOR_TEXTO).place(x=15, y=0) 

    # Helper para crear Entries con estilo consistente
    def crear_entry(parent, width=None):
        e = ctk.CTkEntry(parent, fg_color="white", text_color="black", border_color="grey")
        if width: e.configure(width=width)
        return e

    # COL 1
    c1 = ctk.CTkFrame(f_form, fg_color="transparent")
    c1.grid(row=0, column=0, padx=10, pady=10, sticky='n')
    ctk.CTkLabel(c1, text="DATOS PERSONALES", text_color="#1860C3", font=('Arial', 12, 'bold')).pack(pady=5)
    
    ctk.CTkLabel(c1, text="Cédula:", text_color="black").pack(anchor='w')
    e_cedula = crear_entry(c1); e_cedula.pack(fill='x')
    e_cedula.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c1, text="RUC:", text_color="black").pack(anchor='w')
    e_ruc = crear_entry(c1); e_ruc.pack(fill='x')
    e_ruc.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c1, text="Nombres y Apellidos:", text_color="black").pack(anchor='w')
    e_nombre = crear_entry(c1); e_nombre.pack(fill='x')
    e_nombre.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c1, text="F. Nacim:", text_color="black").pack(anchor='w')
    e_nacimiento = crear_entry(c1); e_nacimiento.pack(fill='x')
    e_nacimiento.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c1, text="Civil:", text_color="black").pack(anchor='w')
    c_civil = ctk.CTkComboBox(c1, values=["Soltero", "Casado", "Divorciado", "Viudo", "Unión Libre"], fg_color="white", text_color="black", border_color="grey", button_color="#1860C3")
    c_civil.pack(fill='x')
    
    ctk.CTkLabel(c1, text="Cargas:", text_color="black").pack(anchor='w')
    e_cargas = crear_entry(c1); e_cargas.pack(fill='x')
    e_cargas.bind('<Return>', saltar_campo)

    # COL 2
    c2 = ctk.CTkFrame(f_form, fg_color="transparent")
    c2.grid(row=0, column=1, padx=10, pady=10, sticky='n')
    ctk.CTkLabel(c2, text="CONTACTO", text_color="#1860C3", font=('Arial', 12, 'bold')).pack(pady=5)
    
    ctk.CTkLabel(c2, text="Telf:", text_color="black").pack(anchor='w')
    e_telf = crear_entry(c2); e_telf.pack(fill='x')
    e_telf.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c2, text="Email:", text_color="black").pack(anchor='w')
    e_email = crear_entry(c2); e_email.pack(fill='x')
    e_email.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c2, text="Dirección:", text_color="black").pack(anchor='w')
    e_dir = crear_entry(c2); e_dir.pack(fill='x')
    e_dir.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c2, text="Parroquia:", text_color="black").pack(anchor='w')
    e_parroquia = crear_entry(c2); e_parroquia.pack(fill='x')
    e_parroquia.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c2, text="Vivienda:", text_color="black").pack(anchor='w')
    c_vivienda = ctk.CTkComboBox(c2, values=["Propia", "Arrendada", "Familiar", "Hipotecada"], fg_color="white", text_color="black", border_color="grey", button_color="#1860C3")
    c_vivienda.pack(fill='x')
    
    ctk.CTkLabel(c2, text="Ref. Vivienda:", text_color="black").pack(anchor='w')
    e_ref_vivienda = crear_entry(c2); e_ref_vivienda.pack(fill='x')
    e_ref_vivienda.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c2, text="Ref. y Telf. 1:", text_color="black").pack(anchor='w')
    e_ref1 = crear_entry(c2); e_ref1.pack(fill='x')
    e_ref1.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c2, text="Ref. y Telf. 2:", text_color="black").pack(anchor='w')
    e_ref2 = crear_entry(c2); e_ref2.pack(fill='x')
    e_ref2.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c2, text="Asesor:", text_color="black").pack(anchor='w')
    e_asesor = crear_entry(c2); e_asesor.pack(fill='x')
    e_asesor.bind('<Return>', saltar_campo)

    # COL 3 - SITUACION FINANCIERA
    c3 = ctk.CTkFrame(f_form, fg_color="transparent")
    c3.grid(row=0, column=2, padx=10, pady=10, sticky='n')
    ctk.CTkLabel(c3, text="SITUACIÓN FINANCIERA", text_color="#1860C3", font=('Arial', 12, 'bold')).pack(pady=5)
    
    # SCORE BURÓ
    c_score_buro = ctk.CTkFrame(c3, fg_color="transparent")
    c_score_buro.pack(fill='x', anchor='w', pady=(0, 5))
    ctk.CTkLabel(c_score_buro, text="Score Buró (1-999):", text_color="black").pack(anchor='w')
    e_score_buro = crear_entry(c_score_buro, width=100); e_score_buro.pack(anchor='w')
    e_score_buro.bind('<Return>', saltar_campo)
    
    # INGRESOS
    c_ingresos = ctk.CTkFrame(c3, fg_color="transparent")
    c_ingresos.pack(fill='x', anchor='w', pady=(0, 5))
    ctk.CTkLabel(c_ingresos, text="Ingresos ($):", text_color="black").pack(anchor='w')
    e_ingresos = crear_entry(c_ingresos); e_ingresos.pack(fill='x')
    e_ingresos.bind('<Return>', saltar_campo)
    e_ingresos.bind('<FocusOut>', lambda e: (on_focus_out_moneda(e), toggle_fuente_ingreso())) 
    e_ingresos.bind('<FocusIn>', on_focus_in_moneda)
    
    f_fuente_ingreso = ctk.CTkFrame(c_ingresos, fg_color="transparent")
    ctk.CTkLabel(f_fuente_ingreso, text="Fuente:", text_color="black").pack(side='left')
    c_fuente_ingreso = ctk.CTkComboBox(f_fuente_ingreso, values=["Sueldo", "Negocio", "Jubilacion", "Arriendo", "Inversiones", "Remesas del Exterior", "Otros"], width=150, fg_color="white", text_color="black", border_color="grey")
    c_fuente_ingreso.pack(side='left', padx=5)
    f_fuente_ingreso.pack_forget()
    
    # INGRESOS 2
    c_ingresos_2 = ctk.CTkFrame(c3, fg_color="transparent")
    c_ingresos_2.pack(fill='x', anchor='w', pady=(0, 5))
    ctk.CTkLabel(c_ingresos_2, text="Ingresos 2 ($):", text_color="black").pack(anchor='w')
    e_ingresos_2 = crear_entry(c_ingresos_2); e_ingresos_2.pack(fill='x')
    e_ingresos_2.bind('<Return>', saltar_campo)
    e_ingresos_2.bind('<FocusOut>', lambda e: (on_focus_out_moneda(e), toggle_fuente_ingreso_2())) 
    e_ingresos_2.bind('<FocusIn>', on_focus_in_moneda)
    
    f_fuente_ingreso_2 = ctk.CTkFrame(c_ingresos_2, fg_color="transparent")
    ctk.CTkLabel(f_fuente_ingreso_2, text="Fuente 2:", text_color="black").pack(side='left')
    c_fuente_ingreso_2 = ctk.CTkComboBox(f_fuente_ingreso_2, values=["Sueldo", "Negocio", "Jubilacion", "Arriendo", "Inversiones", "Remesas del Exterior", "Otros"], width=150, fg_color="white", text_color="black", border_color="grey")
    c_fuente_ingreso_2.pack(side='left', padx=5)
    f_fuente_ingreso_2.pack_forget()
    
    # EGRESOS
    c_egresos = ctk.CTkFrame(c3, fg_color="transparent")
    c_egresos.pack(fill='x', anchor='w', pady=(0, 5))
    ctk.CTkLabel(c_egresos, text="Egresos ($):", text_color="black").pack(anchor='w')
    e_egresos = crear_entry(c_egresos); e_egresos.pack(fill='x')
    e_egresos.bind('<Return>', saltar_campo)
    e_egresos.bind('<FocusOut>', lambda e: (on_focus_out_moneda(e), calcular_total_disponible()))
    e_egresos.bind('<FocusIn>', on_focus_in_moneda)
    
    # TOTAL DISPONIBLE
    c_total_disponible = ctk.CTkFrame(c3, fg_color="transparent")
    c_total_disponible.pack(fill='x', anchor='w', pady=(0, 10))
    ctk.CTkLabel(c_total_disponible, text="Total Disponible:", font=('Arial', 12, 'bold'), text_color="black").pack(anchor='w')
    lbl_total_disponible_valor = ctk.CTkLabel(c_total_disponible, text="$ 0.00", font=('Arial', 14, 'bold'), text_color='#006400')
    lbl_total_disponible_valor.pack(anchor='w')
    
    # Bind calculation to ingresos fields as well
    e_ingresos.bind('<KeyRelease>', calcular_total_disponible)
    e_ingresos_2.bind('<KeyRelease>', calcular_total_disponible)
    e_egresos.bind('<KeyRelease>', calcular_total_disponible)
    
    # --- TERRENO ---
    c_terreno = ctk.CTkFrame(c3, fg_color="transparent")
    c_terreno.pack(fill='x', anchor='w', pady=2)
    f_terreno_r1 = ctk.CTkFrame(c_terreno, fg_color="transparent")
    f_terreno_r1.pack(fill='x', anchor='w')
    ctk.CTkCheckBox(f_terreno_r1, text="Terreno", variable=var_terreno, text_color="black").pack(side='left')
    e_valor_terreno = crear_entry(f_terreno_r1, width=100)
    e_valor_terreno.bind('<FocusOut>', on_focus_out_moneda); e_valor_terreno.bind('<FocusIn>', on_focus_in_moneda); e_valor_terreno.bind('<Return>', saltar_campo)
    e_valor_terreno.pack_forget()
    
    f_terreno_hip = ctk.CTkFrame(c_terreno, fg_color="transparent"); f_terreno_hip.pack(fill='x', anchor='w', padx=20)
    ctk.CTkLabel(f_terreno_hip, text="Hipotecado:", text_color="black").pack(side='left')
    c_hipotecado = ctk.CTkComboBox(f_terreno_hip, values=["Si", "No"], width=70, fg_color="white", text_color="black"); c_hipotecado.pack(side='left', padx=5)
    f_terreno_hip.pack_forget()

    # --- CASA ---
    c_casa = ctk.CTkFrame(c3, fg_color="transparent"); c_casa.pack(fill='x', anchor='w', pady=2)
    f_casa_r1 = ctk.CTkFrame(c_casa, fg_color="transparent"); f_casa_r1.pack(fill='x', anchor='w')
    ctk.CTkCheckBox(f_casa_r1, text="Casa o Dep", variable=var_casa, text_color="black").pack(side='left')
    e_valor_casa = crear_entry(f_casa_r1, width=100)
    e_valor_casa.bind('<FocusOut>', on_focus_out_moneda); e_valor_casa.bind('<FocusIn>', on_focus_in_moneda); e_valor_casa.bind('<Return>', saltar_campo)
    e_valor_casa.pack_forget()
    
    f_casa_hip = ctk.CTkFrame(c_casa, fg_color="transparent"); f_casa_hip.pack(fill='x', anchor='w', padx=20)
    ctk.CTkLabel(f_casa_hip, text="Hipotecado:", text_color="black").pack(side='left')
    c_hip_casa = ctk.CTkComboBox(f_casa_hip, values=["Si", "No"], width=70, fg_color="white", text_color="black"); c_hip_casa.pack(side='left', padx=5)
    f_casa_hip.pack_forget()

    # --- LOCAL ---
    c_local = ctk.CTkFrame(c3, fg_color="transparent"); c_local.pack(fill='x', anchor='w', pady=2)
    f_local_r1 = ctk.CTkFrame(c_local, fg_color="transparent"); f_local_r1.pack(fill='x', anchor='w')
    ctk.CTkCheckBox(f_local_r1, text="Local", variable=var_local, text_color="black").pack(side='left')
    e_valor_local = crear_entry(f_local_r1, width=100)
    e_valor_local.bind('<FocusOut>', on_focus_out_moneda); e_valor_local.bind('<FocusIn>', on_focus_in_moneda); e_valor_local.bind('<Return>', saltar_campo)
    e_valor_local.pack_forget()
    
    f_local_hip = ctk.CTkFrame(c_local, fg_color="transparent"); f_local_hip.pack(fill='x', anchor='w', padx=20)
    ctk.CTkLabel(f_local_hip, text="Hipotecado:", text_color="black").pack(side='left')
    c_hip_local = ctk.CTkComboBox(f_local_hip, values=["Si", "No"], width=70, fg_color="white", text_color="black"); c_hip_local.pack(side='left', padx=5)
    f_local_hip.pack_forget()

    # COL 4 - CRÉDITO Y LEGAL
    c4 = ctk.CTkFrame(f_form, fg_color="transparent")
    c4.grid(row=0, column=3, padx=10, pady=10, sticky='n')
    ctk.CTkLabel(c4, text="CRÉDITO Y LEGAL", text_color="#1860C3", font=('Arial', 12, 'bold')).pack(pady=5)
    
    ctk.CTkLabel(c4, text="Profesión:", text_color="black").pack(anchor='w')
    e_profesion = crear_entry(c4); e_profesion.pack(fill='x')
    e_profesion.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c4, text="F. Apertura:", text_color="black").pack(anchor='w')
    e_apertura = crear_entry(c4); e_apertura.pack(fill='x')
    e_apertura.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c4, text="N. Apertura:", text_color="black").pack(anchor='w')
    e_carpeta = crear_entry(c4); e_carpeta.pack(fill='x')
    e_carpeta.bind('<Return>', saltar_campo)
    
    ctk.CTkLabel(c4, text="Producto:", text_color="black").pack(anchor='w')
    c_producto = ctk.CTkComboBox(c4, values=["Rehabilitación", "Microcrédito", "Intermediación"], fg_color="white", text_color="black"); c_producto.pack(fill='x')
    
    ctk.CTkLabel(c4, text="Obs:", text_color="black").pack(anchor='w')
    t_obs = tk.Text(c4, height=3, width=30, font=('Arial', 9)); t_obs.pack(fill='x') 

    # LEGAL Frame
    fl = ctk.CTkFrame(c4, fg_color="white", border_width=1, border_color="grey")
    fl.pack(fill='x', pady=5)
    ctk.CTkLabel(fl, text="Legal", font=('Arial', 10, 'bold'), text_color="grey").pack(anchor='w', padx=5)
    
    # Grid in Legal
    fl_grid = ctk.CTkFrame(fl, fg_color="transparent")
    fl_grid.pack(fill='x', padx=5, pady=5)
    
    # Cartera
    ctk.CTkCheckBox(fl_grid, text="Cartera", variable=var_cartera, text_color="black", width=20).grid(row=0, column=0, sticky='w')
    lbl_dolar_cartera = ctk.CTkLabel(fl_grid, text="($)", text_color="black")
    lbl_dolar_cartera.grid(row=0, column=1)
    e_val_cartera = crear_entry(fl_grid, width=80)
    e_val_cartera.grid(row=0, column=2, padx=5)
    e_val_cartera.bind('<FocusOut>', on_focus_out_moneda); e_val_cartera.bind('<FocusIn>', on_focus_in_moneda); e_val_cartera.bind('<Return>', saltar_campo) 
    lbl_dolar_cartera.grid_remove(); e_val_cartera.grid_remove()

    # Demanda
    ctk.CTkCheckBox(fl_grid, text="Demanda", variable=var_demanda, text_color="black", width=20).grid(row=1, column=0, sticky='w')
    lbl_dolar_demanda = ctk.CTkLabel(fl_grid, text="($)", text_color="black")
    lbl_dolar_demanda.grid(row=1, column=1)
    e_val_demanda = crear_entry(fl_grid, width=80)
    e_val_demanda.grid(row=1, column=2, padx=5)
    e_val_demanda.bind('<FocusOut>', on_focus_out_moneda); e_val_demanda.bind('<FocusIn>', on_focus_in_moneda); e_val_demanda.bind('<Return>', saltar_campo)
    lbl_dolar_demanda.grid_remove(); e_val_demanda.grid_remove()
    
    # Justicia
    ctk.CTkCheckBox(fl_grid, text="Justicia", variable=var_justicia, text_color="black", width=20).grid(row=2, column=0, sticky='w')
    e_det_justicia = crear_entry(fl_grid, width=100)
    e_det_justicia.grid(row=2, column=1, columnspan=2, padx=5)
    e_det_justicia.bind('<Return>', saltar_campo)
    e_det_justicia.grid_remove()

    # Buttons
    f_btns = ctk.CTkFrame(f_form, fg_color="transparent")
    f_btns.grid(row=1, column=0, columnspan=4, pady=10)
    
    # Botones con estilo
    btn_cancelar = ctk.CTkButton(f_btns, text="Cancelar", command=limpiar_campos_ui, fg_color="#d9534f", hover_color="#c9302c")
    btn_cancelar.pack(side='left', padx=10)
    
    btn_accion = ctk.CTkButton(f_btns, text="💾 Guardar Nuevo", command=accion_guardar, fg_color=COLOR_BTN_BG, hover_color=COLOR_BTN_HOVER)
    btn_accion.pack(side='left', padx=10)
    
    btn_eliminar = ctk.CTkButton(f_btns, text="🗑 Eliminar", command=eliminar_cliente, fg_color="#d9534f", hover_color="#c9302c", state="disabled")
    if NIVEL_ACCESO == 1: btn_eliminar.pack(side='left', padx=10)

    # Logo
    try:
        img = Image.open("Logo Face.jpg")
        logo_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(225, 210))
        lbl = ctk.CTkLabel(top_frame, image=logo_ctk, text="")
        lbl.place(relx=1.0, x=-20, y=10, anchor='ne') # Absolute positioning for logo
    except Exception as e: 
        print(f"Error logo: {e}")
        ctk.CTkLabel(top_frame, text="LOGO", text_color="grey").place(relx=1.0, x=-20, y=10, anchor='ne')

    # --- LISTA ---
    # Container for Treeview
    mid = ctk.CTkFrame(app, fg_color=COLOR_FONDO)
    mid.pack(fill='both', expand=True, padx=10, pady=5)
    
    fb = ctk.CTkFrame(mid, fg_color="transparent")
    fb.pack(fill='x', pady=5)
    ctk.CTkLabel(fb, text="Buscar:", text_color="black").pack(side='left')
    e_busqueda = crear_entry(fb)
    e_busqueda.pack(side='left', fill='x', expand=True, padx=5)
    # Busqueda automatica al escribir o con boton
    ctk.CTkButton(fb, text="🔎", width=50, command=filtrar_clientes, fg_color=COLOR_BTN_BG).pack(side='left')
    e_busqueda.bind('<KeyRelease>', lambda e: filtrar_clientes())

    ft = ctk.CTkFrame(mid, fg_color="white")
    ft.pack(fill='both', expand=True)

    # CAMBIADO NOMBRE DE COLUMNA CARPETA POR N. APERTURA
    cols = ("ID", "Cédula", "Nombre", "Teléfono", "Ingresos ($)", "Sit. Financiera", "Producto", "N. Apertura", "Asesor")
    tree = ttk.Treeview(ft, columns=cols, show='headings')
    
    # Scrollbar
    sy = ttk.Scrollbar(ft, orient='vertical', command=tree.yview)
    sy.pack(side='right', fill='y')
    tree.configure(yscrollcommand=sy.set)
    tree.pack(fill='both', expand=True)

    tree.heading("ID", text="ID"); tree.column("ID", width=30)
    tree.heading("Cédula", text="Cédula"); tree.column("Cédula", width=80)
    tree.heading("Nombre", text="Nombres y Apellidos"); tree.column("Nombre", width=200)
    tree.heading("Teléfono", text="Teléfono"); tree.column("Teléfono", width=80)
    tree.heading("Ingresos ($)", text="Ingresos ($)"); tree.column("Ingresos ($)", width=90)
    tree.heading("Sit. Financiera", text="Sit. Financiera"); tree.column("Sit. Financiera", width=90)
    tree.heading("Producto", text="Producto"); tree.column("Producto", width=100)
    tree.heading("N. Apertura", text="N. Apertura"); tree.column("N. Apertura", width=80)
    tree.heading("Asesor", text="Asesor"); tree.column("Asesor", width=80)

    tree.bind("<Double-1>", cargar_seleccion)
    mostrar_datos_tree()
    mostrar_datos_tree()
    # app.mainloop() # Ya no es mainloop principal


# --- MÓDULO MICROCRÉDITO ---
import webbrowser

def abrir_modulo_microcredito():
    global win_micro, e_cedula_micro, e_ruc_micro, e_nombre_micro, t_obs_micro
    global e_m_ref1_rel, e_m_ref1_tiempo, e_m_ref1_dir, c_m_ref1_viv, e_m_ref1_cargas, c_m_ref1_resp
    global e_m_ref2_rel, e_m_ref2_tiempo, e_m_ref2_dir, c_m_ref2_viv, e_m_ref2_cargas, c_m_ref2_resp
    global e_m_ref1_nom, e_m_ref1_tel, e_m_ref1_fec, e_m_ref1_hor
    global e_m_ref2_nom, e_m_ref2_tel, e_m_ref2_fec, e_m_ref2_hor
    global cedula_micro_actual, id_micro_actual
    global var_m_ref1_vehiculo, var_m_ref1_casa, var_m_ref1_terreno, var_m_ref1_inver
    global var_m_ref2_vehiculo, var_m_ref2_casa, var_m_ref2_terreno, var_m_ref2_inver
    global e_n_apertura_micro, e_val_apertura_micro, e_f_apertura_micro
    global e_fecha_visita, e_mapa_direccion
    global e_info_dir, e_info_civil, e_info_cargas, e_info_ing1, e_info_ing2, e_info_egr, lbl_info_total
    global e_info_casa, e_info_terr, e_info_local, e_info_cart, e_info_dem, e_info_just
    global t_obs_info_micro

    cedula_micro_actual = None
    id_micro_actual = None

    win_micro = ctk.CTkToplevel()
    win_micro.title("Módulo de Microcrédito")
    win_micro.geometry("1100x750")
    win_micro.after(100, lambda: win_micro.state('zoomed'))

    COLOR_FONDO = "#FAFAD2"
    win_micro.configure(fg_color=COLOR_FONDO)
    
    # Barra superior
    nav_frame = ctk.CTkFrame(win_micro, fg_color=COLOR_FONDO, height=40)
    nav_frame.pack(side='top', fill='x', pady=(5,0))
    
    # Logo removed from navigation frame

    ctk.CTkButton(nav_frame, text="Volver al Menú", command=win_micro.destroy, 
                  fg_color=COLOR_FONDO, text_color="#d9534f", hover_color="#EEE8AA", 
                  font=('Arial', 12, 'bold')).pack(side='right', padx=10)
    
    ctk.CTkLabel(win_micro, text="GESTIÓN DE MICROCRÉDITO", text_color="#1860C3", font=('Arial', 16, 'bold')).pack(pady=10)

    # Frame principal dividido
    main_frame = ctk.CTkFrame(win_micro, fg_color=COLOR_FONDO)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # LEFT PANEL (Content)
    left_panel = ctk.CTkFrame(main_frame, fg_color="transparent") # Transparent wrapper
    left_panel.pack(side='left', fill='both', expand=True, padx=(0, 20))

    # SECCIÓN BÚSQUEDA (Arriba) - Using helper internal frame for layout
    search_frame = ctk.CTkFrame(left_panel, fg_color="white", border_width=1, border_color="grey")
    search_frame.pack(fill='x', pady=(0,10))
    ctk.CTkLabel(search_frame, text=" Datos del Cliente ", text_color="grey", font=('Arial', 10, 'bold')).place(x=10, y=-8) # Faux LabelFrame Title
    
    # Padding internal container
    sf_in = ctk.CTkFrame(search_frame, fg_color="transparent")
    sf_in.pack(fill='x', padx=10, pady=15)
    
    ctk.CTkLabel(sf_in, text="Cédula:", text_color="black").pack(side='left')
    e_cedula_micro = ctk.CTkEntry(sf_in, width=150, fg_color="white", text_color="black", border_color="grey")
    e_cedula_micro.pack(side='left', padx=5)
    e_cedula_micro.bind('<KeyRelease>', buscar_micro_auto)
    
    ctk.CTkLabel(sf_in, text="RUC:", text_color="black").pack(side='left', padx=(15,0))
    e_ruc_micro = ctk.CTkEntry(sf_in, width=150, fg_color="white", text_color="black", border_color="grey")
    e_ruc_micro.pack(side='left', padx=5)
    e_ruc_micro.bind('<KeyRelease>', buscar_micro_auto)

    ctk.CTkLabel(sf_in, text="Cliente:", text_color="black").pack(side='left', padx=(15,0))
    e_nombre_micro = ctk.CTkEntry(sf_in, width=350, fg_color="white", text_color="black", border_color="grey")
    e_nombre_micro.pack(side='left', padx=5)
    e_nombre_micro.bind('<KeyRelease>', buscar_micro_auto)

    # NOTEBOOK (Pestañas) -> CTkTabview
    # Estilo mejorado: Botones más grandes, colores más vivos
    nb = ctk.CTkTabview(left_panel, width=1000, height=600, 
                        fg_color="white",  # Fondo del contenido de la pestaña (blanco para contraste)
                        segmented_button_fg_color="#E0E0E0", # Fondo de la barra de pestañas
                        segmented_button_selected_color="#1860C3", # Color seleccionado
                        segmented_button_selected_hover_color="#1452A6",
                        segmented_button_unselected_color="white", # Color no seleccionado
                        segmented_button_unselected_hover_color="#EEE",
                        text_color="grey",
                        text_color_disabled="grey",
                        corner_radius=10,
                        border_width=1,
                        border_color="#CCCCCC"
                        )
    nb.pack(fill='both', expand=True)

    # ... (Tabs content defined below but nb structure is here) ...
    # We must ensure tab content is added to 'nb' which is now in 'left_panel'

    # --- RIGHT PANEL (Logo) ---
    try:
        img = Image.open("Logo Face.jpg")
        # Match size from Documentos module (225x210 in that snippet)
        logo_micro = ctk.CTkImage(light_image=img, dark_image=img, size=(225, 210))
        lbl = ctk.CTkLabel(main_frame, image=logo_micro, text="")
        lbl.pack(side='right', padx=20, anchor='n')
    except: 
        ctk.CTkLabel(main_frame, text="LOGO", text_color="grey").pack(side='right', padx=20, anchor='n')

    # --- PESTAÑA 1: INFORMACIÓN ---
    nb.add("Información")
    tab_info = nb.tab("Información")
    
    # ... (Existing tab construction continues) ...

    # ctk Tabs act like frames, no need to add separate frame if not needed, but code structure uses grid on tab_info
    
    # Grid layout for Info
    ctk.CTkLabel(tab_info, text="Información Relevante del Cliente", text_color="#1860C3", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,20), sticky='w')
    
    ctk.CTkLabel(tab_info, text="N. de Apertura (Carpeta):", text_color="black").grid(row=1, column=0, sticky='w', pady=5)
    e_n_apertura_micro = ctk.CTkEntry(tab_info, width=150, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_n_apertura_micro.grid(row=1, column=1, sticky='w', padx=10)
    
    ctk.CTkLabel(tab_info, text="Valor de Apertura ($):", text_color="black").grid(row=2, column=0, sticky='w', pady=5)
    e_val_apertura_micro = ctk.CTkEntry(tab_info, width=150, fg_color="white", text_color="black", border_color="grey")
    e_val_apertura_micro.grid(row=2, column=1, sticky='w', padx=10)
    e_val_apertura_micro.bind('<FocusOut>', on_focus_out_moneda)
    e_val_apertura_micro.bind('<FocusIn>', on_focus_in_moneda)
    
    ctk.CTkLabel(tab_info, text="Fecha de Apertura:", text_color="black").grid(row=3, column=0, sticky='w', pady=5)
    e_f_apertura_micro = ctk.CTkEntry(tab_info, width=150, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey") # Readonly
    e_f_apertura_micro.grid(row=3, column=1, sticky='w', padx=10)

    # NUEVOS CAMPOS INFORMACIÓN CLIENTE (Solo Lectura)
    row_idx = 4
    ctk.CTkLabel(tab_info, text="Dirección:", text_color="black").grid(row=row_idx, column=0, sticky='w', pady=5)
    e_info_dir = ctk.CTkEntry(tab_info, width=350, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_dir.grid(row=row_idx, column=1, sticky='w', padx=10, columnspan=2)
    
    row_idx += 1
    ctk.CTkLabel(tab_info, text="Estado Civil:", text_color="black").grid(row=row_idx, column=0, sticky='w', pady=5)
    e_info_civil = ctk.CTkEntry(tab_info, width=150, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_civil.grid(row=row_idx, column=1, sticky='w', padx=10)
    
    ctk.CTkLabel(tab_info, text="Cargas:", text_color="black").grid(row=row_idx, column=2, sticky='w', pady=5)
    e_info_cargas = ctk.CTkEntry(tab_info, width=80, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_cargas.grid(row=row_idx, column=3, sticky='w', padx=10)

    row_idx += 1
    ctk.CTkLabel(tab_info, text="Ingresos 1 / Fuente:", text_color="black").grid(row=row_idx, column=0, sticky='w', pady=5)
    e_info_ing1 = ctk.CTkEntry(tab_info, width=250, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_ing1.grid(row=row_idx, column=1, sticky='w', padx=10, columnspan=2)

    row_idx += 1
    ctk.CTkLabel(tab_info, text="Ingresos 2 / Fuente:", text_color="black").grid(row=row_idx, column=0, sticky='w', pady=5)
    e_info_ing2 = ctk.CTkEntry(tab_info, width=250, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_ing2.grid(row=row_idx, column=1, sticky='w', padx=10, columnspan=2)

    row_idx += 1
    ctk.CTkLabel(tab_info, text="Egresos:", text_color="black").grid(row=row_idx, column=0, sticky='w', pady=5)
    e_info_egr = ctk.CTkEntry(tab_info, width=150, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_egr.grid(row=row_idx, column=1, sticky='w', padx=10)
    
    ctk.CTkLabel(tab_info, text="Total Disponible:", text_color="black", font=('Arial', 10, 'bold')).grid(row=row_idx, column=2, sticky='w', pady=5)
    lbl_info_total = ctk.CTkLabel(tab_info, text="$ 0.00", text_color="green", font=('Arial', 10, 'bold'))
    lbl_info_total.grid(row=row_idx, column=3, sticky='w', padx=10)

    # PATRIMONIO
    row_idx += 1
    ctk.CTkLabel(tab_info, text="PATRIMONIO", text_color="#1860C3", font=('Arial', 11, 'bold')).grid(row=row_idx, column=0, sticky='w', pady=(10,5))

    row_idx += 1
    ctk.CTkLabel(tab_info, text="Casa (Val/Hip):", text_color="black").grid(row=row_idx, column=0, sticky='w', pady=2)
    e_info_casa = ctk.CTkEntry(tab_info, width=200, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_casa.grid(row=row_idx, column=1, sticky='w', padx=10, columnspan=2)

    row_idx += 1
    ctk.CTkLabel(tab_info, text="Terreno (Val/Hip):", text_color="black").grid(row=row_idx, column=0, sticky='w', pady=2)
    e_info_terr = ctk.CTkEntry(tab_info, width=200, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_terr.grid(row=row_idx, column=1, sticky='w', padx=10, columnspan=2)

    row_idx += 1
    ctk.CTkLabel(tab_info, text="Local (Val/Hip):", text_color="black").grid(row=row_idx, column=0, sticky='w', pady=2)
    e_info_local = ctk.CTkEntry(tab_info, width=200, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_local.grid(row=row_idx, column=1, sticky='w', padx=10, columnspan=2)

    # LEGAL
    row_idx = 4 # Start second column of fields? No, let's keep it vertical or split. 
    # Actually, grid column 4 and 5 for legal might be better if there is space.
    # The window is zoomed, so we have space.
    
    ctk.CTkLabel(tab_info, text="HISTORIAL LEGAL", text_color="#1860C3", font=('Arial', 11, 'bold')).grid(row=row_idx, column=4, sticky='w', pady=(0,5), padx=(40,0))
    
    row_idx += 1
    ctk.CTkLabel(tab_info, text="Cartera (Cast/Val):", text_color="black").grid(row=row_idx, column=4, sticky='w', pady=2, padx=(40,0))
    e_info_cart = ctk.CTkEntry(tab_info, width=200, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_cart.grid(row=row_idx, column=5, sticky='w', padx=10)

    row_idx += 1
    ctk.CTkLabel(tab_info, text="Demanda (Jud/Val):", text_color="black").grid(row=row_idx, column=4, sticky='w', pady=2, padx=(40,0))
    e_info_dem = ctk.CTkEntry(tab_info, width=200, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_dem.grid(row=row_idx, column=5, sticky='w', padx=10)

    row_idx += 1
    ctk.CTkLabel(tab_info, text="Justicia (Prob/Det):", text_color="black").grid(row=row_idx, column=4, sticky='w', pady=2, padx=(40,0))
    e_info_just = ctk.CTkEntry(tab_info, width=200, fg_color="#F0F0F0", text_color="black", state='readonly', border_color="grey")
    e_info_just.grid(row=row_idx, column=5, sticky='w', padx=10)

    # OBSERVACIONES ESPECÍFICAS
    row_idx += 2
    ctk.CTkLabel(tab_info, text="Observaciones Específicas:", text_color="#1860C3", font=('Arial', 11, 'bold')).grid(row=row_idx, column=4, sticky='w', pady=(10,0), padx=(40,0))
    row_idx += 1
    # 1.5 cm high x 4.5 cm wide aprox. 1cm ~ 38px. 1.5cm ~ 57px, 4.5cm ~ 170px.
    # Let's make it a bit bigger for usability but keeping proportions.
    t_obs_info_micro = ctk.CTkTextbox(tab_info, height=60, width=250, fg_color="white", text_color="black", border_color="grey", border_width=1)
    t_obs_info_micro.grid(row=row_idx, column=4, columnspan=2, sticky='w', pady=5, padx=(40,0))


    # --- PESTAÑA 2: LLAMADAS ---
    nb.add("Llamadas")
    tab_llamadas = nb.tab("Llamadas")

    # Reuse existing reference logic but place in tab_llamadas
    refs_container = ctk.CTkFrame(tab_llamadas, fg_color="transparent")
    refs_container.pack(fill='both', expand=True)

    def create_ref_group(parent, title, col):
        f = ctk.CTkFrame(parent, fg_color="white", border_width=1, border_color="grey")
        f.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(f, text=title, text_color="grey", font=('Arial', 10, 'bold')).pack(anchor='w', padx=5, pady=2)
        
        # Grid content for compactness
        f_grid = ctk.CTkFrame(f, fg_color="transparent")
        f_grid.pack(fill='both', expand=True, padx=5, pady=2)
        f_grid.grid_columnconfigure(1, weight=1)
        
        row = 0
        ctk.CTkLabel(f_grid, text="Nombre Ref.:", text_color="black", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        e_nom = ctk.CTkEntry(f_grid, height=25, fg_color="white", text_color="black", border_color="grey", font=('Arial', 11)); e_nom.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        
        row += 1
        ctk.CTkLabel(f_grid, text="Teléfono:", text_color="black", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        e_tel = ctk.CTkEntry(f_grid, height=25, fg_color="white", text_color="black", border_color="grey", font=('Arial', 11)); e_tel.grid(row=row, column=1, sticky='ew', padx=5, pady=2)

        row += 1
        ctk.CTkLabel(f_grid, text="Fecha:", text_color="black", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        e_fec = ctk.CTkEntry(f_grid, height=25, width=100, fg_color="white", text_color="black", border_color="grey", font=('Arial', 11)); e_fec.grid(row=row, column=1, sticky='w', padx=5, pady=2)
        # Set default date
        e_fec.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))

        row += 1
        ctk.CTkLabel(f_grid, text="Hora:", text_color="black", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        e_hor = ctk.CTkEntry(f_grid, height=25, width=100, fg_color="white", text_color="black", border_color="grey", font=('Arial', 11)); e_hor.grid(row=row, column=1, sticky='w', padx=5, pady=2)
        # Set default time
        e_hor.insert(0, datetime.datetime.now().strftime("%H:%M"))

        row += 1
        ctk.CTkLabel(f_grid, text="1. Relación:", text_color="black", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        e_rel = ctk.CTkEntry(f_grid, height=25, fg_color="white", text_color="black", border_color="grey", font=('Arial', 11)); e_rel.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        
        row += 1
        ctk.CTkLabel(f_grid, text="2. Tiempo:", text_color="black", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        e_tiempo = ctk.CTkEntry(f_grid, height=25, fg_color="white", text_color="black", border_color="grey", font=('Arial', 11)); e_tiempo.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        
        row += 1
        ctk.CTkLabel(f_grid, text="3. Dirección:", text_color="black", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        e_dir = ctk.CTkEntry(f_grid, height=25, fg_color="white", text_color="black", border_color="grey", font=('Arial', 11)); e_dir.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        
        row += 1
        ctk.CTkLabel(f_grid, text="4. Vivienda:", text_color="black", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        c_viv = ctk.CTkComboBox(f_grid, height=25, values=["Arrendada", "Familiar", "Propia"], fg_color="white", text_color="black", border_color="grey", button_color="#1860C3", font=('Arial', 11))
        c_viv.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        
        row += 1
        ctk.CTkLabel(f_grid, text="5. Cargas:", text_color="black", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        e_cargas = ctk.CTkEntry(f_grid, height=25, fg_color="white", text_color="black", border_color="grey", font=('Arial', 11)); e_cargas.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        
        row += 1
        ctk.CTkLabel(f_grid, text="6. Patrimonio:", text_color="black", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        f_pat = ctk.CTkFrame(f_grid, fg_color="transparent")
        f_pat.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        
        v_veh = tk.IntVar(); v_casa = tk.IntVar(); v_terr = tk.IntVar(); v_inv = tk.IntVar()
        # Compact checkbuttons
        ctk.CTkCheckBox(f_pat, text="Veh.", variable=v_veh, text_color="black", height=20, width=50, checkbox_width=18, checkbox_height=18, font=('Arial', 9)).grid(row=0, column=0, sticky='w')
        ctk.CTkCheckBox(f_pat, text="Casa", variable=v_casa, text_color="black", height=20, width=50, checkbox_width=18, checkbox_height=18, font=('Arial', 9)).grid(row=0, column=1, sticky='w', padx=5)
        ctk.CTkCheckBox(f_pat, text="Terr.", variable=v_terr, text_color="black", height=20, width=50, checkbox_width=18, checkbox_height=18, font=('Arial', 9)).grid(row=1, column=0, sticky='w')
        ctk.CTkCheckBox(f_pat, text="Inv.", variable=v_inv, text_color="black", height=20, width=50, checkbox_width=18, checkbox_height=18, font=('Arial', 9)).grid(row=1, column=1, sticky='w', padx=5)
        
        row += 1
        ctk.CTkLabel(f_grid, text="7. R. Crédito:", text_color="black", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        c_resp = ctk.CTkComboBox(f_grid, height=25, values=["Si", "No"], fg_color="white", text_color="black", border_color="grey", button_color="#1860C3", font=('Arial', 11))
        c_resp.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        
        return e_nom, e_tel, e_fec, e_hor, e_rel, e_tiempo, e_dir, c_viv, e_cargas, (v_veh, v_casa, v_terr, v_inv), c_resp

    e_m_ref1_nom, e_m_ref1_tel, e_m_ref1_fec, e_m_ref1_hor, e_m_ref1_rel, e_m_ref1_tiempo, e_m_ref1_dir, c_m_ref1_viv, e_m_ref1_cargas, vars_pat1, c_m_ref1_resp = create_ref_group(refs_container, "Verificación Referencia 1", 0)
    var_m_ref1_vehiculo, var_m_ref1_casa, var_m_ref1_terreno, var_m_ref1_inver = vars_pat1

    e_m_ref2_nom, e_m_ref2_tel, e_m_ref2_fec, e_m_ref2_hor, e_m_ref2_rel, e_m_ref2_tiempo, e_m_ref2_dir, c_m_ref2_viv, e_m_ref2_cargas, vars_pat2, c_m_ref2_resp = create_ref_group(refs_container, "Verificación Referencia 2", 1)
    var_m_ref2_vehiculo, var_m_ref2_casa, var_m_ref2_terreno, var_m_ref2_inver = vars_pat2


    # --- PESTAÑA 3: VISITAS ---
    nb.add("Visitas")
    tab_visitas = nb.tab("Visitas")
    
    ctk.CTkLabel(tab_visitas, text="Agendar Visita / Ubicación", text_color="#1860C3", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0,10))
    
    fv = ctk.CTkFrame(tab_visitas, fg_color="transparent")
    fv.pack(fill='x', pady=5)
    ctk.CTkLabel(fv, text="Fecha de Visita:", text_color="black").pack(side='left')
    
    # DateEntry workaround: ctk doesn't have it. Use Entry with formatted text or keep tk wrapper.
    # We will use CTkEntry for consistency and user manually enters date or we assume similar behavior.
    # Integrating tkcalendar with ctk is tricky due to visual mismatch. Let's use CTkEntry.
    e_fecha_visita = ctk.CTkEntry(fv, width=150, fg_color="white", text_color="black", border_color="grey")
    e_fecha_visita.pack(side='left', padx=10)
    e_fecha_visita.insert(0, "DD/MM/YYYY")
    
    fm = ctk.CTkFrame(tab_visitas, fg_color="transparent")
    fm.pack(fill='x', pady=20)
    ctk.CTkLabel(fm, text="Dirección para Mapa:", text_color="black").pack(side='left')
    e_mapa_direccion = ctk.CTkEntry(fm, width=400, fg_color="white", text_color="black", border_color="grey")
    e_mapa_direccion.pack(side='left', padx=10)
    
    def abrir_mapa():
        d = e_mapa_direccion.get().strip()
        if d:
            webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={d}")
        else:
            messagebox.showinfo("Mapa", "Ingrese una dirección para buscar.")

    ctk.CTkButton(fm, text="🗺️ Ver en Google Maps", command=abrir_mapa, fg_color="#465EA6", hover_color="#1860C3").pack(side='left', padx=10)


    # --- PESTAÑA 4: RECORDATORIOS ---
    nb.add("Recordatorios")
    tab_recordatorios = nb.tab("Recordatorios")
    
    ctk.CTkLabel(tab_recordatorios, text="Notas y Recordatorios", text_color="#1860C3", font=('Arial', 12, 'bold')).pack(anchor='w')
    # CustomTkinter has CTkTextbox
    t_obs_micro = ctk.CTkTextbox(tab_recordatorios, height=200, width=600, fg_color="white", text_color="black", border_color="grey", border_width=1)
    t_obs_micro.pack(fill='both', expand=True, pady=10)


    # Botonera General (Fuera del Notebook)
    btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    btn_frame.pack(pady=10)
    ctk.CTkButton(btn_frame, text="💾 Guardar / Actualizar Todo", command=guardar_microcredito, fg_color="#465EA6", hover_color="#1860C3", font=('Arial', 12, 'bold'), width=200, height=40).pack()

    # Secondary logo block removed


def get_patrimonio_str(v_veh, v_casa, v_terr, v_inv):
    p = []
    if v_veh.get(): p.append("Vehiculo")
    if v_casa.get(): p.append("Casa o Dep")
    if v_terr.get(): p.append("Terreno")
    if v_inv.get(): p.append("Inversiones")
    return ",".join(p)

def set_patrimonio_check(s, v_veh, v_casa, v_terr, v_inv):
    v_veh.set(0); v_casa.set(0); v_terr.set(0); v_inv.set(0)
    if not s: return
    parts = s.split(',')
    if "Vehiculo" in parts: v_veh.set(1)
    if "Casa o Dep" in parts: v_casa.set(1)
    if "Terreno" in parts: v_terr.set(1)
    if "Inversiones" in parts: v_inv.set(1)

def limpiar_form_micro():
    for e in [e_ruc_micro, e_nombre_micro, e_m_ref1_rel, e_m_ref1_tiempo, e_m_ref1_dir, e_m_ref1_cargas,
              e_m_ref2_rel, e_m_ref2_tiempo, e_m_ref2_dir, e_m_ref2_cargas,
              e_m_ref1_nom, e_m_ref1_tel, e_m_ref1_fec, e_m_ref1_hor,
              e_m_ref2_nom, e_m_ref2_tel, e_m_ref2_fec, e_m_ref2_hor]:
        try:
            e.configure(state='normal')
            e.delete(0, tk.END)
        except: pass
    
    t_obs_micro.delete("1.0", tk.END)
    t_obs_info_micro.delete("1.0", tk.END)
    
    # Limpiar Info tabs
    if 'e_n_apertura_micro' in globals():
        for e in [e_n_apertura_micro, e_f_apertura_micro, e_info_dir, e_info_civil, e_info_cargas, e_info_ing1, e_info_ing2, e_info_egr, e_info_casa, e_info_terr, e_info_local, e_info_cart, e_info_dem, e_info_just]:
            try:
                e.configure(state='normal')
                e.delete(0, tk.END)
                if e != e_val_apertura_micro: e.configure(state='readonly')
            except: pass
        
        e_val_apertura_micro.delete(0, tk.END)
        lbl_info_total.configure(text="$ 0.00")
    
    if 'e_mapa_direccion' in globals(): 
        e_mapa_direccion.delete(0, tk.END)
    # DateEntry reset?
    # if 'e_fecha_visita' in globals(): ...


def buscar_micro_auto(event=None):
    global cedula_micro_actual, id_micro_actual
    
    ced = e_cedula_micro.get().strip()
    ruc = e_ruc_micro.get().strip()
    nom = e_nombre_micro.get().strip()
    
    criteria = None
    val = None
    
    # Determine search criteria based on valid input
    if len(ced) == 10 and ced.isdigit():
        criteria = "cedula"
        val = ced
    elif len(ruc) >= 10 and ruc.isdigit():
         criteria = "ruc"
         val = ruc
    elif len(nom) >= 3:
         criteria = "nombre"
         val = nom
    
    if not criteria:
        return

    conn, cursor = conectar_db()
    
    res = None
    # Fetch result based on criteria
    # Including 'cedula' in SELECT to ensure we can load linked data
    # res fields: 0:cedula, 1:nombre, 2:ruc, 3:carpeta, 4:val_ape, 5:fecha_ape, 6:dir, 7:civil, 8:cargas, 9:ing1, 10:f1, 11:ing2, 12:f2, 13:egr, 14:total, 
    # 15:casa, 16:val_casa, 17:hip_casa, 18:terr, 19:val_terr, 20:hip_terr, 21:loc, 22:val_loc, 23:hip_loc,
    # 24:cart, 25:v_cart, 26:dem, 27:v_dem, 28:prob, 29:det
    
    query = """
        SELECT cedula, nombre, ruc, numero_carpeta, valor_apertura, apertura, direccion, 
               estado_civil, cargas_familiares, ingresos_mensuales, fuente_ingreso, ingresos_mensuales_2, fuente_ingreso_2, egresos, total_disponible, 
               casa_dep, valor_casa_dep, hipotecado_casa_dep, terreno, valor_terreno, hipotecado, local, valor_local, hipotecado_local,
               "cartera castigada", "valor cartera", "demanda judicial", "valor demanda", "problemas justicia", "detalle justicia"
        FROM Clientes 
    """
    
    if criteria == "cedula":
         cursor.execute(query + " WHERE cedula = ?", (val,))
         res = cursor.fetchone()
    elif criteria == "ruc":
         cursor.execute(query + " WHERE ruc = ?", (val,))
         res = cursor.fetchone()
    elif criteria == "nombre":
         cursor.execute(query + " WHERE nombre LIKE ? LIMIT 1", (f"%{val}%",))
         res = cursor.fetchone()
    
    conn.close()
    
    if res:
        # Avoid overwriting the active field to allow fluid typing
        widget = event.widget if event else None
        
        # res fields: 0:cedula, 1:nombre, 2:ruc, 3:carpeta, 4:val_ape, 5:fecha_ape, 6:dir, 7:civil, 8:cargas, 9:ing1, 10:f1, 11:ing2, 12:f2, 13:egr, 14:total, 
        # 15:casa, 16:val_casa, 17:hip_casa, 18:terr, 19:val_terr, 20:hip_terr, 21:loc, 22:val_loc, 23:hip_loc,
        # 24:cart, 25:v_cart, 26:dem, 27:v_dem, 28:prob, 29:det
        
        if criteria != "nombre" or (widget != e_nombre_micro):
            e_nombre_micro.delete(0, tk.END); e_nombre_micro.insert(0, res[1] if res[1] else "")
            
        if criteria != "ruc" or (widget != e_ruc_micro):
            e_ruc_micro.delete(0, tk.END); 
            if res[2]: e_ruc_micro.insert(0, res[2])

        if criteria != "cedula" or (widget != e_cedula_micro):
            e_cedula_micro.delete(0, tk.END); e_cedula_micro.insert(0, res[0])
        
        # Populate Info Tab (Existing)
        for e in [e_n_apertura_micro, e_f_apertura_micro]: e.configure(state='normal'); e.delete(0, tk.END)
        if res[3]: e_n_apertura_micro.insert(0, res[3])
        if res[5]: e_f_apertura_micro.insert(0, res[5])
        for e in [e_n_apertura_micro, e_f_apertura_micro]: e.configure(state='readonly')
        
        e_val_apertura_micro.delete(0, tk.END)
        if res[4]: e_val_apertura_micro.insert(0, formatear_float_str(res[4]))
        
        # Populate New Info Fields
        for e in [e_info_dir, e_info_civil, e_info_cargas, e_info_ing1, e_info_ing2, e_info_egr, e_info_casa, e_info_terr, e_info_local, e_info_cart, e_info_dem, e_info_just]:
            e.configure(state='normal'); e.delete(0, tk.END)

        if res[6]: e_info_dir.insert(0, res[6])
        if res[7]: e_info_civil.insert(0, res[7])
        if res[8]: e_info_cargas.insert(0, str(res[8]))
        
        ing1_str = f"{formatear_float_str(res[9] or 0)} / {res[10] or ''}"
        e_info_ing1.insert(0, ing1_str)
        
        ing2_str = f"{formatear_float_str(res[11] or 0)} / {res[12] or ''}"
        e_info_ing2.insert(0, ing2_str)
        
        if res[13]: e_info_egr.insert(0, formatear_float_str(res[13]))
        lbl_info_total.configure(text="$ " + formatear_float_str(res[14] or 0))

        # Patrimonio
        casa_str = f"{'Si' if res[15] else 'No'} ({formatear_float_str(res[16] or 0)} / {res[17] or 'No'})"
        e_info_casa.insert(0, casa_str)
        terr_str = f"{'Si' if res[18] else 'No'} ({formatear_float_str(res[19] or 0)} / {res[20] or 'No'})"
        e_info_terr.insert(0, terr_str)
        loc_str = f"{'Si' if res[21] else 'No'} ({formatear_float_str(res[22] or 0)} / {res[23] or 'No'})"
        e_info_local.insert(0, loc_str)

        # Legal
        cart_str = f"{'Si' if res[24] else 'No'} ({formatear_float_str(res[25] or 0)})"
        e_info_cart.insert(0, cart_str)
        dem_str = f"{'Si' if res[26] else 'No'} ({formatear_float_str(res[27] or 0)})"
        e_info_dem.insert(0, dem_str)
        just_str = f"{'Si' if res[28] else 'No'} ({res[29] or ''})"
        e_info_just.insert(0, just_str)

        for e in [e_info_dir, e_info_civil, e_info_cargas, e_info_ing1, e_info_ing2, e_info_egr, e_info_casa, e_info_terr, e_info_local, e_info_cart, e_info_dem, e_info_just]:
            e.configure(state='readonly')

        # Populate Map Address
        e_mapa_direccion.delete(0, tk.END)
        if res[6]: e_mapa_direccion.insert(0, res[6])
        
        cedula_micro_actual = res[0]
        cargar_datos_micro(cedula_micro_actual)
    else:
        # Not found
        # Do not clear fields while typing, just clear dependent data
        cedula_micro_actual = None
        id_micro_actual = None
        t_obs_micro.delete("1.0", tk.END)

def cargar_datos_micro(cedula):
    global id_micro_actual
    conn, cursor = conectar_db()
    cursor.execute("SELECT * FROM Microcreditos WHERE cedula_cliente = ?", (cedula,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        id_micro_actual = row[0]
        # row[1]=ced, row[2]=ruc, row[3]=obs, row[4]=obs_info
        t_obs_micro.delete("1.0", tk.END); t_obs_micro.insert("1.0", row[3] if row[3] else "")
        t_obs_info_micro.delete("1.0", tk.END); t_obs_info_micro.insert("1.0", row[4] if row[4] else "")
        
        # Refs starting from row[5] now... wait, let's check exact indexes.
        # Microcreditos table: id(0), ced(1), ruc(2), obs(3), obs_info(4), ref1_rel(5)...
        # Ref 1
        e_m_ref1_rel.delete(0,tk.END); e_m_ref1_rel.insert(0, row[5] if row[5] else "")
        e_m_ref1_tiempo.delete(0,tk.END); e_m_ref1_tiempo.insert(0, row[6] if row[6] else "")
        e_m_ref1_dir.delete(0,tk.END); e_m_ref1_dir.insert(0, row[7] if row[7] else "")
        c_m_ref1_viv.set(row[8] if row[8] else "")
        e_m_ref1_cargas.delete(0,tk.END); e_m_ref1_cargas.insert(0, row[9] if row[9] else "")
        set_patrimonio_check(row[10] if row[10] else "", var_m_ref1_vehiculo, var_m_ref1_casa, var_m_ref1_terreno, var_m_ref1_inver)
        c_m_ref1_resp.set(row[11] if row[11] else "")
        
        if len(row) > 19:
            e_m_ref1_fec.delete(0,tk.END); e_m_ref1_fec.insert(0, row[19] if row[19] else "")
            e_m_ref1_hor.delete(0,tk.END); e_m_ref1_hor.insert(0, row[20] if row[20] else "")
            e_m_ref1_nom.delete(0,tk.END); e_m_ref1_nom.insert(0, row[21] if row[21] else "")
            e_m_ref1_tel.delete(0,tk.END); e_m_ref1_tel.insert(0, row[22] if row[22] else "")

        # Ref 2
        e_m_ref2_rel.delete(0,tk.END); e_m_ref2_rel.insert(0, row[12] if row[12] else "")
        e_m_ref2_tiempo.delete(0,tk.END); e_m_ref2_tiempo.insert(0, row[13] if row[13] else "")
        e_m_ref2_dir.delete(0,tk.END); e_m_ref2_dir.insert(0, row[14] if row[14] else "")
        c_m_ref2_viv.set(row[15] if row[15] else "")
        e_m_ref2_cargas.delete(0,tk.END); e_m_ref2_cargas.insert(0, row[16] if row[16] else "")
        set_patrimonio_check(row[17] if row[17] else "", var_m_ref2_vehiculo, var_m_ref2_casa, var_m_ref2_terreno, var_m_ref2_inver)
        c_m_ref2_resp.set(row[18] if row[18] else "")

        if len(row) > 23:
            e_m_ref2_fec.delete(0,tk.END); e_m_ref2_fec.insert(0, row[23] if row[23] else "")
            e_m_ref2_hor.delete(0,tk.END); e_m_ref2_hor.insert(0, row[24] if row[24] else "")
            e_m_ref2_nom.delete(0,tk.END); e_m_ref2_nom.insert(0, row[25] if row[25] else "")
            e_m_ref2_tel.delete(0,tk.END); e_m_ref2_tel.insert(0, row[26] if row[26] else "")
    else:
        id_micro_actual = None
        # Limpiar formulario
        t_obs_micro.delete("1.0", tk.END)
        for e in [e_m_ref1_rel, e_m_ref1_tiempo, e_m_ref1_dir, e_m_ref1_cargas, e_m_ref2_rel, e_m_ref2_tiempo, e_m_ref2_dir, e_m_ref2_cargas]:
            e.delete(0, tk.END)
        for c in [c_m_ref1_viv, c_m_ref1_resp, c_m_ref2_viv, c_m_ref2_resp]: c.set('')
        set_patrimonio_check("", var_m_ref1_vehiculo, var_m_ref1_casa, var_m_ref1_terreno, var_m_ref1_inver)
        set_patrimonio_check("", var_m_ref2_vehiculo, var_m_ref2_casa, var_m_ref2_terreno, var_m_ref2_inver)

def guardar_microcredito():
    if not cedula_micro_actual:
        messagebox.showwarning("Aviso", "Busque un cliente primero.")
        return
        
    ruc = e_ruc_micro.get()
    obs = t_obs_micro.get("1.0", tk.END).strip()
    obs_info = t_obs_info_micro.get("1.0", tk.END).strip()
    
    pat1 = get_patrimonio_str(var_m_ref1_vehiculo, var_m_ref1_casa, var_m_ref1_terreno, var_m_ref1_inver)
    pat2 = get_patrimonio_str(var_m_ref2_vehiculo, var_m_ref2_casa, var_m_ref2_terreno, var_m_ref2_inver)
    
    # Save Valor Apertura to Clientes table
    val_apertura = limpiar_moneda(e_val_apertura_micro.get())
    
    vals = (
        cedula_micro_actual, ruc, obs, obs_info,
        e_m_ref1_rel.get(), e_m_ref1_tiempo.get(), e_m_ref1_dir.get(), c_m_ref1_viv.get(), e_m_ref1_cargas.get(), pat1, c_m_ref1_resp.get(),
        e_m_ref2_rel.get(), e_m_ref2_tiempo.get(), e_m_ref2_dir.get(), c_m_ref2_viv.get(), e_m_ref2_cargas.get(), pat2, c_m_ref2_resp.get(),
        e_m_ref1_fec.get(), e_m_ref1_hor.get(), e_m_ref1_nom.get(), e_m_ref1_tel.get(),
        e_m_ref2_fec.get(), e_m_ref2_hor.get(), e_m_ref2_nom.get(), e_m_ref2_tel.get()
    )
    
    conn, cursor = conectar_db()
    try:
        # Update Clientes table for valor_apertura
        cursor.execute("UPDATE Clientes SET valor_apertura = ? WHERE cedula = ?", (val_apertura, cedula_micro_actual))

        if id_micro_actual:
            # Update
            cursor.execute("""
                UPDATE Microcreditos SET 
                observaciones=?, observaciones_info=?,
                ref1_relacion=?, ref1_tiempo_conocer=?, ref1_direccion=?, ref1_tipo_vivienda=?, ref1_cargas=?, ref1_patrimonio=?, ref1_responsable=?,
                ref2_relacion=?, ref2_tiempo_conocer=?, ref2_direccion=?, ref2_tipo_vivienda=?, ref2_cargas=?, ref2_patrimonio=?, ref2_responsable=?,
                ref1_fecha=?, ref1_hora=?, ref1_nombre=?, ref1_telefono=?,
                ref2_fecha=?, ref2_hora=?, ref2_nombre=?, ref2_telefono=?
                WHERE id=?
            """, vals[2:] + (id_micro_actual,))
            msg = "Datos actualizados."
        else:
            # Insert
            cursor.execute("""
                INSERT INTO Microcreditos (
                    cedula_cliente, ruc, observaciones, observaciones_info,
                    ref1_relacion, ref1_tiempo_conocer, ref1_direccion, ref1_tipo_vivienda, ref1_cargas, ref1_patrimonio, ref1_responsable,
                    ref2_relacion, ref2_tiempo_conocer, ref2_direccion, ref2_tipo_vivienda, ref2_cargas, ref2_patrimonio, ref2_responsable,
                    ref1_fecha, ref1_hora, ref1_nombre, ref1_telefono,
                    ref2_fecha, ref2_hora, ref2_nombre, ref2_telefono
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, vals)
            msg = "Datos guardados."
            
        conn.commit()
        messagebox.showinfo("Éxito", msg)
        cargar_datos_micro(cedula_micro_actual) # Recargar para obtener ID si fue insert
    except Exception as e:
        messagebox.showerror("Error", f"Error DB: {e}")
    finally: conn.close()



# --- MÓDULOS NUEVOS (Structure) ---
def crear_modulo_generico(titulo, color_titulo="#1860C3"):
    win = ctk.CTkToplevel()
    win.title(titulo)
    win.geometry("1100x750")
    win.after(100, lambda: win.state('zoomed'))
    
    COLOR_FONDO = "#FAFAD2"
    win.configure(fg_color=COLOR_FONDO)
    
    nav_frame = ctk.CTkFrame(win, fg_color=COLOR_FONDO, height=40)
    nav_frame.pack(side='top', fill='x', pady=(5,0))
    
    # Logo in nav_frame (right) - REMOVED
    # try:
    #     img = Image.open("Logo Face.jpg"); ...
    # except: pass

    ctk.CTkButton(nav_frame, text="Volver al Menú", command=win.destroy, 
                  fg_color=COLOR_FONDO, text_color="#d9534f", hover_color="#EEE8AA", 
                  font=('Arial', 12, 'bold')).pack(side='right', padx=10)
                  
    ctk.CTkLabel(win, text=titulo.upper(), text_color=color_titulo, font=('Arial', 16, 'bold')).pack(pady=10)
    
    # Frame principal
    main_frame = ctk.CTkFrame(win, fg_color=COLOR_FONDO)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Split Layout: Left Content, Right Logo
    left_panel = ctk.CTkFrame(main_frame, fg_color="transparent")
    left_panel.pack(side='left', fill='both', expand=True, padx=(0, 20))

    # Search Section (in Left Panel)
    search_frame = ctk.CTkFrame(left_panel, fg_color="white", border_width=1, border_color="grey")
    search_frame.pack(fill='x', pady=(0,10))
    ctk.CTkLabel(search_frame, text=" Datos del Cliente ", text_color="grey", font=('Arial', 10, 'bold')).place(x=10, y=-8)
    
    sf_in = ctk.CTkFrame(search_frame, fg_color="transparent")
    sf_in.pack(fill='x', padx=10, pady=15)
    
    ctk.CTkLabel(sf_in, text="Cédula:", text_color="black").pack(side='left')
    e_cedula = ctk.CTkEntry(sf_in, width=150, fg_color="white", text_color="black", border_color="grey")
    e_cedula.pack(side='left', padx=5)
    
    ctk.CTkLabel(sf_in, text="RUC:", text_color="black").pack(side='left', padx=(15,0))
    e_ruc = ctk.CTkEntry(sf_in, width=150, fg_color="white", text_color="black", border_color="grey")
    e_ruc.pack(side='left', padx=5)

    ctk.CTkLabel(sf_in, text="Cliente:", text_color="black").pack(side='left', padx=(15,0))
    e_nombre = ctk.CTkEntry(sf_in, width=350, fg_color="white", text_color="black", border_color="grey")
    e_nombre.pack(side='left', padx=5)
    
    # Generic Search Function
    def buscar_cliente_gen(event=None):
        ced = e_cedula.get().strip()
        ruc = e_ruc.get().strip()
        nom = e_nombre.get().strip()
        
        criteria = None
        val = None
        
        if len(ced) == 10 and ced.isdigit():
            criteria = "cedula"
            val = ced
        elif len(ruc) >= 10 and ruc.isdigit():
             criteria = "ruc"
             val = ruc
        elif len(nom) >= 3:
             criteria = "nombre"
             val = nom
        
        if not criteria: return

        conn, cursor = conectar_db()
        res = None
        
        if criteria == "cedula":
             cursor.execute("SELECT nombre, ruc, cedula FROM Clientes WHERE cedula = ?", (val,))
             res = cursor.fetchone()
        elif criteria == "ruc":
             cursor.execute("SELECT nombre, ruc, cedula FROM Clientes WHERE ruc = ?", (val,))
             res = cursor.fetchone()
        elif criteria == "nombre":
             cursor.execute("SELECT nombre, ruc, cedula FROM Clientes WHERE nombre LIKE ? LIMIT 1", (f"%{val}%",))
             res = cursor.fetchone()
             
        conn.close()
        
        if res:
            widget = event.widget if event else None
            
            # res: 0:nombre, 1:ruc, 2:cedula
            
            if criteria != "nombre" or (widget != e_nombre):
                e_nombre.delete(0, tk.END); e_nombre.insert(0, res[0]); 
                
            if criteria != "ruc" or (widget != e_ruc):
                e_ruc.delete(0, tk.END); 
                if res[1]: e_ruc.insert(0, res[1])

            if criteria != "cedula" or (widget != e_cedula):
                e_cedula.delete(0, tk.END); e_cedula.insert(0, res[2])
        else:
            # Optional: Clear fields if not found or keep typing
            pass

    e_cedula.bind('<KeyRelease>', buscar_cliente_gen)
    e_ruc.bind('<KeyRelease>', buscar_cliente_gen)
    e_nombre.bind('<KeyRelease>', buscar_cliente_gen)
    
    # Right Logo
    try:
        img = Image.open("Logo Face.jpg")
        logo_gen = ctk.CTkImage(light_image=img, dark_image=img, size=(225, 210))
        lbl = ctk.CTkLabel(main_frame, image=logo_gen, text="")
        lbl.pack(side='right', padx=20, anchor='n')
    except: 
        ctk.CTkLabel(main_frame, text="LOGO", text_color="grey").pack(side='right', padx=20, anchor='n')
    
    # Return container for module content (Left Panel)
    content_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
    content_frame.pack(fill='both', expand=True)
    
    return win, content_frame

def abrir_modulo_rehabilitacion():
    win, frame = crear_modulo_generico("Módulo de Rehabilitación")
    ctk.CTkLabel(frame, text="Contenido específico de Rehabilitación aquí...", text_color="grey", font=("Arial", 12)).pack(pady=50)

def abrir_modulo_intermediacion():
    win, frame = crear_modulo_generico("Módulo de Intermediación")
    ctk.CTkLabel(frame, text="Contenido específico de Intermediación aquí...", text_color="grey", font=("Arial", 12)).pack(pady=50)

def abrir_modulo_consultas():
    win, frame = crear_modulo_generico("Módulo de Consultas")
    ctk.CTkLabel(frame, text="Contenido específico de Consultas aquí...", text_color="grey", font=("Arial", 12)).pack(pady=50)

def abrir_modulo_cartera():
    win, frame = crear_modulo_generico("Módulo de Cartera")
    ctk.CTkLabel(frame, text="Contenido específico de Cartera aquí...", text_color="grey", font=("Arial", 12)).pack(pady=50)


if __name__ == '__main__':
    win = ctk.CTk()
    win.title("Login")
    win.geometry("300x250")
    
    # Centrar ventana login
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    w_width, w_height = 300, 250
    pos_x, pos_y = (screen_width - w_width) // 2, (screen_height - w_height) // 2
    win.geometry(f"{w_width}x{w_height}+{pos_x}+{pos_y}")
    
    ctk.CTkLabel(win, text="Usuario:", font=("Arial", 14)).pack(pady=(30, 5))
    u = ctk.CTkEntry(win)
    u.pack()
    
    # Focus logic tweak
    u.bind('<Return>', lambda e: p.focus())
    
    ctk.CTkLabel(win, text="Clave:", font=("Arial", 14)).pack(pady=5)
    p = ctk.CTkEntry(win, show="*")
    p.pack()
    
    # Pass 'win' as the app root to be reused
    p.bind('<Return>', lambda e: login_fn(win, u, p))
    
    ctk.CTkButton(win, text="Entrar", command=lambda: login_fn(win, u, p)).pack(pady=20)
    
    try:
         # win.iconbitmap("icono.ico") 
         pass
    except: pass
    
    win.mainloop()

