file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'num_carpeta, aper, nac, obs,' in line or 'aper, num_carpeta, nac, obs,' in line:
            print(f"Line {i+1}: {line.strip()}")
