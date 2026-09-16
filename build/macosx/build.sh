#!/bin/sh
# ----------------------------------------------------
# build.sh -- build sokit.app (macOS application bundle)
#
# usage:  ./build.sh
# needs:  Qt 5 (qmake, lrelease, macdeployqt) and the Xcode command line tools
# result: ../../bin/macos/sokit.app  (Qt libraries bundled, ad-hoc signed)
# ----------------------------------------------------

set -e

here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)

# --- toolchain ------------------------------------------------------------
if [ -z "$QMAKE" ]; then
	for q in /opt/homebrew/opt/qt@5/bin/qmake /usr/local/opt/qt@5/bin/qmake qmake; do
		if command -v "$q" >/dev/null 2>&1; then
			QMAKE=$q
			break
		fi
	done
fi

if [ -z "$QMAKE" ]; then
	echo "qmake not found. install Qt 5 first, e.g. 'brew install qt@5'" >&2
	exit 1
fi

qtbin=$(dirname "$QMAKE")
MACDEPLOYQT=${MACDEPLOYQT:-$qtbin/macdeployqt}
LRELEASE=${LRELEASE:-$qtbin/lrelease}

# --- application icon -----------------------------------------------------
# sokit.png is only 32x32, so it is scaled up into an .icns container
if [ ! -f "$here/sokit.icns" ]; then
	echo "==> generating sokit.icns"
	rm -rf "$here/icon.iconset"
	mkdir -p "$here/icon.iconset"
	for s in 16 32 128 256 512; do
		sips -z $s $s "$root/src/sokit/sokit.png" --out "$here/icon.iconset/icon_${s}x${s}.png" >/dev/null
		sips -z $((s * 2)) $((s * 2)) "$root/src/sokit/sokit.png" \
			--out "$here/icon.iconset/icon_${s}x${s}@2x.png" >/dev/null
	done
	python3 "$here/icns.py" "$here/icon.iconset" "$here/sokit.icns"
fi

# --- compile --------------------------------------------------------------
cd "$here/../qmake"
echo "==> qmake ($QMAKE)"
"$QMAKE" sokit.pro CONFIG+=sdk_no_version_check

echo "==> make"
make -j"$(sysctl -n hw.ncpu)"

# macdeployqt rewrites the load commands of the binary, so the app has to be
# signed again afterwards or macOS refuses to start it on Apple Silicon
app="$root/bin/macos/sokit.app"

echo "==> bundling Qt frameworks"
"$MACDEPLOYQT" "$app" -always-overwrite

echo "==> signing (ad-hoc)"
codesign --force --deep --sign - "$app"
codesign --verify --deep "$app"

echo
echo "built: $app"
echo "run:   open \"$app\""
