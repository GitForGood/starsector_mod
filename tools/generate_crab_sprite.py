"""
Generates the sprite for the Carcinus-class Skitter Cruiser.
Produces a crisp, 200x160 Starsector-style pixel art vessel.
"""
import math
import struct
import zlib
import os

WIDTH = 200
HEIGHT = 160

# Palette
TRANSPARENT = (0, 0, 0, 0)
DARK_OUTLINE = (18, 22, 28, 255)
HULL_DARK = (38, 46, 56, 255)
HULL_MID = (54, 65, 78, 255)
HULL_LIGHT = (76, 90, 107, 255)
HULL_HIGHLIGHT = (105, 122, 142, 255)

CARAPACE_DARK = (112, 58, 28, 255)
CARAPACE_MID = (158, 86, 38, 255)
CARAPACE_LIGHT = (201, 115, 52, 255)
CARAPACE_HIGHLIGHT = (235, 150, 80, 255)

METAL_GRATE = (25, 30, 36, 255)
WEAPON_WELL = (20, 24, 30, 255)
WEAPON_RIM = (70, 82, 98, 255)

GLOW_CYAN_CORE = (180, 255, 255, 255)
GLOW_CYAN = (40, 210, 230, 255)
GLOW_CYAN_DIM = (20, 110, 130, 200)

ENGINE_NOZZLE = (35, 38, 44, 255)

grid = [[TRANSPARENT for _ in range(WIDTH)] for _ in range(HEIGHT)]

