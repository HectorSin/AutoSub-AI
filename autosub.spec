# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [
    ('src/prompts', 'src/prompts'),
    ('src/gui', 'src/gui'),
    ('assets', 'assets'),
    ('.streamlit', '.streamlit'),
    ('src/utils', 'src/utils'),
    ('src/core', 'src/core'),
]
binaries = []
hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'faster_whisper',
    'keyring',
    'pystray',
    'PIL',
    'google.generativeai',
    'pydantic',
    'structlog',
    'ffmpeg',
    'engineio.async_drivers.threading',
    'nvidia.cudnn',
    'nvidia.cublas',
]

# Collect data for packages that might need it
tmp_ret = collect_all('faster_whisper')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('streamlit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

block_cipher = None

a = Analysis(
    ['src/gui_launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='AutoSub-AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoSub-AI',
)
