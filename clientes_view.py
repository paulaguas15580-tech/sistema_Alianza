import flet as ft
import database as db

class ClientesView(ft.Column):
    def __init__(self, page):
        self.page = page
        self.raw_data = []
        self.edit_mode = False
        self.current_id = None
        
        # --- UI COMPONENTS ---
        self.search_field = ft.TextField(
            label="Buscar por Cédula, Nombre, RUC o Carpeta", 
            expand=True, 
            on_change=self.filtrar_clientes, 
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            bgcolor="white"
        )
        
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cédula/RUC")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("N. Carpeta")),
                ft.DataColumn(ft.Text("Total Disp.")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
            heading_row_color=ft.Colors.with_opacity(0.05, "black"),
            border=ft.border.all(1, "#EEEEEE"),
            border_radius=10,
        )
        
        # --- FORM COMPONENTS (GROUPED) ---
        
        # 1. Datos Personales
        self.cedula = ft.TextField(label="Cédula", border_radius=8)
        self.ruc = ft.TextField(label="RUC", border_radius=8)
        self.nombre = ft.TextField(label="Nombres y Apellidos", border_radius=8)
        self.fecha_nac = ft.TextField(label="F. Nacim (DD/MM/YYYY)", border_radius=8)
        self.estado_civil = ft.Dropdown(
            label="Estado Civil",
            options=[
                ft.dropdown.Option("Soltero/a"),
                ft.dropdown.Option("Casado/a"),
                ft.dropdown.Option("Divorciado/a"),
                ft.dropdown.Option("Viudo/a"),
                ft.dropdown.Option("Union de Hecho"),
            ],
            border_radius=8
        )
        self.cargas = ft.TextField(label="Cargas", border_radius=8, value="0")
        
        # 2. Contacto y Referencias
        self.telefono = ft.TextField(label="Telf", border_radius=8)
        self.email = ft.TextField(label="Email", border_radius=8)
        self.direccion = ft.TextField(label="Dirección", border_radius=8)
        self.parroquia = ft.TextField(label="Parroquia", border_radius=8)
        self.tipo_vivienda = ft.Dropdown(
            label="Vivienda",
            options=[ft.dropdown.Option("Propia"), ft.dropdown.Option("Arrendada"), ft.dropdown.Option("Familar")],
            border_radius=8
        )
        self.ref_vivienda = ft.TextField(label="Ref. Vivienda", border_radius=8)
        self.ref_1 = ft.TextField(label="Ref. y Telf. 1", border_radius=8)
        self.ref_2 = ft.TextField(label="Ref. y Telf. 2", border_radius=8)
        self.asesor = ft.TextField(label="Asesor", border_radius=8)

        # 3. Situación Financiera
        self.score_buro = ft.TextField(label="Score Buró (1-999)", border_radius=8)
        self.ingresos_1 = ft.TextField(label="Ingresos ($)", border_radius=8, value="0.00", on_change=self.update_total_disp)
        self.fuente_1 = ft.TextField(label="Fuente Ingreso 1", border_radius=8)
        self.ingresos_2 = ft.TextField(label="Ingresos 2 ($)", border_radius=8, value="0.00", on_change=self.update_total_disp)
        self.fuente_2 = ft.TextField(label="Fuente Ingreso 2", border_radius=8)
        self.egresos = ft.TextField(label="Egresos ($)", border_radius=8, value="0.00", on_change=self.update_total_disp)
        self.total_disp = ft.Text("$ 0.00", size=20, weight="bold", color="green")
        
        self.chk_terreno = ft.Checkbox(label="Terreno", on_change=self.toggle_terreno)
        self.val_terreno = ft.TextField(label="Valor Terreno ($)", border_radius=8, visible=False)
        self.chk_casa = ft.Checkbox(label="Casa o Dep", on_change=self.toggle_casa)
        self.val_casa = ft.TextField(label="Valor Casa ($)", border_radius=8, visible=False)
        self.chk_local = ft.Checkbox(label="Local", border_radius=8, on_change=self.toggle_local)
        self.val_local = ft.TextField(label="Valor Local ($)", border_radius=8, visible=False)

        # 4. Crédito y Legal
        self.profesion = ft.TextField(label="Profesión", border_radius=8)
        self.apertura = ft.TextField(label="F. Apertura", border_radius=8)
        self.n_carpeta = ft.TextField(label="N. Apertura", border_radius=8)
        self.producto = ft.Dropdown(
            label="Producto",
            options=[ft.dropdown.Option("Rehabilitación"), ft.dropdown.Option("Inversión"), ft.dropdown.Option("Microcrédito")],
            border_radius=8
        )
        self.observaciones = ft.TextField(label="Obs", border_radius=8, multiline=True, height=80)
        
        self.chk_cartera = ft.Checkbox(label="Cartera", on_change=self.toggle_cartera)
        self.val_cartera = ft.TextField(label="Valor Cartera ($)", border_radius=8, visible=False)
        self.chk_demanda = ft.Checkbox(label="Demanda", on_change=self.toggle_demanda)
        self.val_demanda = ft.TextField(label="Valor Demanda ($)", border_radius=8, visible=False)
        self.chk_justicia = ft.Checkbox(label="Justicia", on_change=self.toggle_justicia)
        self.det_justicia = ft.TextField(label="Detalle Justicia", border_radius=8, visible=False)
        self.val_apertura = ft.TextField(label="Valor Apertura ($)", border_radius=8)

        # Dialog Tabs - Grouped as per user's request
        self.form_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Personales y Contacto",
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([self.cedula, self.ruc]),
                            self.nombre,
                            ft.Row([self.fecha_nac, self.estado_civil, self.cargas]),
                            ft.Divider(),
                            ft.Row([self.telefono, self.email]),
                            ft.Row([self.direccion, self.parroquia]),
                            ft.Row([self.tipo_vivienda, self.ref_vivienda]),
                            ft.Row([self.ref_1, self.ref_2]),
                            self.asesor,
                        ], scroll=ft.ScrollMode.AUTO, spacing=15),
                        padding=20
                    )
                ),
                ft.Tab(
                    text="Situación Financiera",
                    content=ft.Container(
                        content=ft.Column([
                            self.score_buro,
                            ft.Row([self.ingresos_1, self.fuente_1]),
                            ft.Row([self.ingresos_2, self.fuente_2]),
                            self.egresos,
                            ft.Row([ft.Text("Total Disponible: "), self.total_disp], alignment=ft.MainAxisAlignment.START),
                            ft.Divider(),
                            ft.Text("Patrimonio", weight="bold"),
                            ft.Row([self.chk_terreno, self.val_terreno]),
                            ft.Row([self.chk_casa, self.val_casa]),
                            ft.Row([self.chk_local, self.val_local]),
                        ], scroll=ft.ScrollMode.AUTO, spacing=15),
                        padding=20
                    )
                ),
                ft.Tab(
                    text="Crédito y Legal",
                    content=ft.Container(
                        content=ft.Column([
                            self.profesion,
                            ft.Row([self.apertura, self.n_carpeta]),
                            ft.Row([self.producto, self.val_apertura]),
                            self.observaciones,
                            ft.Divider(),
                            ft.Text("Estado Legal", weight="bold"),
                            ft.Row([self.chk_cartera, self.val_cartera]),
                            ft.Row([self.chk_demanda, self.val_demanda]),
                            ft.Row([self.chk_justicia, self.det_justicia]),
                        ], scroll=ft.ScrollMode.AUTO, spacing=15),
                        padding=20
                    )
                ),
            ],
            expand=True
        )

        self.dialog = ft.AlertDialog(
            title=ft.Text("Gestión de Cliente", size=24, weight="bold"),
            content=ft.Container(self.form_tabs, width=700, height=600),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_dialog),
                ft.ElevatedButton(
                    "Guardar Cliente", 
                    on_click=self.save_client,
                    style=ft.ButtonStyle(bgcolor="#1A237E", color="white")
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        initial_controls = [
            ft.Row([
                self.search_field, 
                ft.ElevatedButton(
                    "Nuevo Cliente", 
                    icon=ft.Icons.ADD, 
                    on_click=self.open_add,
                    style=ft.ButtonStyle(bgcolor="#1A237E", color="white", padding=20)
                )
            ], spacing=20),
            ft.Container(
                content=ft.ListView([self.data_table], expand=True),
                expand=True,
                margin=ft.margin.only(top=20)
            )
        ]
        
        super().__init__(controls=initial_controls, expand=True)

    def did_mount(self):
        self.cargar_datos()

    def cargar_datos(self):
        self.raw_data = db.consultar_clientes_db()
        self.update_table(self.raw_data)

    def update_table(self, data_list):
        self.data_table.rows = []
        for row in data_list:
            disp = db.formatear_float_str(row.get('total_disponible', 0))
            id_disp = row.get('cedula') or row.get('ruc') or "---"
            
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(id_disp)),
                        ft.DataCell(ft.Text(row['nombre'])),
                        ft.DataCell(ft.Text(row['telefono'] or "")),
                        ft.DataCell(ft.Text(row['numero_carpeta'] or "")),
                        ft.DataCell(ft.Text(f"${disp}")),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.Icons.EDIT_ROUNDED, icon_color="blue", on_click=lambda e, r=row: self.open_edit(r), tooltip="Editar"),
                            ft.IconButton(ft.Icons.DELETE_ROUNDED, icon_color="red", on_click=lambda e, r=row: self.delete_client(r), tooltip="Eliminar")
                        ]))
                    ]
                )
            )
        self.update()

    def update_total_disp(self, e):
        try:
            i1 = db.limpiar_moneda(self.ingresos_1.value)
            i2 = db.limpiar_moneda(self.ingresos_2.value)
            eg = db.limpiar_moneda(self.egresos.value)
            self.total_disp.value = "{:,.2f}".format(i1 + i2 - eg)
            self.update()
        except: pass

    def filtrar_clientes(self, e):
        term = self.search_field.value.lower()
        filtered = [
            x for x in self.raw_data 
            if term in x['nombre'].lower() 
            or term in (x['cedula'] or "")
            or term in (x['ruc'] or "")
            or term in (x['numero_carpeta'] or "")
        ]
        self.update_table(filtered)

    # Toggles
    def toggle_casa(self, e):
        self.val_casa.visible = self.chk_casa.value
        self.hip_casa.visible = self.chk_casa.value
        self.update()

    def toggle_terreno(self, e):
        self.val_terreno.visible = self.chk_terreno.value
        self.hip_terreno.visible = self.chk_terreno.value
        self.update()

    def toggle_local(self, e):
        self.val_local.visible = self.chk_local.value
        self.hip_local.visible = self.chk_local.value
        self.update()

    def toggle_cartera(self, e):
        self.val_cartera.visible = self.chk_cartera.value
        self.update()

    def toggle_demanda(self, e):
        self.val_demanda.visible = self.chk_demanda.value
        self.update()

    def toggle_justicia(self, e):
        self.det_justicia.visible = self.chk_justicia.value
        self.update()

    def open_add(self, e):
        self.edit_mode = False
        self.current_id = None
        self.limpiar_form()
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def open_edit(self, row):
        self.edit_mode = True
        self.current_id = row['id']
        self.cargar_form(row)
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        self.dialog.open = False
        self.page.update()

    def limpiar_form(self):
        # Reset all fields
        fields = [
            self.cedula, self.ruc, self.nombre, self.email, self.telefono, self.direccion, self.parroquia,
            self.cargas, self.fecha_nac, self.profesion, self.ingresos_1, self.fuente_1,
            self.ingresos_2, self.fuente_2, self.egresos, self.score_buro,
            self.ref_vivienda, self.val_casa, self.val_terreno,
            self.val_local, self.val_cartera, self.val_demanda, self.det_justicia,
            self.ref_1, self.ref_2, self.asesor, self.apertura, self.n_carpeta, self.producto,
            self.observaciones, self.val_apertura
        ]
        for f in fields: 
            if hasattr(f, "value"): f.value = ""
        
        self.cargas.value = "0"
        self.ingresos_1.value = "0.00"
        self.ingresos_2.value = "0.00"
        self.egresos.value = "0.00"
        self.total_disp.value = "$ 0.00"
        self.total_disp.color = None # Reset color
        
        self.chk_casa.value = self.chk_terreno.value = self.chk_local.value = False
        self.chk_cartera.value = self.chk_demanda.value = self.chk_justicia.value = False
        
        for f in [self.val_casa, self.val_terreno, self.val_local, self.val_cartera, self.val_demanda, self.det_justicia]:
            f.visible = False
        
        self.update()

    def cargar_form(self, row):
        self.cedula.value = row.get('cedula') or ""
        self.ruc.value = row.get('ruc') or ""
        self.nombre.value = row.get('nombre') or ""
        self.email.value = row.get('email') or ""
        self.telefono.value = row.get('telefono') or ""
        self.direccion.value = row.get('direccion') or ""
        self.parroquia.value = row.get('parroquia') or ""
        self.estado_civil.value = row.get('estado_civil')
        self.cargas.value = str(row.get('cargas_familiares') or 0)
        self.fecha_nac.value = row.get('fecha nacimiento') or ""
        self.profesion.value = row.get('profesion') or ""
        self.ingresos_1.value = str(row.get('ingresos_mensuales') or 0)
        self.fuente_1.value = row.get('fuente_ingreso') or ""
        self.ingresos_2.value = str(row.get('ingresos_mensuales_2') or 0)
        self.fuente_2.value = row.get('fuente_ingreso_2') or ""
        self.egresos.value = str(row.get('egresos') or 0)
        
        total = (row.get('ingresos_mensuales') or 0) + (row.get('ingresos_mensuales_2') or 0) - (row.get('egresos') or 0)
        self.total_disp.value = "$ {:,.2f}".format(total)
        self.total_disp.color = "green" if total >= 0 else "red"
        
        self.score_buro.value = str(row.get('score_buro') or "")
        self.tipo_vivienda.value = row.get('tipo_vivienda')
        self.ref_vivienda.value = row.get('referencia_vivienda') or ""
        
        # Patrimonio
        self.chk_casa.value = bool(row.get('casa_dep'))
        self.val_casa.value = str(row.get('valor_casa_dep') or "")
        self.val_casa.visible = self.chk_casa.value

        self.chk_terreno.value = bool(row.get('terreno'))
        self.val_terreno.value = str(row.get('valor_terreno') or "")
        self.val_terreno.visible = self.chk_terreno.value

        self.chk_local.value = bool(row.get('local'))
        self.val_local.value = str(row.get('valor_local') or "")
        self.val_local.visible = self.chk_local.value

        # Legal
        self.chk_cartera.value = bool(row.get('cartera castigada'))
        self.val_cartera.value = str(row.get('valor cartera') or "")
        self.val_cartera.visible = self.chk_cartera.value

        self.chk_demanda.value = bool(row.get('demanda judicial'))
        self.val_demanda.value = str(row.get('valor demanda') or "")
        self.val_demanda.visible = self.chk_demanda.value

        self.chk_justicia.value = bool(row.get('problemas justicia'))
        self.det_justicia.value = row.get('detalle justicia') or ""
        self.det_justicia.visible = self.chk_justicia.value

        self.ref_1.value = row.get('referencia1') or ""
        self.ref_2.value = row.get('referencia2') or ""
        self.asesor.value = row.get('asesor') or ""
        self.apertura.value = row.get('apertura') or ""
        self.n_carpeta.value = row.get('numero_carpeta') or ""
        self.producto.value = row.get('producto') or ""
        self.observaciones.value = row.get('observaciones') or ""
        self.val_apertura.value = str(row.get('valor_apertura') or "")

    def save_client(self, e):
        data = {
            'cedula': self.cedula.value,
            'ruc': self.ruc.value,
            'nombre': self.nombre.value,
            'email': self.email.value,
            'telefono': self.telefono.value,
            'direccion': self.direccion.value,
            'parroquia': self.parroquia.value,
            'estado_civil': self.estado_civil.value,
            'cargas_familiares': self.cargas.value,
            'fecha_nacimiento': self.fecha_nac.value,
            'profesion': self.profesion.value,
            'ingresos_mensuales': self.ingresos_1.value,
            'fuente_ingreso': self.fuente_1.value,
            'ingresos_mensuales_2': self.ingresos_2.value,
            'fuente_ingreso_2': self.fuente_2.value,
            'egresos': self.egresos.value,
            'score_buro': self.score_buro.value,
            'tipo_vivienda': self.tipo_vivienda.value,
            'referencia_vivienda': self.ref_vivienda.value,
            'casa_dep': 1 if self.chk_casa.value else 0,
            'valor_casa_dep': self.val_casa.value,
            'terreno': 1 if self.chk_terreno.value else 0,
            'valor_terreno': self.val_terreno.value,
            'local': 1 if self.chk_local.value else 0,
            'valor_local': self.val_local.value,
            'cartera_castigada': 1 if self.chk_cartera.value else 0,
            'valor_cartera': self.val_cartera.value,
            'demanda_judicial': 1 if self.chk_demanda.value else 0,
            'valor_demanda': self.val_demanda.value,
            'problemas_justicia': 1 if self.chk_justicia.value else 0,
            'detalle_justicia': self.det_justicia.value,
            'referencia1': self.ref_1.value,
            'referencia2': self.ref_2.value,
            'asesor': self.asesor.value,
            'apertura': self.apertura.value,
            'numero_carpeta': self.n_carpeta.value,
            'producto': self.producto.value,
            'observaciones': self.observaciones.value,
            'valor_apertura': self.val_apertura.value
        }
        
        if self.edit_mode:
            ok, msg = db.actualizar_cliente_db(self.current_id, data)
        else:
            ok, msg = db.guardar_cliente_db(data)
            
        if ok:
            self.page.snack_bar = ft.SnackBar(ft.Text("Operación exitosa"), bgcolor="green")
            self.close_dialog(None)
            self.cargar_datos()
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {msg}"), bgcolor="red")
        self.page.snack_bar.open = True
        self.page.update()

    def delete_client(self, row):
        def confirm_delete(e):
            db.eliminar_cliente_db(row['id'])
            self.cargar_datos()
            self.page.dialog.open = False
            self.page.update()

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text(f"¿Está seguro de eliminar al cliente {row['nombre']}?"),
            actions=[
                ft.TextButton("No", on_click=lambda _: setattr(self.page.dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Sí, Eliminar", on_click=confirm_delete, bgcolor="red", color="white")
            ]
        )
        self.page.dialog.open = True
        self.page.update()
