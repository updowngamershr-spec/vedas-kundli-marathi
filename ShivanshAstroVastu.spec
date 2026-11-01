# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('reports', 'reports'),
    ('data/world_cities.db', 'data'),
    ('data/lal_kitab_hindi_cleaned.json', 'data'),
    ('app_icon.ico', '.'),
    ('assets', 'assets'),
]

hidden_imports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'pydantic',
    'astronomy',
    'pypdf',
    'PIL',
    'webview',
    'webview.platforms.winforms',
    'clr',
    'pythonnet',
    'engine.ashtakavarga_shadbala',
    'engine.cities',
    'engine.dashas',
    'engine.ephemeris',
    'engine.knowledge_predictions',
    'engine.kp_lal_kitab',
    'engine.kundli_milan',
    'engine.milan_dossier',
    'engine.lal_kitab_corpus',
    'engine.master_kundli',
    'engine.report_html_pdf',
    'engine.svg_charts',
    'engine.vargas_avkahada',
    'engine.varshaphal_sadesati_yogas',
    'engine.remedy_pages',
    'engine.marathi_engine',
    'crm_db',
    'app',
]

a = Analysis(
    ['desktop_main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas', 'unittest', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ShivanshAstroVastu',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='ShivanshAstroVastu',
)
