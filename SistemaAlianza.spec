# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('Logo Face.jpg', '.'), ('background.jpg', '.'), ('bg_metal_brushed.jpg', '.'), ('bg_microcredito.jpg', '.'), ('btn_bg.jpg', '.'), ('fondo gestion.jpg', '.'), ('cartera_icon.png', '.'), ('clientes_icon.png', '.'), ('consultas_icon.png', '.'), ('documentos_icon.png', '.'), ('icono_guardar.png', '.'), ('informes_icon.png', '.'), ('intermediacion_icon.png', '.'), ('logo_transparent.png', '.'), ('microcredito_icon.png', '.'), ('rehabilitacion_icon.png', '.'), ('salir_icon.png', '.'), ('usuarios_icon.png', '.')]
binaries = []
hiddenimports = ['reportlab.graphics.barcode.code128', 'reportlab.graphics.barcode.code93', 'reportlab.graphics.barcode.code39', 'reportlab.graphics.barcode.usps', 'reportlab.graphics.barcode.usps4cb', 'reportlab.graphics.barcode.ecc200datamatrix', 'reportlab.graphics.barcode.usps4s']
tmp_ret = collect_all('reportlab')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('xhtml2pdf')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['basededatos_v3.0.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SistemaAlianza',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SistemaAlianza',
)
