import re

file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix SQL queries
content = content.replace('SELECT cedula, nombre, ruc, numero_carpeta', 'SELECT cedula, nombres, ruc, numero_carpeta')
content = content.replace('WHERE nombre LIKE', 'WHERE nombres LIKE')
content = content.replace('WHERE nombre =', 'WHERE nombres =')
# Fix any other SELECTs
content = content.replace('SELECT id, cedula, ruc, nombre, ', 'SELECT id, cedula, ruc, nombres, ')
content = content.replace('SELECT id, cedula, nombre, ', 'SELECT id, cedula, nombres, ')

# Fix the zero issue in buscar_micro_auto
content = content.replace('if res[8]: e_info_cargas.insert(0, str(res[8]))', 'if res[8] is not None: e_info_cargas.insert(0, str(res[8]))')
content = content.replace('if res[13]: e_info_egr.insert(0, str(res[13]))', 'if res[13] is not None: e_info_egr.insert(0, str(res[13]))')
content = content.replace('if res[14]: lbl_total_val.configure(text=formatear_float_str(res[14]))', 'if res[14] is not None: lbl_total_val.configure(text=formatear_float_str(res[14]))')
content = content.replace('if res[9]: e_info_ing1.insert(0, f"{res[9]:.2f} / {res[10] if res[10] else \'\'}")', 'if res[9] is not None: e_info_ing1.insert(0, f"{res[9]:.2f} / {res[10] if res[10] else \'\'}")')
content = content.replace('if res[11]: e_info_ing2.insert(0, f"{res[11]:.2f} / {res[12] if res[12] else \'\'}")', 'if res[11] is not None: e_info_ing2.insert(0, f"{res[11]:.2f} / {res[12] if res[12] else \'\'}")')
content = content.replace('if res[21]: e_info_score.insert(0, str(res[21]))', 'if res[21] is not None: e_info_score.insert(0, str(res[21]))')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced microcredito bugs successfully.")
