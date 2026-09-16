#!/usr/bin/env python3
"""Pack an .iconset directory into an .icns file.

Only the python standard library is used, so it works on every macOS version
(sips/iconutil can refuse to write icns on newer systems).

usage: icns.py <iconset dir> <out.icns>

The iconset directory uses the usual naming, missing files are skipped:
    icon_16x16.png  icon_16x16@2x.png  icon_32x32.png  ...  icon_512x512@2x.png
"""

import os
import struct
import sys

# OSType -> (file name, pixel size)
IMAGES = [
    (b"icp4", "icon_16x16.png", 16),
    (b"ic11", "icon_16x16@2x.png", 32),
    (b"icp5", "icon_32x32.png", 32),
    (b"ic12", "icon_32x32@2x.png", 64),
    (b"icp6", "icon_64x64.png", 64),
    (b"ic07", "icon_128x128.png", 128),
    (b"ic13", "icon_128x128@2x.png", 256),
    (b"ic08", "icon_256x256.png", 256),
    (b"ic14", "icon_256x256@2x.png", 512),
    (b"ic09", "icon_512x512.png", 512),
    (b"ic10", "icon_512x512@2x.png", 1024),
]


def png_size(data):
    """Return (width, height) of a png, or None if it is not a png."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2

    src, dst = argv[1], argv[2]
    body = b""
    count = 0

    for ostype, name, size in IMAGES:
        path = os.path.join(src, name)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as fp:
            data = fp.read()
        if png_size(data) != (size, size):
            print("skipping %s, not a %dx%d png" % (name, size, size), file=sys.stderr)
            continue
        body += ostype + struct.pack(">I", len(data) + 8) + data
        count += 1

    if not body:
        print("no usable png found in %s" % src, file=sys.stderr)
        return 1

    with open(dst, "wb") as fp:
        fp.write(b"icns" + struct.pack(">I", len(body) + 8) + body)

    print("wrote %s (%d images)" % (dst, count))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
