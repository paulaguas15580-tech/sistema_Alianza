file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_func = False
for i, line in enumerate(lines):
    if 'def guardar_caja' in line or 'def guardar_datos_caja' in line:
        in_func = True
    if in_func and 'def ' in line and 'guardar_caja' not in line and 'guardar_datos_caja' not in line:
        break
    if in_func:
        if 'execute' in line or 'INSERT' in line or 'UPDATE' in line:
            print(f"Line {i+1}: {line.strip()}")
