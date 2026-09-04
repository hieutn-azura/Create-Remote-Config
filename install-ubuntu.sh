#!/usr/bin/env bash
# Cài "Ads Config Generator" vào menu ứng dụng Ubuntu (không cần cài Python).
set -e
BIN=ads_config_generator
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.local/bin"
APPS="$HOME/.local/share/applications"
mkdir -p "$DEST" "$APPS"
install -m755 "$HERE/$BIN" "$DEST/$BIN"
cat > "$APPS/ads-config-generator.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Ads Config Generator
Comment=Sinh JSON remote config quảng cáo
Exec=$DEST/$BIN
Terminal=false
Categories=Utility;Development;
EOF
echo "✓ Đã cài. Mở từ menu ứng dụng 'Ads Config Generator', hoặc chạy: $DEST/$BIN"
echo "  (đảm bảo \$HOME/.local/bin nằm trong PATH nếu chạy bằng lệnh)"
