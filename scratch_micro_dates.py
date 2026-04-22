file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'fecha_negado' in line or 'fecha_desistimiento' in line or 'fecha_comite' in line:
            print(f"Line {i+1}: {line.strip()}")
        if 'row[' in line and i > 4160 and i < 4175:
            print(f"Line {i+1}: {line.strip()}")
