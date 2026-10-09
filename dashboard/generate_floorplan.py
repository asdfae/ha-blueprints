"""Make the isometric floorplan of the house as an SVG file.

Usage: python generate_floorplan.py <output.svg>

The ha-floorplan card uses the element IDs in this SVG:
- room-<area>: the floor of a room. The card sets the class "light-on" or "light-off".
- motion-<area>: a ring on the floor. The card sets the class "motion-on" or "motion-off".
- temp-<area>: a text. The card sets the temperature.

World axes (metres): x goes from the east wall to the west. y goes from the north
wall to the south. z goes up from the main floor (0.0 m). The camera is north-east
of the house. Thus, you see the north side and the east side.
"""
import math
import sys

S = 30.0
C30 = math.cos(math.radians(30))
OX, OY = 560.0, 600.0
W_IMG, H_IMG = 1200, 900

CYAN = "#00f0ff"
MAGENTA = "#ff2bd6"
YELLOW = "#fcee0a"
VIOLET = "#9d6bff"
GREEN = "#39ff88"
ORANGE = "#ff8a2b"

out = []


def P(x, y, z):
    return (OX + (x - y) * C30 * S, OY - (x + y) * 0.5 * S - z * S)


def poly(pts, fill="none", stroke="none", sw=1.0, op=1.0, extra=""):
    d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (P(*p) for p in pts))
    out.append(f'<polygon points="{d}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" '
               f'stroke-width="{sw}" stroke-linejoin="round" {extra}/>')


def line(a, b, stroke, sw=1.0, op=1.0, extra=""):
    (x1, y1), (x2, y2) = P(*a), P(*b)
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
               f'stroke-width="{sw}" stroke-opacity="{op}" stroke-linecap="round" {extra}/>')


def text(pt, s, fill, size=13, extra=""):
    x, y = P(*pt)
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}" text-anchor="middle" '
               f'class="lbl" {extra}>{s}</text>')


def box(x0, x1, y0, y1, z0, z1, fill, stroke, top_fill=None, glow=False):
    """Draw the visible faces of a box: east (x0), north (y0) and top."""
    g = 'filter="url(#glow)"' if glow else ""
    poly([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], fill, stroke, 1.2, 0.95, g)
    poly([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], fill, stroke, 1.2, 0.85, g)
    poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], top_fill or fill, stroke, 1.2, 0.95, g)


# --- Terrain -----------------------------------------------------------------
TX0, TX1, TY0, TY1, TZB = -5, 20, -4, 15, -3.4


def ground(x, y):
    t = -0.9 + 0.9 * min(max(y / 8.0, 0.0), 1.0)
    if x <= 0:
        return -2.4
    if x >= 4:
        return t
    return -2.4 + (t + 2.4) * x / 4.0


def terrain_cells(select):
    cells = []
    for xi in range(TX0, TX1):
        for yi in range(TY0, TY1):
            if 0 <= xi < 16 and 0 <= yi < 8:
                continue  # below the house
            if select(xi, yi):
                cells.append((xi, yi))
    cells.sort(key=lambda c: -(c[0] + c[1]))
    for xi, yi in cells:
        pts = [(xi, yi), (xi + 1, yi), (xi + 1, yi + 1), (xi, yi + 1)]
        poly([(a, b, ground(a, b)) for a, b in pts], "#120a24", MAGENTA, 0.6, 1.0,
             'stroke-opacity="0.35"')


def is_back(xi, yi):
    return xi >= 0 and yi >= 0


# --- Drawing -----------------------------------------------------------------
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_IMG}" height="{H_IMG}" '
           f'viewBox="0 0 {W_IMG} {H_IMG}">')
out.append("""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#05010d"/><stop offset="1" stop-color="#1a0630"/>
</linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="2.2" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="softglow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="6"/>
</filter>
<pattern id="earth" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <rect width="8" height="8" fill="#1b0d1f"/><line x1="0" y1="0" x2="0" y2="8" stroke="#ff2bd6" stroke-opacity="0.25" stroke-width="2"/>
</pattern>
<style>
  .lbl { font-family: Consolas, 'Courier New', monospace; font-weight: 700; letter-spacing: 1.5px;
         paint-order: stroke; stroke: #05010d; stroke-width: 3px; stroke-linejoin: round; }
</style>
</defs>""")
out.append(f'<rect width="{W_IMG}" height="{H_IMG}" fill="url(#bg)"/>')

# Back and side terrain.
terrain_cells(is_back)

# Altan (Terass): x 0-9, y 8-13, deck at 0.0. Posts where the ground is low.
for px in (0.0, 2.0, 4.0):
    for py in (8.0, 10.5, 13.0):
        g = ground(px, py)
        if g < -0.05:
            box(px, px + 0.15, py - 0.15, py, g, 0.0, "#2a1640", VIOLET)
poly([(0, 8, 0), (9, 8, 0), (9, 13, 0), (0, 13, 0)], "#2a1a10", ORANGE, 1.5, 0.9,
     'id="room-terass" filter="url(#glow)"')
