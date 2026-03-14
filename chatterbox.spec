# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE

block_cipher = None

a = Analysis(
    ['chatterbox_client.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6.sip',
        'numpy',
        'pyaudio',
        'keyboard',
        'requests',
        'pyautogui',
        'pyperclip'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pandas', 'tkinter'], # Exclude heavy unused modules
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Chatterbox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # Use UPX compression if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # Hide the terminal window on Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico' # Uncomment and provide an .ico file if desired
)
