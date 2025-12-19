import flet as ft
import database as db
from clientes_view import ClientesView
from microcredito_view import MicrocreditoView


# =================================================================
# ESTILOS Y CONSTANTES
# =================================================================
COLOR_FONDO = "#FAFAD2" # LightGoldenrodYellow
COLOR_PRIMARY = "#1860C3" # Blue
COLOR_TEXTO = "#000000"

# =================================================================
# VISTAS
# =================================================================

class LoginView(ft.Container):
    def __init__(self, page):
        self.page = page
        self.user = ft.TextField(label="Usuario", width=300)
        self.password = ft.TextField(label="Contraseña", password=True, width=300)
        
        content_col = ft.Column(
            [
                ft.Text("Bienvenido a Alianza C3F", size=30, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                ft.Image(src="Logo Face.jpg", width=150, height=140, fit=ft.ImageFit.CONTAIN),
                self.user,
                self.password,
                ft.ElevatedButton("Ingresar", on_click=self.login, bgcolor=COLOR_PRIMARY, color="white", width=200)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
        
        super().__init__(
            content=content_col,
            bgcolor=COLOR_FONDO,
            alignment=ft.alignment.center,
            expand=True
        )

    def login(self, e):
        if not self.user.value or not self.password.value:
            self.page.snack_bar = ft.SnackBar(ft.Text("Ingrese usuario y contraseña"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
            return

        ok, nivel = db.verificar_credenciales(self.user.value, self.password.value)
        if ok:
            self.page.session.set("user", self.user.value)
            self.page.session.set("nivel", nivel)
            self.page.go("/menu")
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Credenciales incorrectas"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()

class MenuView(ft.Container):
    def __init__(self, page):
        self.page = page
        user = self.page.session.get("user")
        
        content_col = ft.Column(
            [
                ft.Row([
                    ft.Text("Menú Principal", size=30, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                    ft.IconButton(ft.Icons.LOGOUT, tooltip="Salir", on_click=lambda _: self.page.go("/"))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Row(
                    [
                        self.btn_menu("Clientes", ft.Icons.PEOPLE, "/clientes"),
                        self.btn_menu("Microcrédito", ft.Icons.MONEY, "/microcredito"),
                        self.btn_menu("Documentos", ft.Icons.FOLDER, "/documentos"),
                        self.btn_menu("Usuarios", ft.Icons.ADMIN_PANEL_SETTINGS, "/usuarios"),
                    ],
                    wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=20, run_spacing=20
                ),
                ft.Container(expand=True),
                ft.Text(f"Usuario activo: {user}", color="grey")
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
        
        super().__init__(
            content=content_col,
            bgcolor=COLOR_FONDO,
            padding=30,
            expand=True
        )

    def nav_to(self, route):
        self.page.go(route)

    def btn_menu(self, text, icon, route):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=40, color="white"),
                    ft.Text(text, color="white", size=16, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=200, height=150,
            bgcolor=COLOR_PRIMARY,
            border_radius=10,
            ink=True,
            on_click=lambda _: self.nav_to(route),
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.5, "black"))
        )



def main(page: ft.Page):
    page.title = "Sistema Alianza C3F"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = COLOR_FONDO
    page.padding = 0
    
    def route_change(route):
        page.views.clear()
        
        # LOGIN
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [LoginView(page)],
                    bgcolor=COLOR_FONDO,
                    padding=0
                )
            )
        
        # MENU
        elif page.route == "/menu":
            page.views.append(
                ft.View(
                    "/menu",
                    [MenuView(page)],
                    bgcolor=COLOR_FONDO
                )
            )
            
        # CLIENTES
        elif page.route == "/clientes":
            page.views.append(
                ft.View(
                    "/clientes",
                    [ft.AppBar(title=ft.Text("Gestión de Clientes"), bgcolor=COLOR_PRIMARY), 
                     ClientesView(page)],
                    bgcolor=COLOR_FONDO
                )
            )
        # MICROCREDITO
        elif page.route == "/microcredito":
            page.views.append(
                ft.View(
                    "/microcredito",
                    [ft.AppBar(title=ft.Text("Microcrédito"), bgcolor=COLOR_PRIMARY), 
                     MicrocreditoView(page)],
                    bgcolor=COLOR_FONDO
                )
            )
        elif page.route == "/documentos":
             page.views.append(
                ft.View(
                    "/documentos",
                    [ft.AppBar(title=ft.Text("Documentos"), bgcolor=COLOR_PRIMARY), 
                     ft.Text("Módulo de Documentos en construcción...")],
                    bgcolor=COLOR_FONDO
                )
            )
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)
