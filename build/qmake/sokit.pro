# ----------------------------------------------------
# sokit.pro -- cross platform qmake project (Qt 5)
#
#   Windows          -> bin/win/sokit.exe
#   Linux            -> bin/linux/sokit
#   macOS            -> bin/macos/sokit.app
#
# usage:  cd build/qmake && qmake sokit.pro && make     (nmake on Windows)
# ----------------------------------------------------

TEMPLATE = app
TARGET = sokit

QT += gui widgets network
CONFIG += release thread
CONFIG -= debug_and_release

DEFINES += QT_NETWORK_LIB

win32:      PLAT = win
unix:!macx: PLAT = linux
macx:       PLAT = macos

DESTDIR = ../../bin/$$PLAT
MOC_DIR = ../../tmp/$$PLAT
UI_DIR = ../../tmp/$$PLAT
RCC_DIR = ../../tmp/$$PLAT
OBJECTS_DIR = ../../tmp/$$PLAT

INCLUDEPATH += . ../../tmp ../../tmp/$$PLAT ../../src/sokit
DEPENDPATH += .

HEADERS += ../../src/sokit/resource.h \
    ../../src/sokit/setting.h \
    ../../src/sokit/toolkit.h \
    ../../src/sokit/baseform.h \
    ../../src/sokit/clientform.h \
    ../../src/sokit/clientskt.h \
    ../../src/sokit/helpform.h \
    ../../src/sokit/logger.h \
    ../../src/sokit/main.h \
    ../../src/sokit/notepadform.h \
    ../../src/sokit/transferskt.h \
    ../../src/sokit/transferform.h \
    ../../src/sokit/serverskt.h \
    ../../src/sokit/serverform.h
SOURCES += ../../src/sokit/baseform.cpp \
    ../../src/sokit/clientform.cpp \
    ../../src/sokit/clientskt.cpp \
    ../../src/sokit/helpform.cpp \
    ../../src/sokit/logger.cpp \
    ../../src/sokit/main.cpp \
    ../../src/sokit/notepadform.cpp \
    ../../src/sokit/serverform.cpp \
    ../../src/sokit/serverskt.cpp \
    ../../src/sokit/setting.cpp \
    ../../src/sokit/toolkit.cpp \
    ../../src/sokit/transferform.cpp \
    ../../src/sokit/transferskt.cpp
FORMS += ../../src/sokit/clientform.ui \
    ../../src/sokit/helpform.ui \
    ../../src/sokit/serverform.ui \
    ../../src/sokit/transferform.ui
TRANSLATIONS += ../../src/sokit/sokit.ts
RESOURCES += ../../src/sokit/icons.qrc

# the UI language file is placed next to the binary / inside the bundle
QMAKE_POST_LINK = $$[QT_INSTALL_BINS]/lrelease $$PWD/../../src/sokit/sokit.ts -qm $$DESTDIR/sokit.lan

win32 {
    RC_FILE = ../../src/sokit/sokit.rc
    RC_INCLUDEPATH += ../../src/sokit
    LIBS += -lWs2_32 -lWinmm -lImm32
}

macx {
    CONFIG += app_bundle
    QMAKE_MACOSX_DEPLOYMENT_TARGET = 12.0
    QMAKE_INFO_PLIST = $$PWD/Info.plist
    ICON = $$PWD/../macosx/sokit.icns

    QMAKE_POST_LINK += && mkdir -p $$DESTDIR/sokit.app/Contents/Resources \
        && cp -f $$DESTDIR/sokit.lan $$DESTDIR/sokit.app/Contents/Resources/
}

OTHER_FILES += \
    ../../src/sokit/sokit.ts \
    ../../LICENSE \
    ../../README.md
