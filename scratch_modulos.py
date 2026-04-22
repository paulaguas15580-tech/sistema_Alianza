import re
with open('basededatos_v3.0.py', 'r', encoding='utf-8') as f:
    for line in f:
        if 'def abrir_' in line:
            print(line.strip())
