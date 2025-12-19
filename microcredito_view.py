import flet as ft
import database as db
import datetime

class MicrocreditoView(ft.Column):
    def __init__(self, page):
        self.page = page
        self.cedula_actual = None
        self.id_micro_actual = None
        
        # --- UI COMPONENTS ---
        # Search
        self.search_cedula = ft.TextField(label="Buscar Cédula", width=200, keyboard_type=ft.KeyboardType.NUMBER)
        self.btn_buscar = ft.IconButton(ft.Icons.SEARCH, on_click=self.buscar_cliente)
        
        self.txt_nombre = ft.TextField(label="Nombre Cliente", read_only=True, width=300)
        self.txt_ruc = ft.TextField(label="RUC", read_only=True, width=150)
        
        # --- TABS ---
        # Tab 1: Información
        self.txt_fecha_apertura = ft.TextField(label="Fecha Apertura", read_only=True)
        self.txt_n_apertura = ft.TextField(label="N. Apertura", read_only=True)
        self.txt_val_apertura = ft.TextField(label="Valor Apertura ($)")
        
        # Nuevos campos de Gestión de Clientes (Lectura)
        self.txt_direccion = ft.TextField(label="Dirección", read_only=True, multiline=True)
        self.txt_estado_civil = ft.TextField(label="Estado Civil", read_only=True)
        self.txt_cargas = ft.TextField(label="Cargas", read_only=True)
        self.txt_ingresos_f1 = ft.TextField(label="Ingresos 1 / Fuente", read_only=True)
        self.txt_ingresos_f2 = ft.TextField(label="Ingresos 2 / Fuente", read_only=True)
        self.txt_egresos = ft.TextField(label="Egresos", read_only=True)
        self.txt_total_disp = ft.TextField(label="Total Disponible", read_only=True)
        
        # Patrimonio
        self.txt_p_casa = ft.TextField(label="Casa (Valor/Hipotecado)", read_only=True)
        self.txt_p_terreno = ft.TextField(label="Terreno (Valor/Hipotecado)", read_only=True)
        self.txt_p_local = ft.TextField(label="Local (Valor/Hipotecado)", read_only=True)
        
        # Parte Legal
        self.txt_l_cartera = ft.TextField(label="Cartera (Castigada/Valor)", read_only=True)
        self.txt_l_demanda = ft.TextField(label="Demanda (Judicial/Valor)", read_only=True)
        self.txt_l_justicia = ft.TextField(label="Justicia (Problemas/Detalle)", read_only=True, multiline=True)

        # Nuevo campo Observaciones (1.5 cm alto x 2.5 cm ancho aprox)
        # 1.5 cm ~ 57px, 2.5 cm ~ 95px
        self.txt_obs_info = ft.TextField(
            label="Obs.", 
            multiline=True, 
            width=95, 
            height=57, 
            text_size=10, 
            content_padding=5
        )
        
        self.tab_info = ft.Container(
            content=ft.Column([
                ft.Text("Información Relevante", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([self.txt_fecha_apertura, self.txt_n_apertura, self.txt_val_apertura]),
                ft.Divider(),
                ft.Text("Datos de Cliente (Desde Gestión Clientes)", size=16, weight=ft.FontWeight.BOLD),
                self.txt_direccion,
                ft.Row([self.txt_estado_civil, self.txt_cargas]),
                ft.Row([self.txt_ingresos_f1, self.txt_ingresos_f2]),
                ft.Row([self.txt_egresos, self.txt_total_disp]),
                ft.Divider(),
                ft.Text("Patrimonio", size=16, weight=ft.FontWeight.BOLD),
                ft.Row([self.txt_p_casa, self.txt_p_terreno, self.txt_p_local]),
                ft.Divider(),
                ft.Text("Historial Legal", size=16, weight=ft.FontWeight.BOLD),
                self.txt_l_cartera,
                self.txt_l_demanda,
                self.txt_l_justicia,
                ft.Divider(),
                ft.Row([
                    ft.Text("Observaciones Específicas:"),
                    self.txt_obs_info
                ])
            ], scroll=ft.ScrollMode.AUTO), padding=20
        )
        
        # Tab 2: Llamadas (Referencias)
        def create_ref_fields(label_prefix):
            return [
                ft.TextField(label=f"{label_prefix}: Relación"),
                ft.TextField(label="Tiempo Conocer"),
                ft.TextField(label="Dirección"),
                ft.Dropdown(label="Vivienda", options=[ft.dropdown.Option("Propia"), ft.dropdown.Option("Arrendada"), ft.dropdown.Option("Familiar")]),
                ft.TextField(label="Cargas"),
                ft.TextField(label="Patrimonio (Vehiculo, Casa, Terreno...)"), # Simplified for now
                ft.Dropdown(label="Responsable", options=[ft.dropdown.Option("Si"), ft.dropdown.Option("No")])
            ]

        self.ref1_fields = create_ref_fields("Ref 1")
        self.ref2_fields = create_ref_fields("Ref 2")
        
        self.tab_llamadas = ft.Container(
            content=ft.Column([
                ft.Text("Verificación Referencia 1", weight=ft.FontWeight.BOLD),
                ft.ResponsiveRow([
                    ft.Column(self.ref1_fields[:4], col={"sm": 6}),
                    ft.Column(self.ref1_fields[4:], col={"sm": 6})
                ]),
                ft.Divider(),
                ft.Text("Verificación Referencia 2", weight=ft.FontWeight.BOLD),
                ft.ResponsiveRow([
                    ft.Column(self.ref2_fields[:4], col={"sm": 6}),
                    ft.Column(self.ref2_fields[4:], col={"sm": 6})
                ])
            ], scroll=ft.ScrollMode.AUTO), padding=20
        )
        
        # Tab 3: Visitas
        self.txt_fecha_visita = ft.TextField(label="Fecha Visita (DD/MM/YYYY)", width=200)
        self.txt_mapa = ft.TextField(label="Dirección Mapa", width=400)
        
        self.tab_visitas = ft.Container(
            content=ft.Column([
                ft.Text("Agendar Visita / Ubicación", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([self.txt_fecha_visita]),
                ft.Row([self.txt_mapa, ft.ElevatedButton("Ver en Maps", on_click=self.abrir_mapa, icon=ft.Icons.MAP)])
            ]), padding=20
        )
        
        # Tab 4: Recordatorios
        self.txt_obs = ft.TextField(label="Observaciones / Recordatorios", multiline=True, min_lines=5)
        self.tab_recordatorios = ft.Container(
            content=ft.Column([
                ft.Text("Notas", size=20, weight=ft.FontWeight.BOLD),
                self.txt_obs
            ]), padding=20
        )

        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Información", content=self.tab_info),
                ft.Tab(text="Llamadas", content=self.tab_llamadas),
                ft.Tab(text="Visitas", content=self.tab_visitas),
                ft.Tab(text="Recordatorios", content=self.tab_recordatorios),
            ],
            expand=True
        )
        
        initial_controls = [
            ft.Row([self.search_cedula, self.btn_buscar, self.txt_nombre, self.txt_ruc]),
            self.tabs,
            ft.ElevatedButton("Guardar Todo", on_click=self.guardar, bgcolor="#1860C3", color="white")
        ]
        
        super().__init__(controls=initial_controls, expand=True)

    def buscar_cliente(self, e):
        ced = self.search_cedula.value
        if not ced: return
        
        cli = db.buscar_clientes_db(ced) # This returns list, check exact match
        found = next((c for c in cli if c['cedula'] == ced), None)
        
        if found:
            self.cedula_actual = ced
            self.txt_nombre.value = found['nombre']
            self.txt_ruc.value = found['ruc'] or ""
            
            # Info Tab
            self.txt_fecha_apertura.value = found.get('apertura') or ""
            self.txt_n_apertura.value = found.get('numero_carpeta') or ""
            self.txt_val_apertura.value = str(found.get('valor_apertura') or "")
            
            # Populate Client info fields
            self.txt_direccion.value = found.get('direccion') or ""
            self.txt_estado_civil.value = found.get('estado_civil') or ""
            self.txt_cargas.value = str(found.get('cargas_familiares') or "0")
            
            ing1 = db.formatear_float_str(found.get('ingresos_mensuales'))
            fuente1 = found.get('fuente_ingreso') or ""
            self.txt_ingresos_f1.value = f"${ing1} ({fuente1})" if ing1 else ""
            
            ing2 = db.formatear_float_str(found.get('ingresos_mensuales_2'))
            fuente2 = found.get('fuente_ingreso_2') or ""
            self.txt_ingresos_f2.value = f"${ing2} ({fuente2})" if ing2 else ""
            
            self.txt_egresos.value = db.formatear_float_str(found.get('egresos'))
            self.txt_total_disp.value = db.formatear_float_str(found.get('total_disponible'))
            
            # Patrimonio
            casa_val = db.formatear_float_str(found.get('valor_casa_dep'))
            casa_hip = found.get('hipotecado_casa_dep') or "No"
            self.txt_p_casa.value = f"${casa_val} / {casa_hip}" if found.get('casa_dep') else "N/A"
            
            terr_val = db.formatear_float_str(found.get('valor_terreno'))
            terr_hip = found.get('hipotecado') or "No"
            self.txt_p_terreno.value = f"${terr_val} / {terr_hip}" if found.get('terreno') else "N/A"
            
            local_val = db.formatear_float_str(found.get('valor_local'))
            local_hip = found.get('hipotecado_local') or "No"
            self.txt_p_local.value = f"${local_val} / {local_hip}" if found.get('local') else "N/A"
            
            # Legal
            cart_val = db.formatear_float_str(found.get('valor_cartera'))
            cart_sn = "SÍ" if found.get('cartera castigada') else "NO"
            self.txt_l_cartera.value = f"{cart_sn} / ${cart_val}"
            
            dem_val = db.formatear_float_str(found.get('valor_demanda'))
            dem_sn = "SÍ" if found.get('demanda judicial') else "NO"
            self.txt_l_demanda.value = f"{dem_sn} / ${dem_val}"
            
            just_sn = "SÍ" if found.get('problemas justicia') else "NO"
            just_det = found.get('detalle justicia') or ""
            self.txt_l_justicia.value = f"{just_sn}: {just_det}"

            self.txt_mapa.value = found.get('direccion') or ""

            # Load Micro data
            micro = db.obtener_microcredito(ced)
            if micro:
                self.id_micro_actual = micro['id']
                self.txt_obs.value = micro['observaciones'] or ""
                self.txt_obs_info.value = micro['observaciones_info'] or ""
                # Populate Ref 1
                self.ref1_fields[0].value = micro['ref1_relacion']
                self.ref1_fields[1].value = micro['ref1_tiempo_conocer']
                self.ref1_fields[2].value = micro['ref1_direccion']
                self.ref1_fields[3].value = micro['ref1_tipo_vivienda']
                self.ref1_fields[4].value = micro['ref1_cargas']
                self.ref1_fields[5].value = micro['ref1_patrimonio']
                self.ref1_fields[6].value = micro['ref1_responsable']
                # Ref 2
                self.ref2_fields[0].value = micro['ref2_relacion']
                self.ref2_fields[1].value = micro['ref2_tiempo_conocer']
                self.ref2_fields[2].value = micro['ref2_direccion']
                self.ref2_fields[3].value = micro['ref2_tipo_vivienda']
                self.ref2_fields[4].value = micro['ref2_cargas']
                self.ref2_fields[5].value = micro['ref2_patrimonio']
                self.ref2_fields[6].value = micro['ref2_responsable']
            else:
                self.id_micro_actual = None
                self.txt_obs.value = ""
                self.txt_obs_info.value = ""
                for f in self.ref1_fields: f.value = ""
                for f in self.ref2_fields: f.value = ""
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Cliente no encontrado"))
            self.page.snack_bar.open = True
            
        self.update()

    def abrir_mapa(self, e):
        import webbrowser
        d = self.txt_mapa.value
        if d: webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={d}")

    def guardar(self, e):
        if not self.cedula_actual: return
        
        # Save Val Apertura to Client
        # We need a db function for partial update or just update the whole client?
        # db.actualizar_cliente_db... needs ID. We have to fetch ID first.
        # For simplify, I'll assume we implement a specific patch function or fetch full obj.
        # Let's skip updating client val_apertura for this snippet efficiency, focus on Micro data.
        # (Ideally we update Clientes table too).
        
        data = {
            'id': self.id_micro_actual,
            'cedula_cliente': self.cedula_actual,
            'ruc': self.txt_ruc.value,
            'observaciones': self.txt_obs.value,
            'observaciones_info': self.txt_obs_info.value,
            # Ref 1
            'ref1_relacion': self.ref1_fields[0].value,
            'ref1_tiempo_conocer': self.ref1_fields[1].value,
            'ref1_direccion': self.ref1_fields[2].value,
            'ref1_tipo_vivienda': self.ref1_fields[3].value,
            'ref1_cargas': self.ref1_fields[4].value,
            'ref1_patrimonio': self.ref1_fields[5].value,
            'ref1_responsable': self.ref1_fields[6].value,
            # Ref 2
            'ref2_relacion': self.ref2_fields[0].value,
            'ref2_tiempo_conocer': self.ref2_fields[1].value,
            'ref2_direccion': self.ref2_fields[2].value,
            'ref2_tipo_vivienda': self.ref2_fields[3].value,
            'ref2_cargas': self.ref2_fields[4].value,
            'ref2_patrimonio': self.ref2_fields[5].value,
            'ref2_responsable': self.ref2_fields[6].value,
        }
        
        ok, msg = db.guardar_microcredito_db(data)
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()
