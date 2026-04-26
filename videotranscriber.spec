# videotranscriber.spec
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect faster_whisper and ctranslate2 data files
datas = []
datas += collect_data_files("faster_whisper")
datas += collect_data_files("ctranslate2")

# Bundle ffmpeg binary for current platform
if sys.platform.startswith("win"):
    ffmpeg_src = os.path.join("resources", "ffmpeg", "win", "ffmpeg.exe")
    ffmpeg_dest = os.path.join("resources", "ffmpeg", "win")
elif sys.platform == "darwin":
    ffmpeg_src = os.path.join("resources", "ffmpeg", "mac", "ffmpeg")
    ffmpeg_dest = os.path.join("resources", "ffmpeg", "mac")
else:
    ffmpeg_src = os.path.join("resources", "ffmpeg", "linux", "ffmpeg")
    ffmpeg_dest = os.path.join("resources", "ffmpeg", "linux")

if os.path.exists(ffmpeg_src):
    datas.append((ffmpeg_src, ffmpeg_dest))

a = Analysis(
    ["src/main.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "faster_whisper",
        "ctranslate2",
        "customtkinter",
        "tkinterdnd2",
        "anthropic",
        "openai",
        "httpx",
        "PIL",
    ] + collect_submodules("faster_whisper") + collect_submodules("ctranslate2"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if sys.platform == "darwin":
    exe = EXE(
        pyz, a.scripts, [],
        exclude_binaries=True,
        name="VideoTranscriber",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        icon="resources/icon.icns",
    )
    coll = COLLECT(
        exe, a.binaries, a.zipfiles, a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name="VideoTranscriber",
    )
    app = BUNDLE(
        coll,
        name="VideoTranscriber.app",
        icon="resources/icon.icns",
        bundle_identifier="com.videotranscriber.app",
        info_plist={
            "NSMicrophoneUsageDescription": "Used for local video transcription.",
            "CFBundleShortVersionString": "1.0.0",
        },
    )
else:
    exe = EXE(
        pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
        name="VideoTranscriber",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        icon="resources/icon.ico" if sys.platform.startswith("win") else "resources/icon.png",
    )
