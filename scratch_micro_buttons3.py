file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'guardar' in line.lower() and 'micro' in line.lower() and 'button' in line.lower():
            try:
                print(f"Line {i+1}: {line.strip()}"[:100])
            except: pass
