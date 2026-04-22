file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'set_micro_state' in line:
            print(f"Line {i+1}: {line.strip()}")
