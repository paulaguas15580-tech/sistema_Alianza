file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'btn_guardar_micro' in line or 'btn_ref' in line:
            try:
                print(f"Line {i+1}: {line.strip()}"[:100])
            except: pass