def set_pixel(x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        grid[y][x] = color

def set_sym(x, y, color):
    # Symmetrical along X = 100
    # Left side x, right side 199 - x
    set_pixel(x, y, color)
    set_pixel(199 - x, y, color)

def fill_rect_sym(x1, y1, x2, y2, color):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            set_sym(x, y, color)

def fill_poly_sym(points, color):
    # Scanline fill for polygon points [(x, y), ...]
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    for y in range(min_y, max_y + 1):
        intersections = []
        n = len(points)
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            if (p1[1] <= y < p2[1]) or (p2[1] <= y < p1[1]):
                if p2[1] != p1[1]:
                    x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                    intersections.append(x)
        intersections.sort()
        for i in range(0, len(intersections) - 1, 2):
            x_start = int(math.ceil(intersections[i]))
            x_end = int(math.floor(intersections[i + 1]))
            for x in range(x_start, x_end + 1):
                set_sym(x, y, color)

# 1. Base Carapace / Central Body
body_poly = [
    (100, 38),   # Front beak
    (75, 42),
    (55, 52),
    (42, 68),
    (38, 90),
    (42, 115),
    (52, 132),
    (75, 142),
    (100, 145)   # Rear center
]
fill_poly_sym(body_poly, HULL_DARK)

inner_carapace = [
    (100, 42),
    (78, 46),
    (60, 56),
    (48, 72),
    (44, 92),
    (48, 112),
    (58, 126),
    (78, 136),
    (100, 139)
]
fill_poly_sym(inner_carapace, HULL_MID)

# 2. Heavy Claws (Pincers)
left_claw = [
    (54, 18),   # Tip of outer claw
    (42, 28),
    (34, 46),
    (36, 68),
    (48, 72),
    (58, 56),
    (62, 38),
    (66, 26),
    (60, 22)
]
fill_poly_sym(left_claw, CARAPACE_MID)

# Inner claw pincer barb
claw_inner_tooth = [
    (58, 24),
    (68, 32),
    (64, 44),
    (56, 36)
]
fill_poly_sym(claw_inner_tooth, CARAPACE_DARK)

# Claw highlights & edge plates
claw_plates = [
    (50, 22), (40, 32), (36, 48), (38, 62), (46, 52), (54, 34)
]
fill_poly_sym(claw_plates, CARAPACE_LIGHT)

# 3. Lateral Thruster Sponsons (3 on each flank)
# Thruster 1 (Forward flank)
sponson1 = [(44, 60), (22, 66), (20, 76), (40, 78)]
fill_poly_sym(sponson1, HULL_DARK)
sponson1_plate = [(42, 62), (24, 67), (23, 74), (39, 76)]
fill_poly_sym(sponson1_plate, CARAPACE_MID)

# Thruster 2 (Mid flank - widest point)
sponson2 = [(40, 84), (12, 90), (10, 102), (38, 104)]
fill_poly_sym(sponson2, HULL_DARK)
sponson2_plate = [(38, 86), (15, 91), (13, 100), (36, 102)]
fill_poly_sym(sponson2_plate, CARAPACE_MID)

# Thruster 3 (Rear flank)
sponson3 = [(44, 110), (20, 114), (18, 126), (46, 128)]
fill_poly_sym(sponson3, HULL_DARK)
sponson3_plate = [(42, 112), (22, 115), (21, 124), (44, 126)]
fill_poly_sym(sponson3_plate, CARAPACE_MID)

# Lateral thruster exhaust nozzles and glows (facing left: x ~ 10..20)
# Nozzle 1
fill_rect_sym(18, 69, 21, 74, ENGINE_NOZZLE)
fill_rect_sym(19, 70, 20, 73, GLOW_CYAN)
set_sym(20, 71, GLOW_CYAN_CORE)
set_sym(20, 72, GLOW_CYAN_CORE)

# Nozzle 2
fill_rect_sym(9, 93, 12, 99, ENGINE_NOZZLE)
fill_rect_sym(10, 94, 11, 98, GLOW_CYAN)
set_sym(11, 95, GLOW_CYAN_CORE)
set_sym(11, 96, GLOW_CYAN_CORE)
set_sym(11, 97, GLOW_CYAN_CORE)

# Nozzle 3
fill_rect_sym(17, 117, 20, 123, ENGINE_NOZZLE)
fill_rect_sym(18, 118, 19, 122, GLOW_CYAN)
set_sym(19, 119, GLOW_CYAN_CORE)
set_sym(19, 120, GLOW_CYAN_CORE)

# 4. Rear Engines (twin main thrusters)
fill_rect_sym(84, 142, 95, 149, ENGINE_NOZZLE)
fill_rect_sym(86, 144, 93, 148, GLOW_CYAN)
fill_rect_sym(88, 145, 91, 147, GLOW_CYAN_CORE)

# 5. Dorsal Armored Carapace Segment Plates (Crab Shell Bands)
# Band 1 (Forward shell)
band1 = [(100, 52), (80, 55), (66, 65), (66, 74), (82, 68), (100, 66)]
fill_poly_sym(band1, CARAPACE_LIGHT)

# Band 2 (Mid dorsal shell)
band2 = [(100, 72), (78, 74), (64, 85), (64, 96), (80, 90), (100, 88)]
fill_poly_sym(band2, CARAPACE_MID)

# Band 3 (Rear dorsal shell)
band3 = [(100, 94), (76, 96), (62, 108), (62, 118), (78, 114), (100, 112)]
fill_poly_sym(band3, CARAPACE_DARK)

# 6. Weapon Mount Recesses
def draw_mount_well(cx, cy, radius, rim_col=WEAPON_RIM, well_col=WEAPON_WELL):
    for dy in range(-radius - 1, radius + 2):
        for dx in range(-radius - 1, radius + 2):
            d2 = dx * dx + dy * dy
            if d2 <= (radius + 1) ** 2:
                set_sym(cx + dx, cy + dy, rim_col)
            if d2 <= radius ** 2:
                set_sym(cx + dx, cy + dy, well_col)

# Claw Heavy Mounts (WS 001, WS 002) at x=52, y=42
draw_mount_well(52, 42, 5)

# Center Large / Medium Turret (WS 003) at x=100, y=78
draw_mount_well(100, 78, 6)

# Forward Center Medium Mount (WS 004) at x=100, y=56
draw_mount_well(100, 56, 4)

# Flank Turrets (WS 005, WS 006) at x=68, y=96
draw_mount_well(68, 96, 4)

# Rear PD Turrets (WS 007, WS 008) at x=78, y=126
draw_mount_well(78, 126, 3)

# Missile bays (slotted hardpoints) at x=78, y=46
fill_rect_sym(76, 44, 82, 50, WEAPON_WELL)
fill_rect_sym(75, 43, 83, 44, WEAPON_RIM)
fill_rect_sym(75, 50, 83, 51, WEAPON_RIM)

# 7. Bridge / Command Optics (slit sensor)
fill_rect_sym(95, 48, 100, 50, DARK_OUTLINE)
fill_rect_sym(96, 49, 100, 49, GLOW_CYAN_CORE)

# 8. Outline and Bevel Shading
# Create a crisp 1px dark perimeter outline around all opaque pixels
outlines = []
for y in range(HEIGHT):
    for x in range(WIDTH):
        if grid[y][x][3] > 0:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                    if grid[ny][nx][3] == 0:
                        outlines.append((nx, ny))

for x, y in outlines:
    set_pixel(x, y, DARK_OUTLINE)

# Save PNG
def save_png(filename):
    raw = bytearray()
    for y in range(HEIGHT):
        raw.append(0)
        for x in range(WIDTH):
            r, g, b, a = grid[y][x]
            raw.extend([r, g, b, a])
    
    compressed = zlib.compress(bytes(raw), 9)
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(png)
    print(f"Generated sprite: {filename} ({WIDTH}x{HEIGHT})")

save_png(os.path.join("graphics", "ships", "carcinus", "carcinus.png"))
