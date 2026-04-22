file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_func = False
for i, line in enumerate(lines):
    if 'def accion_guardar_micro()' in line or 'def guardar_microcredito_t' in line:
        in_func = True
    if in_func and 'def ' in line and 'guardar_micro' not in line and 'accion_guardar_micro' not in line:
        break
    if in_func:
        print(f"Line {i+1}: {line.strip()}")
