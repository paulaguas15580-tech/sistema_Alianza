import re

file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("if val['cargas_familiares']:", "if val['cargas_familiares'] is not None:")
content = content.replace("if val['ingresos_mensuales']:", "if val['ingresos_mensuales'] is not None:")
content = content.replace("if val['ingresos_mensuales_2']:", "if val['ingresos_mensuales_2'] is not None:")
content = content.replace("if val['egresos']:", "if val['egresos'] is not None:")
content = content.replace("if val['score_buro']:", "if val['score_buro'] is not None:")
content = content.replace("if val['valor_apertura']:", "if val['valor_apertura'] is not None:")

content = content.replace("if val['terreno']:", "if val['terreno'] is not None:")
content = content.replace("if val['casa_dep']:", "if val['casa_dep'] is not None:")
content = content.replace("if val['local']:", "if val['local'] is not None:")
content = content.replace("if val['cartera castigada']:", "if val['cartera castigada'] is not None:")
content = content.replace("if val['demanda judicial']:", "if val['demanda judicial'] is not None:")
content = content.replace("if val['problemas justicia']:", "if val['problemas justicia'] is not None:")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced zero-failing checks successfully.")
