file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        if 'def buscar_cliente_micro' in line or 'def cargar_cliente_micro' in line or 'def buscar_micro' in line:
            print(line.strip())
