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
	for q in /opt/homebrew/opt/qtbase/bin/qmake \
	         /opt/homebrew/opt/qt/bin/qmake \
	         /usr/local/opt/qtbase/bin/qmake \
	         /usr/local/opt/qt/bin/qmake \
	         qmake6 qmake; do
		if command -v "$q" >/dev/null 2>&1; then
			QMAKE=$q
			break
		fi
	done
fi

if [ -z "$QMAKE" ]; then
	echo "qmake not found. install Qt first, e.g. 'brew install qtbase'" >&2
	exit 1
fi

qtbin=$(dirname "$QMAKE")
MACDEPLOYQT=${MACDEPLOYQT:-$qtbin/macdeployqt}
LRELEASE=${LRELEASE:-$qtbin/lrelease}

# --- application icon -----------------------------------------------------
# the icon is drawn at high resolution and packed into an .icns container
if [ ! -f "$here/sokit.icns" ]; then
	echo "==> generating sokit.icns"
	python3 "$here/make-icon.py" "$root"
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
# Qt modules can live in separate prefixes (qtbase, qtsvg, ...), so the Qt
# installation's lib dir is handed to macdeployqt explicitly
qtlibs=$("$QMAKE" -query QT_INSTALL_LIBS 2>/dev/null || true)
[ -n "$qtlibs" ] || qtlibs=$(cd "$qtbin/.." && pwd)/lib

"$MACDEPLOYQT" "$app" -always-overwrite -libpath="$qtlibs"

# QtSvg is a separate module: if it was not bundled, drop the icon plugin
# that depends on it instead of shipping a plugin that cannot be loaded
if [ ! -d "$app/Contents/Frameworks/QtSvg.framework" ]; then
	rm -rf "$app/Contents/PlugIns/iconengines/libqsvgicon.dylib"
fi

echo "==> signing (ad-hoc)"
codesign --force --deep --sign - "$app"
codesign --verify --deep "$app"

echo
echo "built: $app"
echo "run:   open \"$app\""
