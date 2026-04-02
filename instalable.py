import PyInstaller.__main__
import os

def build_executable():
    print("Iniciando la compilación del ejecutable...")

    # Lista de archivos gráficos en el directorio raíz necesarios para la interfaz
    recursos_graficos = [
        'Logo Face.jpg',
        'background.jpg',
        'bg_metal_brushed.jpg',
        'bg_microcredito.jpg',
        'btn_bg.jpg',
        'fondo gestion.jpg',
        'cartera_icon.png',
        'clientes_icon.png',
        'consultas_icon.png',
        'documentos_icon.png',
        'icono_guardar.png',
        'informes_icon.png',
        'intermediacion_icon.png',
        'logo_transparent.png',
        'microcredito_icon.png',
        'rehabilitacion_icon.png',
        'salir_icon.png',
        'usuarios_icon.png'
    ]

    # Configuración base de PyInstaller
    args = [
        'basededatos_v3.0.py',    # Script principal a compilar
        '--name=SistemaAlianza',  # Nombre del ejecutable final
        '--windowed',             # No mostrar consola negra en background
        '--noconsole',
        '--onedir',               # Recomendado crear una carpeta ('dist/SistemaAlianza') para mayor velocidad y menos problemas
        '--noconfirm',            # Sobrescribir carpeta dist/ automáticamente si existe
        '--clean',                # Limpiar caché antes de compilar
        '--hidden-import=reportlab.graphics.barcode.code128',
        '--hidden-import=reportlab.graphics.barcode.code93',
        '--hidden-import=reportlab.graphics.barcode.code39',
        '--hidden-import=reportlab.graphics.barcode.usps',
        '--hidden-import=reportlab.graphics.barcode.usps4cb',
        '--hidden-import=reportlab.graphics.barcode.ecc200datamatrix',
        '--hidden-import=reportlab.graphics.barcode.usps4s',
        '--collect-all=reportlab',
        '--collect-all=xhtml2pdf'
    ]

    # Añadir '--add-data' automáticamente para cada recurso gráfico existente
    for recurso in recursos_graficos:
        if os.path.exists(recurso):
            # En Windows el separador de '--add-data' es ';'
            args.append(f'--add-data={recurso};.')
        else:
            print(f"Advertencia: Archivo '{recurso}' no encontrado. Se omitirá en el empaquetado.")

    try:
        PyInstaller.__main__.run(args)
        print("\n¡Compilación Finalizada! Revisa la carpeta 'dist/'")
    except Exception as e:
        print(f"\nError en compilación: {e}")

if __name__ == "__main__":
    build_executable()
