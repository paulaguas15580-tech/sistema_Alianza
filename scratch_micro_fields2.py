file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_func = False
for i, line in enumerate(lines):
    if 'def buscar_micro_auto' in line:
        in_func = True
    if in_func and 'def ' in line and 'buscar_micro_auto' not in line:
        break
    if in_func:
        if 'e_info_carpeta' in line or 'e_n_apertura_micro' in line or 'res[3]' in line:
            print(f"Line {i+1}: {line.strip()}")
