#!/bin/bash
# Run after: pyinstaller videotranscriber.spec
set -e

APP="dist/VideoTranscriber.app"
DMG="dist/ViScriber.dmg"

create-dmg \
  --volname "Video Transcriber" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "VideoTranscriber.app" 175 190 \
  --hide-extension "VideoTranscriber.app" \
  --app-drop-link 425 190 \
  "$DMG" \
  "$APP"

echo "DMG created: $DMG"
