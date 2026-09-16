# Sokit

Sokit is a TCP & UDP package send/receive/transfer tool, Write in c++ with qt under Windows and Linux.





Build
-----

The cross platform project is ``build/qmake/sokit.pro`` (Qt 5)::

	cd build/qmake && qmake sokit.pro && make        (nmake on Windows)

Output: ``bin/win/sokit.exe``, ``bin/linux/sokit`` or ``bin/macos/sokit.app``.

macOS, one command -- builds the app bundle with the Qt frameworks inside and
signs it, so it runs on a Mac without Qt installed::

	brew install qt@5
	./build/macosx/build.sh
	open bin/macos/sokit.app

Legacy project files (Qt 4 era) are still in ``build/win32/vs2010`` and
``build/linux86/qtcreator``.

The icon is drawn by ``build/macosx/make-icon.py`` (it writes the macOS
``.icns``, the Windows ``.ico`` and ``src/sokit/sokit.png``), run it after
changing the artwork in that script.

Every push builds Windows, Linux and macOS packages on GitHub Actions, see
``.github/workflows/build.yml``.

License
-------
Sokit is licensed under GNU GPLv3 - see the ``LICENSE`` file.
