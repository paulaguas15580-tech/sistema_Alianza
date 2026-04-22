with open('basededatos_v3.0.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'NIVEL_ACCESO ==' in line or 'NIVEL_ACCESO !=' in line or 'NIVEL_ACCESO in' in line:
            print(f"Line {i}: {line.strip()}")
