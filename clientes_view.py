import flet as ft
import database as db

class ClientesView(ft.Column):
    def __init__(self, page):
        self.page = page
        self.data = []
        self.edit_mode = False
        self.current_id = None
        
        # --- UI COMPONENTS ---
        self.search_field = ft.TextField(label="Buscar por Cédula/Nombre", width=300, on_change=self.filtrar_clientes, suffix_icon=ft.Icons.SEARCH)
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cédula")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Ingresos")),
                ft.DataColumn(ft.Text("N. Apertura")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        
        # --- FORM COMPONENTS ---
        self.cedula = ft.TextField(label="Cédula", width=150)
        self.nombre = ft.TextField(label="Nombres", width=300)
        self.telefono = ft.TextField(label="Teléfono", width=150)
        self.ingresos = ft.TextField(label="Ingresos", width=150)
        
        self.dialog = ft.AlertDialog(
            title=ft.Text("Editar Cliente"),
            content=ft.Column([
                self.cedula, self.nombre, self.telefono, self.ingresos
            ], height=400, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_dialog),
                ft.ElevatedButton("Guardar", on_click=self.save_client)
            ]
        )
        
        initial_controls = [
            ft.Row([self.search_field, ft.ElevatedButton("Nuevo Cliente", on_click=self.open_add)]),
            ft.ListView([self.data_table], expand=True, height=500)
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
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row['cedula'])),
                        ft.DataCell(ft.Text(row['nombre'])),
                        ft.DataCell(ft.Text(row['telefono'] or "")),
                        ft.DataCell(ft.Text(str(row['ingresos_mensuales']))),
                        ft.DataCell(ft.Text(row['numero_carpeta'] or "")),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.Icons.EDIT, on_click=lambda e, r=row: self.open_edit(r)),
                            ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda e, r=row: self.delete_client(r))
                        ]))
                    ]
                )
            )
        self.update()

    def filtrar_clientes(self, e):
        term = self.search_field.value.lower()
        filtered = [x for x in self.raw_data if term in x['nombre'].lower() or term in x['cedula']]
        self.update_table(filtered)

    def open_add(self, e):
        self.edit_mode = False
        self.current_id = None
        self.cedula.value = ""
        self.nombre.value = ""
        self.telefono.value = ""
        self.ingresos.value = "0.00"
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def open_edit(self, row):
        self.edit_mode = True
        self.current_id = row['id']
        self.cedula.value = row['cedula']
        self.nombre.value = row['nombre']
        self.telefono.value = row['telefono'] or ""
        self.ingresos.value = str(row['ingresos_mensuales'])
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        self.dialog.open = False
        self.page.update()

    def save_client(self, e):
        data = {
            'cedula': self.cedula.value,
            'nombre': self.nombre.value,
            'telefono': self.telefono.value,
            'ingresos_mensuales': self.ingresos.value
        }
        
        if self.edit_mode:
            ok, msg = db.actualizar_cliente_db(self.current_id, data)
        else:
            ok, msg = db.guardar_cliente_db(data)
            
        if ok:
            self.page.snack_bar = ft.SnackBar(ft.Text("Guardado éxito"))
            self.close_dialog(None)
            self.cargar_datos()
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {msg}"), bgcolor="red")
        self.page.snack_bar.open = True
        self.page.update()

    def delete_client(self, row):
        db.eliminar_cliente_db(row['id'])
        self.cargar_datos()
