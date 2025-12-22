import flet as ft
import database as db

class GenericoView(ft.Column):
    def __init__(self, page, titulo):
        super().__init__(expand=True)
        self.page = page
        self.titulo = titulo
        
        # Campos de búsqueda
        self.e_cedula = ft.TextField(label="Cédula", width=200, on_change=self.buscar_cliente)
        self.e_ruc = ft.TextField(label="RUC", width=200, on_change=self.buscar_cliente)
        self.e_nombre = ft.TextField(label="Nombre del Cliente", expand=True, on_change=self.buscar_cliente)
        
        # Contenedor de resultado
        self.res_nombre = ft.Text("Cliente: ", size=18, weight="bold", color="grey")
        self.res_cedula = ft.Text("Cédula: ", size=14, color="grey")
        
        # Contenido específico (Placeholder)
        self.dynamic_content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CONSTRUCTION_ROUNDED, size=50, color="grey"),
                ft.Text(f"Contenido específico de {self.titulo} aquí...", color="grey"),
                ft.Text("Módulo en desarrollo", size=12, italic=True, color="grey")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            padding=50,
            expand=True
        )

        self.controls = [
            ft.Text(self.titulo.upper(), size=24, weight="bold", color="#1A237E"),
            ft.Divider(),
            ft.Text("Búsqueda de Cliente", size=16, weight="bold"),
            ft.Row([self.e_cedula, self.e_ruc, self.e_nombre], spacing=10),
            ft.Container(
                content=ft.Column([
                    self.res_nombre,
                    self.res_cedula,
                ]),
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.1, "blue"),
                border_radius=10
            ),
            ft.Divider(),
            self.dynamic_content
        ]

    def buscar_cliente(self, e):
        ced = self.e_cedula.value.strip()
        ruc = self.e_ruc.value.strip()
        nom = self.e_nombre.value.strip()
        
        term = ""
        if len(ced) >= 3: term = ced
        elif len(ruc) >= 3: term = ruc
        elif len(nom) >= 3: term = nom
        
        if not term:
            self.res_nombre.value = "Cliente: "
            self.res_cedula.value = "Cédula: "
            self.page.update()
            return
            
        res = db.buscar_clientes_db(term)
        if res:
            cliente = res[0] # Tomamos el primero
            self.res_nombre.value = f"Cliente: {cliente['nombre']}" # Nombre
            self.res_cedula.value = f"Cédula: {cliente['cedula']}" # Cédula
        else:
            self.res_nombre.value = "Cliente: No encontrado"
            self.res_cedula.value = "Cédula: -"
            
        self.page.update()