for i in range(1, 18):
    line((i * 0.5, 8, 0), (i * 0.5, 13, 0), ORANGE, 0.6, 0.35)
text((4.5, 11.2, 0), "TERASS", ORANGE, 13, 'filter="url(#glow)"')

# Basement block: x 0-16, y 0-8, z -2.4 to 0.
out.append('<g id="room-downstairs">')
box(0, 16, 0, 8, -2.4, 0, "#0d1a2a", CYAN, "#0b1320", glow=True)
out.append("</g>")
for zz in (-1.6, -0.8):
    line((0, 0, zz), (0, 8, zz), CYAN, 0.6, 0.25)
    line((0, 0, zz), (16, 0, zz), CYAN, 0.6, 0.25)
text((0, 6.0, -1.5), "DOWNSTAIRS", CYAN, 13, 'filter="url(#glow)"')
text((0, 6.0, -1.95), "NOT MAPPED", CYAN, 10, 'opacity="0.7"')

# Front terrain (covers the buried part of the north face).
terrain_cells(lambda xi, yi: not is_back(xi, yi))

# Cut faces of the terrain slab.
xs = [TX0 + i * 0.5 for i in range(int((TX1 - TX0) / 0.5) + 1)]
poly([(x, TY0, ground(x, TY0)) for x in xs] + [(TX1, TY0, TZB), (TX0, TY0, TZB)],
     "url(#earth)", MAGENTA, 1.0, 1.0)
ys = [TY0 + i * 0.5 for i in range(int((TY1 - TY0) / 0.5) + 1)]
poly([(TX0, y, ground(TX0, y)) for y in ys] + [(TX0, TY1, TZB), (TX0, TY0, TZB)],
     "url(#earth)", MAGENTA, 1.0, 1.0)

# East balcony: x -2 to 0, y 0-8, deck at 0.0, under the main roof.
for py in (0.0, 4.0, 8.0):
    box(-2.0, -1.85, py, py + 0.15, -2.4, 0.0, "#2a1640", VIOLET)
box(-2.0, 0.0, 0.0, 8.0, -0.15, 0.0, "#1f1030", VIOLET, "#2a1640", glow=True)
line((-2, 0, 0.9), (-2, 8, 0.9), VIOLET, 1.2, 0.7)
for py in (0.0, 4.0, 8.0):
    line((-2, py, 0), (-2, py, 0.9), VIOLET, 1.2, 0.8)

# North outside stairs: x 6-8, from -0.9 up to 0.0.
out.append('<g id="front-door">')
for i in range(5):
    y0 = -1.5 + 0.3 * i
    box(6.0, 8.0, y0, 0.0, -0.9, -0.9 + 0.18 * (i + 1), "#141024", YELLOW)
out.append("</g>")

# --- Main floor -----------------------------------------------------------------
rooms = [
    ("KITCHEN", [(0, 5.25), (10.5, 5.25), (10.5, 8), (0, 8)], YELLOW, (5.2, 6.6)),
    ("GARDEROBEN", [(10.5, 5.25), (12.5, 5.25), (12.5, 8), (10.5, 8)], VIOLET, (11.5, 6.6)),
    ("BEDROOM", [(12.5, 3.75), (16, 3.75), (16, 8), (12.5, 8)], MAGENTA, (14.25, 5.9)),
    ("OFFICE", [(12.5, 0), (16, 0), (16, 3.75), (12.5, 3.75)], GREEN, (14.25, 1.9)),
    ("BATHROOM", [(9, 0), (12.5, 0), (12.5, 2.75), (9, 2.75)], CYAN, (10.75, 1.4)),
    ("BIBLIOTEKET", [(0, 0), (5.5, 0), (5.5, 5.25), (0, 5.25)], ORANGE, (2.75, 2.6)),
    ("HALLEN", [(5.5, 0), (9, 0), (9, 2.75), (12.5, 2.75), (12.5, 5.25), (5.5, 5.25)], "#ff4d6d", (8.0, 4.0)),
]
for name, pts, col, _ in rooms:
    poly([(x, y, 0) for x, y in pts], col, col, 1.0, 0.13, f'id="room-{name.lower()}"')

# Inside stairs down: x 8-9, y 0-3.
poly([(8, 0, 0), (9, 0, 0), (9, 3, 0), (8, 3, 0)], "#05010d", CYAN, 1.0, 1.0)
for i in range(1, 12):
    line((8, i * 0.25, 0), (9, i * 0.25, 0), CYAN, 0.7, 0.5)

