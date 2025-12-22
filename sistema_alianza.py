import flet as ft
import database as db
from clientes_view import ClientesView
from microcredito_view import MicrocreditoView
from usuarios_view import UsuariosView
from documentos_view import DocumentosView
from generico_view import GenericoView

# =================================================================
# ESTILOS Y CONSTANTES
# =================================================================
COLOR_FONDO = "#F4F7F6"
COLOR_PRIMARY = "#1A237E"
COLOR_SECONDARY = "#283593"
COLOR_ACCENT = "#FF9800"
COLOR_TEXTO = "#212121"

class LoginView(ft.Container):
    def __init__(self, page):
        self.page = page
        self.user = ft.TextField(
            label="Usuario", 
            width=320,
            border_radius=10,
            prefix_icon=ft.Icons.PERSON_OUTLINE
        )
        self.password = ft.TextField(
            label="Contraseña", 
            password=True, 
            can_reveal_password=True,
            width=320,
            border_radius=10,
            prefix_icon=ft.Icons.LOCK_OUTLINE
        )
        
        content_col = ft.Column(
            [
                ft.Image(src="Logo Face.jpg", width=120, height=110, fit=ft.ImageFit.CONTAIN),
                ft.Text("Alianza C3F", size=32, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                ft.Text("Sistema de Gestión de Clientes", size=16, color="grey"),
                ft.Divider(height=20, color="transparent"),
                self.user,
                self.password,
                ft.ElevatedButton(
                    "Iniciar Sesión", 
                    on_click=self.login, 
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor=COLOR_PRIMARY,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    width=320,
                    height=50
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15
        )
        
        super().__init__(
            content=ft.Container(
                content=content_col,
                bgcolor="white",
                padding=40,
                border_radius=20,
                width=400,
                height=550,
                border=ft.border.all(1, "#DDDDDD"),
                shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.1, "black"))
            ),
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
            print(f"Login exitoso: {self.user.value}")
            self.page.go("/menu")
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Credenciales incorrectas"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()

class MenuView(ft.Container):
    def __init__(self, page):
        self.page = page
        user = self.page.session.get("user") or "Paul"
        nivel = self.page.session.get("nivel") or 1
        
        content_col = ft.Column(
            [
                ft.Row([
                    ft.Column([
                        ft.Text("Panel de Control", size=28, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                        ft.Text(f"Bienvenido de nuevo, {user}", size=16, color="grey"),
                    ]),
                    ft.Row([
                        ft.IconButton(ft.Icons.NOTIFICATIONS_OUTLINED, icon_color=COLOR_PRIMARY),
                        ft.IconButton(ft.Icons.LOGOUT_ROUNDED, tooltip="Cerrar Sesión", on_click=lambda _: self.page.go("/"), icon_color="red"),
                    ])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=40),
                ft.ResponsiveRow(
                    [
                        self.btn_menu("Gestión de Clientes", ft.Icons.PEOPLE_ALT, "/clientes", "Base de datos"),
                        self.btn_menu("Consultas", ft.Icons.SEARCH, "/consultas", "Búsquedas generales"),
                        self.btn_menu("Microcrédito", ft.Icons.MONETIZATION_ON, "/microcredito", "Evaluación crédito"),
                        self.btn_menu("Rehabilitación", ft.Icons.HEALTH_AND_SAFETY, "/rehabilitacion", "Módulo de salud"),
                        self.btn_menu("Intermediación", ft.Icons.SYNC_ALT, "/intermediacion", "Gestión de trámite"),
                        self.btn_menu("Cartera", ft.Icons.ACCOUNT_BALANCE_WALLET, "/cartera", "Seguimiento"),
                        self.btn_menu("Informes", ft.Icons.ASSESSMENT, "/informes", "Reportes sistema"),
                        self.btn_menu("Documentos", ft.Icons.FILE_COPY, "/documentos", "Archivos PDF"),
                        self.btn_menu("Usuarios", ft.Icons.ADMIN_PANEL_SETTINGS, "/usuarios", "Accesos") if nivel == 1 else ft.Container(),
                    ],
                    spacing=20, run_spacing=20
                ),
                ft.Container(expand=True),
                ft.Row([
                    ft.Text("© 2024 Alianza C3F - Todos los derechos reservados", color="grey", size=12)
                ], alignment=ft.MainAxisAlignment.CENTER)
            ],
            expand=True
        )
        
        super().__init__(
            content=content_col,
            bgcolor=COLOR_FONDO,
            padding=40,
            expand=True
        )

    def nav_to(self, route):
        self.page.go(route)

    def btn_menu(self, text, icon, route, subtitle):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=40, color=COLOR_PRIMARY),
                    ft.Text(text, color=COLOR_TEXTO, size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Text(subtitle, color="grey", size=11, text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            col={"sm": 12, "md": 6, "lg": 4}, # 3 columns on large screens
            bgcolor="white",
            height=160,
            border_radius=15,
            ink=True,
            on_click=lambda _: self.nav_to(route),
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.05, "black")),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )

def main(page: ft.Page):
    page.title = "Sistema Alianza C3F"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1200
    page.window.height = 800
    page.bgcolor = COLOR_FONDO
    page.padding = 0
    
    page.fonts = {
        "Inter": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bslnt%2Cwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Inter")

    def route_change(e):
        print(f"Navegando a: {page.route}")
        page.views.clear()
        
        if page.route == "/" or page.route == "" or page.route == "/login":
            page.views.append(ft.View("/", [LoginView(page)], padding=0))
            
        elif page.route == "/menu":
            page.views.append(ft.View("/menu", [MenuView(page)], padding=0))
            
        elif page.route == "/clientes":
            page.views.append(ft.View("/clientes", [ft.AppBar(title=ft.Text("Gestión de Clientes"), bgcolor="white", color=COLOR_PRIMARY), ClientesView(page)], padding=20))
            
        elif page.route == "/microcredito":
            page.views.append(ft.View("/microcredito", [ft.AppBar(title=ft.Text("Evaluación de Microcrédito"), bgcolor="white", color=COLOR_PRIMARY), MicrocreditoView(page)], padding=20))
            
        elif page.route == "/documentos":
            page.views.append(ft.View("/documentos", [ft.AppBar(title=ft.Text("Gestión de Documentos"), bgcolor="white", color=COLOR_PRIMARY), DocumentosView(page)], padding=20))
            
        elif page.route == "/usuarios":
            page.views.append(ft.View("/usuarios", [ft.AppBar(title=ft.Text("Gestión de Usuarios"), bgcolor="white", color=COLOR_PRIMARY), UsuariosView(page)], padding=20))
            
        # Rutas genéricas
        elif page.route == "/rehabilitacion":
            page.views.append(ft.View("/rehabilitacion", [ft.AppBar(title=ft.Text("Rehabilitación"), bgcolor="white", color=COLOR_PRIMARY), GenericoView(page, "Rehabilitación")], padding=20))
            
        elif page.route == "/intermediacion":
            page.views.append(ft.View("/intermediacion", [ft.AppBar(title=ft.Text("Intermediación"), bgcolor="white", color=COLOR_PRIMARY), GenericoView(page, "Intermediación")], padding=20))
            
        elif page.route == "/cartera":
            page.views.append(ft.View("/cartera", [ft.AppBar(title=ft.Text("Cartera"), bgcolor="white", color=COLOR_PRIMARY), GenericoView(page, "Cartera")], padding=20))
            
        elif page.route == "/consultas":
            page.views.append(ft.View("/consultas", [ft.AppBar(title=ft.Text("Consultas"), bgcolor="white", color=COLOR_PRIMARY), GenericoView(page, "Consultas")], padding=20))
            
        elif page.route == "/informes":
            page.views.append(ft.View("/informes", [ft.AppBar(title=ft.Text("Informes"), bgcolor="white", color=COLOR_PRIMARY), GenericoView(page, "Informes")], padding=20))
            
        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Asegurar que la ruta inicial sea /
    if page.route == "/":
        route_change(None)
    else:
        page.go(page.route)

if __name__ == "__main__":
    print("Iniciando aplicación en modo navegador en el puerto 8553...")
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8553)
