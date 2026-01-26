import sys
import http.server
import socketserver
import threading
import time

print("--- DIAGNÓSTICO DE PYTHON ---")
print(f"Versión de Python: {sys.version}")
print(f"Ruta de ejecución: {sys.executable}")

def start_server():
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Servidor de prueba iniciado en http://localhost:{PORT}")
        httpd.serve_forever()

try:
    print("Iniciando prueba de servidor local...")
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(2)
    print("Si ves este mensaje, Python está ejecutando código correctamente.")
    print("Prueba abrir http://localhost:8080 en tu navegador.")
    input("Presiona ENTER para cerrar...")
except Exception as e:
    print(f"ERROR EN DIAGNÓSTICO: {e}")
