"""Flatten the legacy product screenshots (assets/img/screens/) into the site's restrained style.

The six original screens were exported with a colored gradient panel, a decorative circle, and floating
"notification" chips drawn into the image. This repaints the panel in one flat neutral, removes the chips,
restores the top bar where a chip covered it (copied from a screen whose top bar is clean), and outlines the
app window with a hairline. File names and sizes stay the same, so no page markup changes.
Originals: archive/vibecode/screens-original/. Usage: python scripts/clean-screens.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), "..")
SCREENS = os.path.join(ROOT, "assets", "img", "screens")
ORIGINALS = os.path.join(ROOT, "archive", "vibecode", "screens-original")
LEGACY = ["dashboard", "home-collection", "sample-tracking", "turnaround-tracking", "pathology-imaging-reporting", "business-insights"]
WIDE_CHIP = {"pathology-imaging-reporting"}
TOP_CHIP = {"dashboard", "turnaround-tracking", "business-insights"}  # a chip overlaps the app's top bar
PANEL = (241, 240, 235)      # flat warm neutral behind every screen (matches scripts/screens.mjs)
EDGE = (221, 227, 223)       # hairline around the app window
X0 = Y0 = 209                # app window's top-left corner at 2320 px
R = 42                       # its corner radius
SIDEBAR_RIGHT = 628          # last white column before the sidebar border

def clean(name):
    im = Image.open(os.path.join(ORIGINALS, f"{name}-2320.webp")).convert("RGB")
    W, H = im.size
    d = ImageDraw.Draw(im)
    # Bottom-left chip: it sits over empty sidebar space, so paint the sidebar white again
    d.rectangle([X0, 1560, SIDEBAR_RIGHT, H], fill=(255, 255, 255))
    if name in WIDE_CHIP:  # this chip also ran past the sidebar onto the empty page background: repaint that, then the border
        border, page = im.getpixel((SIDEBAR_RIGHT + 2, 1500)), im.getpixel((900, 1650))
        d.rectangle([SIDEBAR_RIGHT + 4, 1605, W, H], fill=page)  # nothing sits below the cards on this screen
        d.rectangle([SIDEBAR_RIGHT + 1, 1560, SIDEBAR_RIGHT + 3, H], fill=border)
    # Top-right chip: copy the same strip of top bar from a screen without one
    if name in TOP_CHIP:
        donor = Image.open(os.path.join(ORIGINALS, "home-collection-2320.webp")).convert("RGB")
        im.paste(donor.crop((1640, Y0, W, 337)), (1640, Y0))
    # Panel: one flat color around the app window, including outside its rounded corner
    d.rectangle([0, 0, W, Y0 - 1], fill=PANEL)
    d.rectangle([0, 0, X0 - 1, H], fill=PANEL)
    mask = Image.new("L", (R, R), 255)
    ImageDraw.Draw(mask).pieslice([0, 0, 2 * R, 2 * R], 180, 270, fill=0)
    im.paste(Image.new("RGB", (R, R), PANEL), (X0, Y0), mask)
    d.rounded_rectangle([X0, Y0, W + 2 * R, H + 2 * R], radius=R, outline=EDGE, width=2)
    return im

if __name__ == "__main__":
    for name in LEGACY:
        im = clean(name)
        for w in (2320, 1600, 1200, 800, 640, 480):
            out = os.path.join(SCREENS, f"{name}-{w}.webp")
            if not os.path.exists(out):
                continue
            ow, oh = Image.open(out).size
            (im if w == im.width else im.resize((ow, oh), Image.LANCZOS)).save(out, "WEBP", quality=82 if w >= 1600 else 80, method=6)
        print("cleaned", name)
