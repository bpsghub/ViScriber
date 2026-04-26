#!/bin/bash
# Wraps the PyInstaller --onefile output in an AppImage
# Requires: appimagetool (download from https://github.com/AppImage/AppImageKit/releases)
set -e

BINARY="dist/VideoTranscriber"
APPDIR="dist/VideoTranscriber.AppDir"

mkdir -p "$APPDIR/usr/bin"
cp "$BINARY" "$APPDIR/usr/bin/VideoTranscriber"
chmod +x "$APPDIR/usr/bin/VideoTranscriber"

cp resources/icon.png "$APPDIR/VideoTranscriber.png"

cat > "$APPDIR/VideoTranscriber.desktop" <<EOF
[Desktop Entry]
Name=Video Transcriber
Exec=VideoTranscriber
Icon=VideoTranscriber
Type=Application
Categories=AudioVideo;
EOF

cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/bash
exec "$APPDIR/usr/bin/VideoTranscriber" "$@"
EOF
chmod +x "$APPDIR/AppRun"

ARCH=x86_64 appimagetool "$APPDIR" dist/VideoTranscriber-x86_64.AppImage
echo "AppImage created: dist/VideoTranscriber-x86_64.AppImage"
