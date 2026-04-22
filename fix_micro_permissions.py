import re

file_path = 'basededatos_v3.0.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Modify create_ref_group to assign buttons to globals
new_create_ref = """
    btn_save = ctk.CTkButton(f_header, text=f"💾 Guardar Ref {col+1}",
                             command=lambda: print("Guardar Ref", col+1),
                             fg_color="#28a745", hover_color="#218838", height=24, font=('Arial', 10, 'bold'))
    btn_save.pack(side='right')
    
    if col == 0:
        global btn_guardar_ref1
        btn_guardar_ref1 = btn_save
    else:
        global btn_guardar_ref2
        btn_guardar_ref2 = btn_save
"""
content = re.sub(r'btn_save = ctk\.CTkButton\(f_header, text=f"💾 Guardar Ref \{col\+1\}",.*?btn_save\.pack\(side=\'right\'\)', new_create_ref, content, flags=re.DOTALL)

# 2. Modify the main Guardar / Actualizar Todo button creation
old_btn_guardar = 'ctk.CTkButton(btn_frame, text="💾 Guardar / Actualizar Todo", command=guardar_microcredito, fg_color="#4F6D96", hover_color="#3A5271").pack(pady=15)'
new_btn_guardar = """
    global btn_guardar_micro_todo
    btn_guardar_micro_todo = ctk.CTkButton(btn_frame, text="💾 Guardar / Actualizar Todo", command=guardar_microcredito, fg_color="#4F6D96", hover_color="#3A5271")
    btn_guardar_micro_todo.pack(pady=15)
"""
content = content.replace(old_btn_guardar, new_btn_guardar)

# 3. Add function set_micro_state
state_func = """
def set_micro_state(state_str):
    for e in [e_m_ref1_rel, e_m_ref1_tiempo, e_m_ref1_dir, e_m_ref1_cargas,
              e_m_ref2_rel, e_m_ref2_tiempo, e_m_ref2_dir, e_m_ref2_cargas,
              e_m_ref1_nom, e_m_ref1_tel, e_m_ref1_fec, e_m_ref1_hor,
              e_m_ref2_nom, e_m_ref2_tel, e_m_ref2_fec, e_m_ref2_hor,
              c_m_ref1_viv, c_m_ref1_resp, c_m_ref2_viv, c_m_ref2_resp,
              t_obs_micro, t_obs_info_micro,
              e_f_desembolsado, e_f_negado_status, e_f_desistimiento, e_f_comite]:
        try:
            if hasattr(e, 'configure'): e.configure(state=state_str)
        except: pass
    
    try:
        btn_guardar_micro_todo.configure(state=state_str)
        btn_guardar_ref1.configure(state=state_str)
        btn_guardar_ref2.configure(state=state_str)
    except: pass

"""
# Add it before limpiar_form_micro
content = content.replace('def limpiar_form_micro():', state_func + '\ndef limpiar_form_micro():')

# 4. Modify limpiar_form_micro to enable everything
# Add set_micro_state('normal') at the end of limpiar_form_micro
content = content.replace('seleccionar_status(None)', "seleccionar_status(None)\n    set_micro_state('normal')")

# 5. Modify cargar_datos_micro to disable if not admin
disable_logic = """
        if len(row) > 31:
            e_f_desistimiento.delete(0, tk.END); e_f_desistimiento.insert(0, row[31] if row[31] else "")
            
        if NIVEL_ACCESO not in ['Administrador', 'admin']:
            set_micro_state('disabled')
        else:
            set_micro_state('normal')
"""
content = content.replace('''        if len(row) > 31:
            e_f_desistimiento.delete(0, tk.END); e_f_desistimiento.insert(0, row[31] if row[31] else "")''', disable_logic)


with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Permissions applied successfully.")
