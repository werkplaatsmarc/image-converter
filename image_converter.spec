# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

# PyInstaller's numpy-hook mist bij sommige numpy-versies interne submodules
# (bv. numpy._core._exceptions), wat resulteert in een ImportError in de
# gebouwde .exe. Expliciet alle numpy-submodules meenemen lost dit op.
# scipy._cyutility is een vergelijkbaar geval (gebruikt door pymatting/rembg).
hidden_imports = collect_submodules('numpy') + ['scipy._cyutility']

# Diverse rembg-afhankelijkheden vragen bij het importeren hun eigen
# versienummer op via importlib.metadata (bv. pymatting, imageio). Zonder de
# bijbehorende .dist-info-metadata gebundeld crasht dat met
# "PackageNotFoundError" in de gebouwde .exe.
metadata_packages = [
    'pymatting', 'imageio', 'numba', 'tqdm', 'jsonschema', 'networkx',
    'scikit-image', 'onnxruntime', 'scipy', 'numpy', 'pillow', 'llvmlite',
    'lazy_loader', 'tifffile', 'pooch', 'rembg', 'referencing', 'rpds-py',
    'jsonschema-specifications',
]
datas = []
for _pkg in metadata_packages:
    try:
        datas += copy_metadata(_pkg)
    except Exception:
        pass

a = Analysis(
    ['image_converter.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    a.binaries,
    a.datas,
    [],
    name='image_converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['converter.ico'],
)
