import flet as ft
import database as db
import datetime

class MicrocreditoView(ft.Column):
    def __init__(self, page):
        self.page = page
        self.cedula_actual = None
        self.id_micro_actual = None
        
        # --- UI COMPONENTS ---
        # Search Section
        self.search_cedula = ft.TextField(
            label="Buscar Cédula del Cliente", 
            width=250, 
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            bgcolor="white",
            prefix_icon=ft.Icons.SEARCH
        )
        self.btn_buscar = ft.ElevatedButton(
            "Buscar", 
            icon=ft.Icons.SEARCH, 
            on_click=self.buscar_cliente,
            style=ft.ButtonStyle(bgcolor="#1A237E", color="white")
        )
        
        self.txt_nombre = ft.Text("Cliente: ---", size=18, weight=ft.FontWeight.BOLD, color="#1A237E")
        self.txt_ruc = ft.Text("RUC: ---", size=14, color="grey")
        
        # --- TABS CONTENT ---
        # Tab 1: Información Relevante
        self.txt_fecha_apertura = ft.TextField(label="Fecha Apertura", read_only=True, border_radius=8)
        self.txt_n_apertura = ft.TextField(label="N. Carpeta", read_only=True, border_radius=8)
        self.txt_val_apertura = ft.TextField(label="Valor Apertura ($)", border_radius=8)
        
        self.txt_direccion = ft.TextField(label="Dirección", read_only=True, multiline=True, border_radius=8)
        self.txt_estado_civil = ft.TextField(label="Estado Civil", read_only=True, border_radius=8)
        self.txt_cargas = ft.TextField(label="Cargas", read_only=True, border_radius=8)
        self.txt_ingresos_f1 = ft.TextField(label="Ingresos 1 / Fuente", read_only=True, border_radius=8)
        self.txt_ingresos_f2 = ft.TextField(label="Ingresos 2 / Fuente", read_only=True, border_radius=8)
        self.txt_egresos = ft.TextField(label="Egresos", read_only=True, border_radius=8)
        self.txt_total_disp = ft.TextField(label="Total Disponible", read_only=True, border_radius=8, bgcolor="#E8EAF6")
        
        self.txt_p_casa = ft.TextField(label="Casa (Valor/Hipotecado)", read_only=True, border_radius=8)
        self.txt_p_terreno = ft.TextField(label="Terreno (Valor/Hipotecado)", read_only=True, border_radius=8)
        self.txt_p_local = ft.TextField(label="Local (Valor/Hipotecado)", read_only=True, border_radius=8)
        
        self.txt_l_cartera = ft.TextField(label="Cartera (Castigada/Valor)", read_only=True, border_radius=8)
        self.txt_l_demanda = ft.TextField(label="Demanda (Judicial/Valor)", read_only=True, border_radius=8)
        self.txt_l_justicia = ft.TextField(label="Justicia (Problemas/Detalle)", read_only=True, multiline=True, border_radius=8)

        self.txt_obs_info = ft.TextField(
            label="Observaciones Específicas de Verificación", 
            multiline=True, 
            min_lines=3,
            border_radius=8
        )
        
        self.tab_info = ft.Container(
            content=ft.Column([
                ft.Text("Resumen de Información Relevante", size=20, weight=ft.FontWeight.BOLD, color="#1A237E"),
                ft.Row([self.txt_fecha_apertura, self.txt_n_apertura, self.txt_val_apertura]),
                ft.Divider(),
                ft.Text("Datos de la Ficha del Cliente", size=16, weight=ft.FontWeight.BOLD),
                self.txt_direccion,
                ft.Row([self.txt_estado_civil, self.txt_cargas]),
                ft.Row([self.txt_ingresos_f1, self.txt_ingresos_f2]),
                ft.Row([self.txt_egresos, self.txt_total_disp]),
                ft.Divider(),
                ft.Text("Patrimonio Declarado", size=16, weight=ft.FontWeight.BOLD),
                ft.Row([self.txt_p_casa, self.txt_p_terreno, self.txt_p_local]),
                ft.Divider(),
                ft.Text("Historial Legal Detectado", size=16, weight=ft.FontWeight.BOLD),
                self.txt_l_cartera,
                self.txt_l_demanda,
                self.txt_l_justicia,
                ft.Divider(),
                self.txt_obs_info
            ], scroll=ft.ScrollMode.AUTO), padding=20
        )
        
        # Tab 2: Llamadas (Referencias)
        def create_ref_fields(label_prefix):
            return [
                ft.TextField(label=f"{label_prefix}: Relación", border_radius=8),
                ft.TextField(label="Tiempo Conocer", border_radius=8),
                ft.TextField(label="Dirección", border_radius=8),
                ft.Dropdown(label="Vivienda", options=[ft.dropdown.Option("Propia"), ft.dropdown.Option("Arrendada"), ft.dropdown.Option("Familiar")], border_radius=8),
                ft.TextField(label="Cargas", border_radius=8),
                ft.TextField(label="Patrimonio (Vehiculo, Casa, Terreno...)", border_radius=8),
                ft.Dropdown(label="Responsable", options=[ft.dropdown.Option("Si"), ft.dropdown.Option("No")], border_radius=8)
            ]

        self.ref1_fields = create_ref_fields("Ref 1")
        self.ref2_fields = create_ref_fields("Ref 2")
        
        self.tab_llamadas = ft.Container(
            content=ft.Column([
                ft.Text("Verificación Referencia 1", weight=ft.FontWeight.BOLD, color="#1A237E", size=18),
                ft.ResponsiveRow([
                    ft.Column([self.ref1_fields[0], self.ref1_fields[1], self.ref1_fields[2], self.ref1_fields[3]], col={"sm": 6}),
                    ft.Column([self.ref1_fields[4], self.ref1_fields[5], self.ref1_fields[6]], col={"sm": 6})
                ]),
                ft.Divider(height=40),
                ft.Text("Verificación Referencia 2", weight=ft.FontWeight.BOLD, color="#1A237E", size=18),
                ft.ResponsiveRow([
                    ft.Column([self.ref2_fields[0], self.ref2_fields[1], self.ref2_fields[2], self.ref2_fields[3]], col={"sm": 6}),
                    ft.Column([self.ref2_fields[4], self.ref2_fields[5], self.ref2_fields[6]], col={"sm": 6})
                ])
            ], scroll=ft.ScrollMode.AUTO), padding=20
        )
        
        # Tab 3: Visitas
        self.txt_fecha_visita = ft.TextField(label="Fecha Visita (DD/MM/YYYY)", width=250, border_radius=8)
        self.txt_mapa = ft.TextField(label="Ubicación Sugerida", expand=True, border_radius=8)
        
        self.tab_visitas = ft.Container(
            content=ft.Column([
                ft.Text("Coordinación de Visita a Campo", size=20, weight=ft.FontWeight.BOLD, color="#1A237E"),
                ft.Row([self.txt_fecha_visita]),
                ft.Row([
                    self.txt_mapa, 
                    ft.ElevatedButton("Abrir en Maps", on_click=self.abrir_mapa, icon=ft.Icons.MAP, style=ft.ButtonStyle(bgcolor="#2E7D32", color="white"))
                ])
            ]), padding=20
        )
        
        # Tab 4: Recordatorios
        self.txt_obs = ft.TextField(label="Notas Internas y Recordatorios", multiline=True, min_lines=10, border_radius=8)
        self.tab_recordatorios = ft.Container(
            content=ft.Column([
                ft.Text("Seguimiento y Conclusiones", size=20, weight=ft.FontWeight.BOLD, color="#1A237E"),
                self.txt_obs
            ]), padding=20
        )

        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Información", content=self.tab_info),
                ft.Tab(text="Verif. Telefónica", content=self.tab_llamadas),
                ft.Tab(text="Visitas Campo", content=self.tab_visitas),
                ft.Tab(text="Conclusiones", content=self.tab_recordatorios),
            ],
            expand=True
        )
        
        super().__init__(
            controls=[
                ft.Container(
                    content=ft.Row([
                        self.search_cedula, self.btn_buscar,
                        ft.VerticalDivider(),
                        ft.Column([self.txt_nombre, self.txt_ruc], spacing=2),
                    ], spacing=20),
                    padding=10,
                    bgcolor="white",
                    border_radius=10,
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.05, "black"))
                ),
                self.tabs,
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            "Guardar Todo el Informe", 
                            icon=ft.Icons.SAVE_ROUNDED,
                            on_click=self.guardar, 
                            bgcolor="#1A237E", 
                            color="white",
                            height=50,
                            expand=True
                        )
                    ]),
                    padding=ft.padding.only(top=10)
                )
            ], 
            expand=True
        )

    def buscar_cliente(self, e):
        ced = self.search_cedula.value
        if not ced: return
        
        cli = db.buscar_clientes_db(ced)
        found = next((c for c in cli if c['cedula'] == ced), None)
        
        if found:
            self.cedula_actual = ced
            self.txt_nombre.value = f"Cliente: {found['nombre']}"
            self.txt_ruc.value = f"RUC: {found['ruc'] or 'N/A'}"
            
            # Info Tab
            self.txt_fecha_apertura.value = found.get('apertura') or ""
            self.txt_n_apertura.value = found.get('numero_carpeta') or ""
            self.txt_val_apertura.value = db.formatear_float_str(found.get('valor_apertura'))
            
            self.txt_direccion.value = found.get('direccion') or ""
            self.txt_estado_civil.value = found.get('estado_civil') or ""
            self.txt_cargas.value = str(found.get('cargas_familiares') or "0")
            
            self.txt_ingresos_f1.value = f"${db.formatear_float_str(found.get('ingresos_mensuales'))} ({found.get('fuente_ingreso') or 'N/A'})"
            self.txt_ingresos_f2.value = f"${db.formatear_float_str(found.get('ingresos_mensuales_2'))} ({found.get('fuente_ingreso_2') or 'N/A'})"
            self.txt_egresos.value = db.formatear_float_str(found.get('egresos'))
            self.txt_total_disp.value = db.formatear_float_str(found.get('total_disponible'))
            
            # Patrimonio
            self.txt_p_casa.value = f"${db.formatear_float_str(found.get('valor_casa_dep'))} / {found.get('hipotecado_casa_dep') or 'No'}" if found.get('casa_dep') else "N/A"
            self.txt_p_terreno.value = f"${db.formatear_float_str(found.get('valor_terreno'))} / {found.get('hipotecado') or 'No'}" if found.get('terreno') else "N/A"
            self.txt_p_local.value = f"${db.formatear_float_str(found.get('valor_local'))} / {found.get('hipotecado_local') or 'No'}" if found.get('local') else "N/A"
            
            # Legal
            self.txt_l_cartera.value = f"{'SÍ' if found.get('cartera castigada') else 'NO'} / ${db.formatear_float_str(found.get('valor_cartera'))}"
            self.txt_l_demanda.value = f"{'SÍ' if found.get('demanda judicial') else 'NO'} / ${db.formatear_float_str(found.get('valor_demanda'))}"
            self.txt_l_justicia.value = f"{'SÍ' if found.get('problemas justicia') else 'NO'}: {found.get('detalle justicia') or ''}"

            self.txt_mapa.value = found.get('direccion') or ""

            # Load Micro data
            micro = db.obtener_microcredito(ced)
            if micro:
                self.id_micro_actual = micro['id']
                self.txt_obs.value = micro['observaciones'] or ""
                self.txt_obs_info.value = micro['observaciones_info'] or ""
                # Populate Ref 1
                for i, field in enumerate(self.ref1_fields):
                    key = [
                        'ref1_relacion', 'ref1_tiempo_conocer', 'ref1_direccion', 
                        'ref1_tipo_vivienda', 'ref1_cargas', 'ref1_patrimonio', 'ref1_responsable'
                    ][i]
                    field.value = micro.get(key) or ""
                # Ref 2
                for i, field in enumerate(self.ref2_fields):
                    key = [
                        'ref2_relacion', 'ref2_tiempo_conocer', 'ref2_direccion', 
                        'ref2_tipo_vivienda', 'ref2_cargas', 'ref2_patrimonio', 'ref2_responsable'
                    ][i]
                    field.value = micro.get(key) or ""
            else:
                self.id_micro_actual = None
                self.txt_obs.value = ""
                self.txt_obs_info.value = ""
                for f in self.ref1_fields + self.ref2_fields: f.value = ""
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Cliente no encontrado", color="white"), bgcolor="red")
            self.page.snack_bar.open = True
            
        self.update()

    def abrir_mapa(self, e):
        import webbrowser
        d = self.txt_mapa.value
        if d: webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={d}")

    def guardar(self, e):
        if not self.cedula_actual:
            self.page.snack_bar = ft.SnackBar(ft.Text("Primero busque un cliente"), bgcolor="orange")
            self.page.snack_bar.open = True
            self.update()
            return
        
        # Save Val Apertura to Client
        # We need a db function for partial update or just update the whole client?
        # db.actualizar_cliente_db... needs ID. We have to fetch ID first.
        # For simplify, I'll assume we implement a specific patch function or fetch full obj.
        # (Ideally we update Clientes table too).
        
        data = {
            'id': self.id_micro_actual,
            'cedula_cliente': self.cedula_actual,
            'ruc': self.txt_ruc.value.replace("RUC: ", ""),
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
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="green" if ok else "red")
        self.page.snack_bar.open = True
        self.page.update()
