import flet as ft
import database as db
import subprocess
import sys
import os

# =================================================================
# ESTILOS
# =================================================================
COLOR_FONDO = "#FAFAD2" # LightGoldenrodYellow
COLOR_PRIMARY = "#1860C3" # Blue

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
            self.page.window.close()
            # Launch basededatos.py
            cmd = [sys.executable, "basededatos.py", "--user", self.user.value, "--level", nivel]
            subprocess.Popen(cmd)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Credenciales incorrectas"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()

def main(page: ft.Page):
    page.title = "Login - Alianza C3F"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = COLOR_FONDO
    page.window.width = 400
    page.window.height = 500
    page.window.resizable = False
    
    page.add(LoginView(page))

if __name__ == "__main__":
    ft.app(target=main)
