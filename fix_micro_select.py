import re

file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_query = 'cursor.execute("SELECT * FROM Microcreditos WHERE cedula_cliente = %s", (cedula,))'
new_query = '''cursor.execute("""
        SELECT id, cedula_cliente, ruc, observaciones, observaciones_info,
               ref1_relacion, ref1_tiempo_conocer, ref1_direccion, ref1_tipo_vivienda, ref1_cargas, ref1_patrimonio, ref1_responsable,
               ref2_relacion, ref2_tiempo_conocer, ref2_direccion, ref2_tipo_vivienda, ref2_cargas, ref2_patrimonio, ref2_responsable,
               ref1_fecha, ref1_hora, ref1_nombre, ref1_telefono,
               ref2_fecha, ref2_hora, ref2_nombre, ref2_telefono,
               status, sub_status, fecha_desembolsado, fecha_negado, fecha_desistimiento, fecha_comite
        FROM Microcreditos WHERE cedula_cliente = %s
    """, (cedula,))'''

content = content.replace(old_query, new_query)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Microcreditos SELECT query order.")
