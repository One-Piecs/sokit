# Sokit

Sokit is a TCP & UDP package send/receive/transfer tool, Write in c++ with qt under Windows and Linux.





Build
-----

The cross platform project is ``build/qmake/sokit.pro`` (Qt 6, Qt 5.15 still
works)::

	cd build/qmake && qmake sokit.pro && make        (nmake on Windows)

Output: ``bin/win/sokit.exe``, ``bin/linux/sokit`` or ``bin/macos/sokit.app``.

macOS, one command -- builds the app bundle with the Qt frameworks inside and
signs it, so it runs on a Mac without Qt installed::

	brew install qtbase qttools
	./build/macosx/build.sh
	open bin/macos/sokit.app

Legacy project files (Qt 4 era) are still in ``build/win32/vs2010`` and
``build/linux86/qtcreator``.

The icon is drawn by ``build/macosx/make-icon.py`` (it writes the macOS
``.icns``, the Windows ``.ico`` and ``src/sokit/sokit.png``), run it after
changing the artwork in that script.

Every push builds Windows, Linux and macOS packages on GitHub Actions, see
``.github/workflows/build.yml``.

Several instances
-----------------

sokit can run more than once at the same time, which is handy when a few
connections have to be watched side by side. On macOS a double click on the
icon only brings up the window that is already open, so a second copy is
started from ``File / New Instance`` (Cmd-N) or from the command line::

	open -n bin/macos/sokit.app

Every instance keeps its own settings, notepad and log directory -- normally
``~/.sokit`` for the first one and ``~/.sokit-2``, ``~/.sokit-3`` ... for the
next ones (started from a writable directory the files stay in that directory,
as before, and the next instance uses ``<dir>-2``). A new instance starts from
a copy of the first instance's settings, and ``--instance NAME`` uses
``<dir>-NAME`` for a fixed profile. The window title shows which instance it
is.

License
-------
Sokit is licensed under GNU GPLv3 - see the ``LICENSE`` file.
