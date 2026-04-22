import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import datetime
import psycopg2

class AsesoresView(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, session_user):
        super().__init__(parent)
        self.db_manager = db_manager
        self.session_user = session_user
        
        self.title("Módulo Asesores - Ingreso Rápido Buró")
        self.geometry("500x650") # Height increased to fit simulator button
        self.resizable(False, False)
        
        # Center window
        self.transient(parent)
        self.grab_set()
        
        # Variables
        self.vars = {
            "cedula": ctk.StringVar(),
            "nombres": ctk.StringVar(),
            "fecha": ctk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d")),
            "imagen_ruta": ctk.StringVar()
        }
        
        self.image_bytes = None
        
        self.construir_ui()
        
    def construir_ui(self):
        title_lbl = ctk.CTkLabel(self, text="Registro Rápido de Buró", font=("Arial", 20, "bold"), text_color="#1860C3")
        title_lbl.pack(pady=(20, 30))
        
        # Container frame
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(padx=30, fill="both", expand=True)
        
        # Cédula
        ctk.CTkLabel(frame, text="Número de Cédula:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.e_cedula = ctk.CTkEntry(frame, textvariable=self.vars["cedula"], width=1000) # Use max width, frame limits it
        self.e_cedula.pack(fill="x", pady=(0, 15))
        
        # Nombres
        ctk.CTkLabel(frame, text="Nombres y Apellidos Completos:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.e_nombres = ctk.CTkEntry(frame, textvariable=self.vars["nombres"], width=1000)
        self.e_nombres.pack(fill="x", pady=(0, 15))
        
        # Fecha
        ctk.CTkLabel(frame, text="Fecha de Registro:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        e_fecha = ctk.CTkEntry(frame, textvariable=self.vars["fecha"], state="readonly", width=1000, fg_color="#F0F0F0", text_color="#333333")
        e_fecha.pack(fill="x", pady=(0, 20))
        
        # Imagen Frame
        img_frame = ctk.CTkFrame(frame, fg_color="#F8F9FA", border_width=1, border_color="#E0E0E0")
        img_frame.pack(fill="x", pady=(0, 20), ipadx=10, ipady=10)
        
        ctk.CTkLabel(img_frame, text="Imagen de Depósito:", font=("Arial", 12, "bold")).pack(anchor="center", pady=(5, 5))
        
        btn_img = ctk.CTkButton(img_frame, text="📂 Cargar Imagen", command=self.cargar_imagen, fg_color="#6C757D", hover_color="#5A6268")
        btn_img.pack(pady=5)
        
        self.lbl_archivo = ctk.CTkLabel(img_frame, text="Ningún archivo seleccionado", font=("Arial", 11, "italic"), text_color="gray")
        self.lbl_archivo.pack()
        
        # Botón Grabar
        btn_grabar = ctk.CTkButton(self, text="💾 GRABAR CLIENTE", command=self.grabar_cliente,
                                   font=("Arial", 16, "bold"), fg_color="#28A745", hover_color="#218838", height=50)
        btn_grabar.pack(fill="x", padx=30, pady=(10, 5))
        
        # Botón Simulador
        btn_simulador = ctk.CTkButton(self, text="📊 SIMULADOR DE CRÉDITO", command=self.abrir_simulador,
                                      font=("Arial", 14, "bold"), height=40)
        btn_simulador.pack(fill="x", padx=30, pady=(5, 20))

    def cargar_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar Imagen de Depósito",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp"), ("Todos los archivos", "*.*")],
            parent=self
        )
        if ruta:
            try:
                with open(ruta, "rb") as f:
                    self.image_bytes = f.read()
                self.vars["imagen_ruta"].set(ruta)
                # Extraer nombre archivo
                filename = ruta.split("/")[-1]
                self.lbl_archivo.configure(text=filename, text_color="#1860C3")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer la imagen.\n{e}", parent=self)
                
    def abrir_simulador(self):
        sim_window = ctk.CTkToplevel(self)
        sim_window.title("Simulador de Amortización (Sistema Francés)")
        sim_window.geometry("950x550")
        sim_window.transient(self)
        sim_window.grab_set()

        # Inputs Frame
        frame_inputs = ctk.CTkFrame(sim_window, fg_color="transparent")
        frame_inputs.pack(pady=20, padx=20, fill="x")

        # Variables
        monto_var = ctk.StringVar()
        tasa_var = ctk.StringVar()
        plazo_var = ctk.StringVar()
        cuota_var = ctk.StringVar()

        # Monto
        ctk.CTkLabel(frame_inputs, text="Monto ($):", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(frame_inputs, textvariable=monto_var, width=100).grid(row=0, column=1, padx=5, pady=5)

        # Tasa
        ctk.CTkLabel(frame_inputs, text="Tasa Anual (%):", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(frame_inputs, textvariable=tasa_var, width=100).grid(row=0, column=3, padx=5, pady=5)

        # Plazo
        ctk.CTkLabel(frame_inputs, text="Plazo (Meses):", font=("Arial", 12, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(frame_inputs, textvariable=plazo_var, width=100).grid(row=0, column=5, padx=5, pady=5)

        # Cuota
        ctk.CTkLabel(frame_inputs, text="Valor de Cuota:", font=("Arial", 12, "bold"), text_color="#1860C3").grid(row=0, column=6, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(frame_inputs, textvariable=cuota_var, width=120, state="readonly", fg_color="#E8F0FE", text_color="#333333", font=("Arial", 14, "bold")).grid(row=0, column=7, padx=5, pady=5)

        # Configurar Estilos Treeview
        style = ttk.Style(sim_window)
        style.theme_use("default")
        style.configure("Treeview", background="#0A1172", foreground="white", fieldbackground="#0A1172", rowheight=30, borderwidth=0, font=("Arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#333333", foreground="white")
        style.map("Treeview", background=[('selected', '#1f538d')])

        # Treeview Frame
        frame_tree = ctk.CTkFrame(sim_window)
        frame_tree.pack(pady=10, padx=20, fill="both", expand=True)

        columnas = ("Mes", "Cuota", "Interés", "Capital", "Saldo")
        tree = ttk.Treeview(frame_tree, columns=columnas, show="headings", height=10)
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        def calcular_tabla():
            try:
                monto = float(monto_var.get())
                tasa_anual = float(tasa_var.get())
                plazo = int(plazo_var.get())

                if monto <= 0 or tasa_anual <= 0 or plazo <= 0:
                    raise ValueError("Los valores deben ser mayores a 0")
            except ValueError:
                messagebox.showerror("Error de Entrada", "Por favor ingrese valores numéricos válidos mayores a 0.", parent=sim_window)
                return

            # Limpiar tabla
            for item in tree.get_children():
                tree.delete(item)

            tasa_mensual = (tasa_anual / 100) / 12
            # Fórmula Sistema Francés
            cuota = monto * (tasa_mensual * (1 + tasa_mensual)**plazo) / ((1 + tasa_mensual)**plazo - 1)
            
            # Formatear y mostrar en el campo superior
            cuota_var.set(f"${cuota:,.2f}")

            saldo = monto
            for mes in range(1, plazo + 1):
                interes = saldo * tasa_mensual
                capital = cuota - interes
                saldo = saldo - capital
                if saldo < 0:
                    saldo = 0 # Evitar -0.00 en la última cuota
                
                tree.insert("", "end", values=(
                    mes,
                    f"${cuota:.2f}",
                    f"${interes:.2f}",
                    f"${capital:.2f}",
                    f"${saldo:.2f}"
                ))

        # Botón Calcular
        btn_calcular = ctk.CTkButton(sim_window, text="Calcular Tabla", command=calcular_tabla, font=("Arial", 14, "bold"))
        btn_calcular.pack(pady=10)

    def grabar_cliente(self):
        cedula = self.vars["cedula"].get().strip()
        nombres = self.vars["nombres"].get().strip()
        fecha = self.vars["fecha"].get()
        
        if not cedula:
            messagebox.showwarning("Atención", "El número de cédula es obligatorio.", parent=self)
            return
            
        if not nombres:
            messagebox.showwarning("Atención", "Los nombres completos son obligatorios.", parent=self)
            return
            
        if not self.image_bytes:
            messagebox.showwarning("Atención", "Debe cargar obligatoriamente la imagen de depósito.", parent=self)
            return
            
        if not self.db_manager:
            messagebox.showerror("Error Crítico", "No hay conexión con la base de datos configurada.", parent=self)
            return
            
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Validación: Verificar si la cédula ya existe
            # Se usa el campo 'nombre' como nombre ('nombres' en otras, pero según esquema: nombre TEXT NOT NULL)
            cursor.execute("SELECT nombre, asesor FROM Clientes WHERE cedula = %s", (cedula,))
            row = cursor.fetchone()
            
            if row:
                asesor_registro = row[1] if row[1] else "Desconocido"
                messagebox.showerror("Registro Denegado", 
                                     f"El cliente con cédula {cedula} ya se encuentra registrado en el sistema.\n\n"
                                     f"Asesor a cargo: {asesor_registro}", parent=self)
                self.db_manager.release_connection(conn)
                return
            
            # Si no existe, procedemos con INSERT
            # Nota: Necesitamos que la tabla Clientes tenga la columna 'imagen_deposito' (BYTEA)
            try:
                # El envio a la BD debe ser nativo, asegurando primero envolver los bytes crudos a binario para pyscopg2
                # y usando de modo directo los placeholders en el bloque VALUES (%, %, %, %, %) sin convert_to()
                imagen_binaria = psycopg2.Binary(self.image_bytes) if self.image_bytes else None

                cursor.execute("""
                    INSERT INTO Clientes (cedula, nombre, fecha_registro, imagen_deposito, asesor)
                    VALUES (%s, %s, %s, %s, %s)
                """, (str(cedula), str(nombres), str(fecha), imagen_binaria, str(self.session_user)))
                
                conn.commit()
                messagebox.showinfo("Éxito", "Cliente grabado correctamente en la base de datos.", parent=self)
                self.destroy() # Cerramos el formulario si es exitoso
                
            except Exception as e_insert:
                conn.rollback()
                messagebox.showerror("Error de Base de Datos", f"Al insertar el cliente: {e_insert}", parent=self)

        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Error General", f"Error procesando solicitud: {e}", parent=self)
        finally:
            if conn and self.db_manager:
                self.db_manager.release_connection(conn)

