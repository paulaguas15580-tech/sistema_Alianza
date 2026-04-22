import re

file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace ==
content = content.replace('NIVEL_ACCESO == "Administrador"', 'NIVEL_ACCESO in ["Administrador", "admin"]')
# Replace !=
content = content.replace('NIVEL_ACCESO != "Administrador"', 'NIVEL_ACCESO not in ["Administrador", "admin"]')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced all NIVEL_ACCESO checks successfully.")
