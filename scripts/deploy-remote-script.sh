#!/bin/bash
# Deploy AbletonBridge Remote Script to Ableton's install locations.
# Run after any change to AbletonBridge_Remote_Script/*.
# After deploying, toggle the control surface off/on in Ableton Preferences
# (Link, Tempo & MIDI) to reload — no Ableton restart needed.

set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)/AbletonBridge_Remote_Script"
DEST1="$HOME/Music/Ableton/User Library/Remote Scripts/AbletonBridge"
DEST2="$HOME/Library/Preferences/Ableton/Live 12.2.7/User Remote Scripts/AbletonBridge"

if [ ! -d "$SRC" ]; then
    echo "ERROR: source not found at $SRC" >&2
    exit 1
fi

deployed=0
for DEST in "$DEST1" "$DEST2"; do
    if [ -d "$DEST" ]; then
        find "$DEST" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
        rsync -av --exclude='__pycache__' "$SRC/" "$DEST/"
        echo "✓ Deployed to $DEST"
        deployed=$((deployed + 1))
    fi
done

if [ "$deployed" -eq 0 ]; then
    echo "WARNING: no install locations found. Expected one of:"
    echo "  $DEST1"
    echo "  $DEST2"
    exit 1
fi

echo ""
echo "Done. Toggle AbletonBridge off/on in Ableton Preferences to reload."
