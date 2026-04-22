import re

file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. In buscar_micro_auto, load 'apertura' instead of 'numero_carpeta'
# The SELECT query is: SELECT cedula, nombres, ruc, numero_carpeta, valor_apertura, fecha_registro
# Let's replace 'numero_carpeta' with 'apertura'
content = content.replace('SELECT cedula, nombres, ruc, numero_carpeta, valor_apertura', 'SELECT cedula, nombres, ruc, apertura, valor_apertura')

# 2. In buscar_micro_auto, don't lock e_n_apertura_micro, e_val_apertura_micro, e_f_apertura_micro if Admin
# Find the line where it locks them:
# e_n_apertura_micro.configure(state='readonly') -> we only want this if not admin
content = content.replace("e_n_apertura_micro.configure(state='readonly')", "if NIVEL_ACCESO not in ['Administrador', 'admin']: e_n_apertura_micro.configure(state='readonly')")
content = content.replace("e_val_apertura_micro.configure(state='readonly')", "if NIVEL_ACCESO not in ['Administrador', 'admin']: e_val_apertura_micro.configure(state='readonly')")
content = content.replace("e_f_apertura_micro.configure(state='readonly')", "if NIVEL_ACCESO not in ['Administrador', 'admin']: e_f_apertura_micro.configure(state='readonly')")

# Wait, there's another loop that locks e_n_apertura_micro at the beginning of buscar_micro_auto:
# for e in [e_n_apertura_micro, e_f_apertura_micro, e_info_dir, ...]:
#     if e != e_val_apertura_micro: e.configure(state='readonly')
# Let's replace that to not lock if admin.
content = content.replace("if e != e_val_apertura_micro: e.configure(state='readonly')", "if e != e_val_apertura_micro:\n                if NIVEL_ACCESO not in ['Administrador', 'admin']: e.configure(state='readonly')")

# 3. In guardar_microcredito, save e_n_apertura_micro and e_f_apertura_micro
# Find: cursor.execute("UPDATE Clientes SET valor_apertura = %s, producto = %s WHERE cedula = %s", (val_apertura, status_micro_actual, cedula_micro_actual))
# Replace with one that also updates apertura and fecha_registro.
new_update = """
        apertura_val = e_n_apertura_micro.get()
        fecha_aper_val = e_f_apertura_micro.get()
        cursor.execute("UPDATE Clientes SET valor_apertura = %s, producto = %s, apertura = %s, fecha_registro = %s WHERE cedula = %s", (val_apertura, status_micro_actual, apertura_val, fecha_aper_val, cedula_micro_actual))
"""
content = content.replace('cursor.execute("UPDATE Clientes SET valor_apertura = %s, producto = %s WHERE cedula = %s", (val_apertura, status_micro_actual, cedula_micro_actual))', new_update)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed microcredito editable fields.")
