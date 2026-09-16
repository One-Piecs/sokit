#!/usr/bin/env python3
"""Draw the sokit application icon.

The original artwork is a 32x32 png (a blue network hub), which looks blurry
when scaled up. This script redraws it as a flat macOS style icon: a rounded
square ("squircle") with a light blue gradient and the same blue hub in the
middle. Everything is drawn 4x oversized and then downscaled, so edges stay
clean at every size, including 16x16.

usage: make-icon.py [repo root]

outputs (all relative to the repo root):
    build/macosx/sokit-1024.png      master artwork
    build/macosx/icon.iconset/*.png  apple iconset
    build/macosx/sokit.icns          macOS icon (packed by icns.py)
    src/sokit/sokit.png              icon used by the application and Linux
    src/sokit/sokit.ico              Windows icon
"""

import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageOps

CANVAS = 1024          # final canvas size
SUPER = 4              # supersampling factor while drawing
PADDING = 100          # apple style margin around the rounded square
RADIUS = 185           # corner radius of the rounded square

TOP = (88, 162, 248)       # tile gradient, top
BOTTOM = (22, 86, 190)     # tile gradient, bottom
EDGE = (16, 66, 146)       # tile border

NODE_TOP = (255, 255, 255)     # hub gradient, top
NODE_BOTTOM = (226, 238, 255)  # hub gradient, bottom
LINK = (255, 255, 255, 120)    # spokes between the nodes

SPOKE_STEP = 0.024   # spoke width, relative to the tile
NODE_STEP = 0.130    # middle node radius, relative to the tile
RING_STEP = 0.315    # distance of the outer nodes, relative to the tile
OUTER_STEP = 0.068   # outer node radius, relative to the tile


def corner_curve(radius, samples=180, exponent=4.2):
    """Points of a squircle corner, from (radius, 0) to (0, radius)."""
    pts = []
    for i in range(samples + 1):
        t = (math.pi / 2) * i / samples
        u = radius * math.cos(t) ** (2.0 / exponent)
        v = radius * math.sin(t) ** (2.0 / exponent)
        pts.append((u, v))
    return pts


def squircle_points(size, radius, samples=180):
    """Outline of a rounded square with continuous curvature corners."""
    half = size / 2.0
    a = half - radius          # corner centre offset
    curve = corner_curve(radius, samples)
    pts = []

    pts += [(-a, -half), (a, -half)]                          # top edge
    pts += [(a + u, -a - v) for u, v in reversed(curve)]      # top right corner
    pts += [(half, -a), (half, a)]                            # right edge
    pts += [(a + u, a + v) for u, v in curve]                 # bottom right corner
    pts += [(a, half), (-a, half)]                            # bottom edge
    pts += [(-a - u, a + v) for u, v in reversed(curve)]      # bottom left corner
    pts += [(-half, a), (-half, -a)]                          # left edge
    pts += [(-a - u, -a - v) for u, v in curve]               # top left corner

    return pts


def vertical_gradient(size, top, bottom):
    ramp = Image.linear_gradient("L").resize((size, size), Image.BILINEAR)
    return ImageOps.colorize(ramp, black=top, white=bottom).convert("RGB")


def circle_mask(size, cx, cy, radius):
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=255)
    return mask


def draw_master():
    work = CANVAS * SUPER
    tile = CANVAS - 2 * PADDING
    shape = squircle_points(tile, RADIUS)

    # --- the rounded square with its gradient ------------------------------
    icon = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    body = Image.new("L", (work, work), 0)
    ImageDraw.Draw(body).polygon(
        [((x + CANVAS / 2.0) * SUPER, (y + CANVAS / 2.0) * SUPER) for x, y in shape],
        fill=255,
    )
    icon.paste(vertical_gradient(work, TOP, BOTTOM), (0, 0), body)

    # --- the hub: centre node, ring of nodes and the spokes -----------------
    layer = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    cx = cy = CANVAS / 2.0 * SUPER
    ring = RING_STEP * tile
    spokes = []
    nodes = []
    for i in range(8):
        angle = -math.pi / 2 + i * math.pi / 4
        nodes.append(
            (
                cx + ring * math.cos(angle) * SUPER,
                cy + ring * math.sin(angle) * SUPER,
            )
        )
    nodes.insert(0, (cx, cy))

    spoke_width = max(2, int(SPOKE_STEP * tile * SUPER))
    for x, y in nodes[1:]:
        draw.line([cx, cy, x, y], fill=LINK, width=spoke_width)

    nodes_gradient = vertical_gradient(work, NODE_TOP, NODE_BOTTOM)
    nodes_layer = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    for i, (x, y) in enumerate(nodes):
        radius = (NODE_STEP if i == 0 else OUTER_STEP) * tile * SUPER
        mask = circle_mask(work, x, y, radius)
        nodes_layer.paste(nodes_gradient, (0, 0), mask)

    icon = Image.alpha_composite(icon, layer)
    icon = Image.alpha_composite(icon, nodes_layer)

    # --- a hair line around the tile, clipped to the shape ------------------
    outline = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    border = [
        ((x + CANVAS / 2.0) * SUPER, (y + CANVAS / 2.0) * SUPER) for x, y in shape
    ]
    border.append(border[0])
    ImageDraw.Draw(outline).line(
        border,
        fill=EDGE + (255,),
        width=max(2, int(SUPER * 2)),
        joint="curve",
    )
    icon = Image.alpha_composite(icon, Image.composite(outline, Image.new("RGBA", (work, work), (0, 0, 0, 0)), body))

    return icon.resize((CANVAS, CANVAS), Image.LANCZOS)


def write_png(image, path, size):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    image.resize((size, size), Image.LANCZOS).save(path)


def main(argv):
    root = argv[1] if len(argv) > 1 else os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    here = os.path.join(root, "build", "macosx")

    master = draw_master()
    master.save(os.path.join(here, "sokit-1024.png"))

    iconset = os.path.join(here, "icon.iconset")
    for size in (16, 32, 128, 256, 512):
        write_png(master, os.path.join(iconset, "icon_%dx%d.png" % (size, size)), size)
        write_png(
            master,
            os.path.join(iconset, "icon_%dx%d@2x.png" % (size, size)),
            size * 2,
        )

    subprocess.check_call(
        [sys.executable, os.path.join(here, "icns.py"), iconset, os.path.join(here, "sokit.icns")]
    )

    write_png(master, os.path.join(root, "src", "sokit", "sokit.png"), 256)
    master.resize((256, 256), Image.LANCZOS).save(
        os.path.join(root, "src", "sokit", "sokit.ico"),
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )

    print("icons written to %s" % here)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
