file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'status_micro_actual = ' in line and 'row[' in line:
            print(f"Line {i+1}: {line.strip()}")
        if 'var_sub_status.set(' in line and 'row[' in line:
            print(f"Line {i+1}: {line.strip()}")
        if 'e_f_desembolsado.insert(' in line and 'row[' in line:
            print(f"Line {i+1}: {line.strip()}")
