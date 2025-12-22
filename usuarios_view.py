import flet as ft
import database as db

class UsuariosView(ft.Column):
    def __init__(self, page):
        self.page = page
        self.users_data = []
        
        # --- UI COMPONENTS ---
        self.user_field = ft.TextField(label="Nuevo Usuario", border_radius=8, bgcolor="white", expand=True)
        self.pass_field = ft.TextField(label="Contraseña", password=True, border_radius=8, bgcolor="white", expand=True)
        self.level_drop = ft.Dropdown(
            label="Nivel de Acceso",
            options=[
                ft.dropdown.Option("1", "Administrador"),
                ft.dropdown.Option("2", "Operativo"),
            ],
            value="2",
            border_radius=8,
            bgcolor="white",
            width=200
        )
        
        self.btn_add = ft.ElevatedButton(
            "Crear Usuario", 
            icon=ft.Icons.PERSON_ADD, 
            on_click=self.add_user,
            style=ft.ButtonStyle(bgcolor="#1A237E", color="white")
        )
        
        self.users_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Usuario")),
                ft.DataColumn(ft.Text("Nivel")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
            border=ft.border.all(1, "#EEEEEE"),
            border_radius=10,
        )
        
        super().__init__(
            controls=[
                ft.Text("Administración de Usuarios", size=24, weight="bold", color="#1A237E"),
                ft.Container(
                    content=ft.Row([
                        self.user_field, self.pass_field, self.level_drop, self.btn_add
                    ], spacing=10),
                    padding=20,
                    bgcolor="white",
                    border_radius=10,
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.05, "black"))
                ),
                ft.Divider(height=40),
                ft.Text("Usuarios Registrados", size=18, weight="bold"),
                ft.Container(
                    content=ft.ListView([self.users_table], expand=True),
                    expand=True
                )
            ],
            expand=True,
            spacing=10
        )

    def did_mount(self):
        self.load_users()

    def load_users(self):
        conn, cursor = db.conectar_db()
        cursor.execute("SELECT id, usuario, nivel_acceso FROM Usuarios")
        rows = cursor.fetchall()
        conn.close()
        
        self.users_table.rows = []
        for r in rows:
            uid, uname, ulevel = r
            self.users_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(uname)),
                        ft.DataCell(ft.Text("Admin" if ulevel == 1 else "Operativo")),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE, 
                                icon_color="red", 
                                on_click=lambda e, id=uid: self.delete_user(id)
                            )
                        )
                    ]
                )
            )
        self.update()

    def add_user(self, e):
        u = self.user_field.value
        p = self.pass_field.value
        l = int(self.level_drop.value)
        
        if not u or not p:
            self.page.snack_bar = ft.SnackBar(ft.Text("Complete todos los campos"))
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        conn, cursor = db.conectar_db()
        try:
            cursor.execute("INSERT INTO Usuarios (usuario, clave_hash, nivel_acceso) VALUES (?, ?, ?)", 
                           (u, db.generar_hash(p), l))
            conn.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Usuario creado"), bgcolor="green")
            self.user_field.value = ""
            self.pass_field.value = ""
            self.load_users()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="red")
        finally:
            conn.close()
        self.page.snack_bar.open = True
        self.page.update()

    def delete_user(self, uid):
        # Prevent deleting the main admin if possible, but for now simple delete
        conn, cursor = db.conectar_db()
        cursor.execute("DELETE FROM Usuarios WHERE id = ?", (uid,))
        conn.commit()
        conn.close()
        self.load_users()