WH = 1.1  # cut height of the walls
walls = [
    # Outer walls (with gaps for the doors).
    (0, 0, 6.5, 0), (7.5, 0, 16, 0),              # north, entrance gap
    (0, 0, 0, 2.5), (0, 3.0, 0, 8),               # east, balcony door gap
    (0, 8, 8.0, 8), (8.5, 8, 16, 8),              # south, altan door gap
    (16, 0, 16, 8),                               # west
    # Inside walls.
    (2.5, 5.25, 6.0, 5.25), (7.5, 5.25, 12.0, 5.25),
    (10.5, 5.25, 10.5, 8),
    (12.5, 0, 12.5, 3.0), (12.5, 3.5, 12.5, 4.5), (12.5, 5.0, 12.5, 8),
    (12.5, 3.75, 16, 3.75),
    (5.5, 0, 5.5, 3.5), (5.5, 5.0, 5.5, 5.25),
    (9, 0, 9, 2.75), (9, 2.75, 11.5, 2.75), (12.0, 2.75, 12.5, 2.75),
]
walls.sort(key=lambda w: -((w[0] + w[2]) / 2 + (w[1] + w[3]) / 2))
for x0, y0, x1, y1 in walls:
    poly([(x0, y0, 0), (x1, y1, 0), (x1, y1, WH), (x0, y0, WH)], "#0a1424", CYAN, 0.8, 0.82)
    line((x0, y0, WH), (x1, y1, WH), CYAN, 2.0, 1.0, 'filter="url(#glow)"')

# Windows (glow strips) and French balcony doors.
windows = [
    ((0, 5.5), (0, 7.5)), ((0, 0.0), (0, 2.5)),              # east
    ((10.5, 0), (11.0, 0)), ((14.25, 0), (14.75, 0)),        # north
    ((7.5, 8), (8.0, 8)), ((15.0, 8), (15.5, 8)), ((11.5, 8), (12.0, 8)),  # south
    ((16, 1.0), (16, 1.5)),                                  # west
]
for (ax, ay), (bx, by) in windows:
    poly([(ax, ay, 0.35), (bx, by, 0.35), (bx, by, 0.95), (ax, ay, 0.95)], CYAN, CYAN, 1.0, 0.55,
         'filter="url(#glow)"')
poly([(0.75, 8, 0.85), (1.5, 8, 0.85), (1.5, 8, 1.05), (0.75, 8, 1.05)], CYAN, CYAN, 1.0, 0.6)  # small high
poly([(14.0, 8, 0.0), (14.5, 8, 0.0), (14.5, 8, 1.05), (14.0, 8, 1.05)], MAGENTA, MAGENTA, 1.0, 0.6,
     'filter="url(#glow)"')  # French balcony

# Arched openings: glowing arcs above the gaps.
line((6.0, 5.25, WH), (7.5, 5.25, WH), YELLOW, 2.5, 0.9, 'filter="url(#glow)" stroke-dasharray="4 3"')
line((5.5, 3.5, WH), (5.5, 5.0, WH), YELLOW, 2.5, 0.9, 'filter="url(#glow)" stroke-dasharray="4 3"')

# Room labels.
for name, _, col, (lx, ly) in rooms:
    text((lx, ly, 0.05), name, col, 10 if name == "GARDEROBEN" else 12, 'filter="url(#glow)"')

# Motion rings and temperature texts.
sensors = {"bathroom": (10.75, 1.4), "hallen": (8.0, 4.0)}
for area, (cx_, cy_) in sensors.items():
    ring = [(cx_ + 0.8 * math.cos(a / 24 * 2 * math.pi), cy_ + 0.8 * math.sin(a / 24 * 2 * math.pi), 0.02)
            for a in range(24)]
    poly(ring, "none", "#ff2b4a", 2.0, 1.0, f'id="motion-{area}" class="motion-off"')
    text((cx_, cy_, 0.05), "--.- °C", "#e8f6ff", 11, f'id="temp-{area}" dy="16"')

# Entrance marker.
text((7.0, -2.2, -0.9), "ENTRANCE", YELLOW, 11, 'filter="url(#glow)"')
text((-1.0, 9.0, 0.2), "BALCONY", VIOLET, 11, 'filter="url(#glow)"')

# Title and compass.
out.append(f'<text x="40" y="60" fill="{CYAN}" font-size="28" class="lbl" filter="url(#glow)">'
           f'HOUSE // MAIN FLOOR</text>')
out.append(f'<text x="40" y="88" fill="{MAGENTA}" font-size="13" class="lbl" opacity="0.85">'
           f'MAIN FLOOR 0.0 M  ·  DOWNSTAIRS -2.4 M  ·  VIEW FROM NORTH-EAST</text>')
cx, cy = 1090, 790
out.append(f'<g class="lbl" font-size="13" text-anchor="middle" filter="url(#glow)">'
           f'<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{CYAN}" stroke-opacity="0.5"/>')
for name in ("N", "S", "E", "W"):
    # Direction of each compass point in screen space.
    vx, vy = {"N": (C30, 0.5), "S": (-C30, -0.5), "E": (-C30, 0.5), "W": (C30, -0.5)}[name]
    col = YELLOW if name == "N" else CYAN
    out.append(f'<text x="{cx + vx * 48:.1f}" y="{cy + vy * 48 + 5:.1f}" fill="{col}">{name}</text>')
out.append("</g>")

out.append("</svg>")
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out))
