# Build with: pyinstaller --clean --noconfirm GestureControl.spec
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

project = Path(SPECPATH)
hiddenimports = collect_submodules("mediapipe")

a = Analysis(
    ["src/gesture_control/__main__.py"],
    pathex=[str(project / "src")],
    binaries=[],
    datas=[(str(project / "models" / "hand_landmarker.task"), "models")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="GestureControl",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
