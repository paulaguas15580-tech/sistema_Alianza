file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('filtrar_clientes()', 'buscar_clientes()')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced filtrar_clientes with buscar_clientes successfully.")
