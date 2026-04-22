file_path = 'basededatos_v3.0.py'
with open('out.txt', 'w', encoding='utf-8') as out:
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if 'Guardar / Actualizar' in line or 'Guardar Ref' in line:
                out.write(f"Line {i+1}: {line.strip()[:100]}\n")
            if 'CTkButton' in line and ('ref' in line or 'guardar' in line.lower() or 'micro' in line.lower()):
                out.write(f"Line {i+1}: {line.strip()[:100]}\n")
