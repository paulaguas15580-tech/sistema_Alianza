import flet as ft
import database as db
import os
import shutil
import datetime

class DocumentosView(ft.Column):
    def __init__(self, page):
        self.page = page
        self.selected_cedula = None
        
        # --- FILE PICKER ---
        self.picker = ft.FilePicker(on_result=self.on_file_result)
        self.page.overlay.append(self.picker)
        
        # --- UI COMPONENTS ---
        self.search_cedula = ft.TextField(
            label="Cédula del Cliente", 
            width=300, 
            border_radius=8,
            suffix_icon=ft.Icons.SEARCH,
            on_submit=self.load_docs
        )
        
        self.lbl_cliente = ft.Text("Cliente: ---", size=18, weight="bold", color="#1A237E")
        
        self.doc_list = ft.ListView(expand=True, spacing=10)
        
        self.btn_upload = ft.ElevatedButton(
            "Subir Documento (PDF/JPG)", 
            icon=ft.Icons.UPLOAD_FILE,
            on_click=lambda _: self.picker.pick_files(allow_multiple=False, allowed_extensions=["pdf", "jpg", "png"]),
            visible=False,
            style=ft.ButtonStyle(bgcolor="#2E7D32", color="white")
        )
        
        super().__init__(
            controls=[
                ft.Text("Gestión de Documentos", size=24, weight="bold", color="#1A237E"),
                ft.Row([
                    self.search_cedula,
                    ft.ElevatedButton("Buscar", on_click=self.load_docs)
                ]),
                ft.Divider(),
                ft.Row([self.lbl_cliente, self.btn_upload], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=self.doc_list,
                    expand=True,
                    padding=10
                )
            ],
            expand=True
        )

    def load_docs(self, e):
        ced = self.search_cedula.value
        if not ced: return
        
        # Check client
        cli = db.buscar_clientes_db(ced)
        found = next((c for c in cli if c['cedula'] == ced), None)
        
        if found:
            self.selected_cedula = ced
            self.lbl_cliente.value = f"Cliente: {found['nombre']}"
            self.btn_upload.visible = True
            self.refresh_list()
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Cliente no encontrado"))
            self.page.snack_bar.open = True
            self.selected_cedula = None
            self.lbl_cliente.value = "Cliente: ---"
            self.btn_upload.visible = False
            self.doc_list.controls.clear()
        self.update()

    def refresh_list(self):
        self.doc_list.controls.clear()
        conn, cursor = db.conectar_db()
        cursor.execute("SELECT nombre_archivo, ruta_archivo, fecha_subida FROM Documentos WHERE cedula_cliente = ?", (self.selected_cedula,))
        docs = cursor.fetchall()
        conn.close()
        
        for d in docs:
            name, path, date = d
            self.doc_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PICTURE_AS_PDF if ".pdf" in name.lower() else ft.Icons.IMAGE),
                    title=ft.Text(name),
                    subtitle=ft.Text(f"Subido el: {date}"),
                    trailing=ft.IconButton(ft.Icons.OPEN_IN_NEW, on_click=lambda e, p=path: self.open_file(p)),
                    bgcolor="white",
                    border_radius=10
                )
            )
        self.update()

    def on_file_result(self, e: ft.FilePickerResultEvent):
        if not e.files or not self.selected_cedula: return
        
        file = e.files[0]
        dest_dir = os.path.join("Documentos", self.selected_cedula)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        dest_path = os.path.join(dest_dir, file.name)
        shutil.copy(file.path, dest_path)
        
        # Save to DB
        db.guardar_archivo_db(self.selected_cedula, file.name, dest_path, "Manual")
        
        self.page.snack_bar = ft.SnackBar(ft.Text("Archivo subido con éxito"), bgcolor="green")
        self.page.snack_bar.open = True
        self.refresh_list()

    def open_file(self, path):
        if os.path.exists(path):
            os.startfile(path)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("El archivo no existe localmente"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
