file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'CTkButton' in line and 'micro' in line or 'Guardar' in line and 'micro' in line:
            print(f"Line {i+1}: {line.strip()}")
