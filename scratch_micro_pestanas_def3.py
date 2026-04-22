file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
in_func = False
for line in lines:
    if line.strip().startswith('def actualizar_pestanas_status'):
        in_func = True
    if in_func:
        if line.strip().startswith('def ') and not line.strip().startswith('def actualizar_pestanas_status'):
            break
        print(line.rstrip())
