file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_micro = False
for i, line in enumerate(lines):
    if 'def abrir_modulo_microcredito' in line:
        in_micro = True
    if in_micro and 'def abrir_' in line and 'abrir_modulo_microcredito' not in line:
        break
    if in_micro and 'nombre' in line and 'nombres' not in line:
        print(f"Line {i+1}: {line.strip()}")
