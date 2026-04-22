file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    in_func = False
    for i, line in enumerate(f):
        if 'def actualizar_pestanas_status' in line:
            in_func = True
        if in_func and 'def ' in line and 'actualizar_pestanas_status' not in line:
            break
        if in_func:
            print(f"Line {i+1}: {line.strip()}")
