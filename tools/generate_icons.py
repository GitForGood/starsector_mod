"""
Generates UI icons for Decapod Locomotion hullmod (32x32)
and Lateral Skitter Drive ship system (64x64).
"""
import math
import os
import struct
import zlib

def write_png(filename, width, height, pixel_func):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            r, g, b, a = pixel_func(x, y)
            raw.extend([r, g, b, a])
    compressed = zlib.compress(bytes(raw), 9)
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(png)

# 1. Decapod Locomotion (32x32)
# Lateral arrows and thruster flare
def hullmod_pix(x, y):
    cx, cy = 15.5, 15.5
    dx = x - cx
    dy = y - cy
    dist = math.sqrt(dx * dx + dy * dy)
    
    # Border ring
    if 13 <= dist <= 15:
        return (60, 180, 220, 230)
    
    # Left and right arrows (< | >)
    # Left arrow tip at (4, 16), base at (10, 10..22)
    is_left_arrow = (x >= 4 and x <= 11 and abs(dy) <= (x - 4) * 1.5 and abs(dy) <= 6)
    is_right_arrow = (x <= 27 and x >= 20 and abs(dy) <= (27 - x) * 1.5 and abs(dy) <= 6)
    
    if is_left_arrow or is_right_arrow:
        return (240, 255, 255, 255)
    
    # Center chevron / crab shield symbol
    if abs(dx) <= 3 and abs(dy) <= 5:
        return (220, 130, 50, 240)
    
    # Soft background
    if dist < 13:
        return (20, 30, 42, 190)
    
    return (0, 0, 0, 0)

# 2. Skitter Drive System (64x64)
def shipsys_pix(x, y):
    cx, cy = 31.5, 31.5
    dx = x - cx
    dy = y - cy
    dist = math.sqrt(dx * dx + dy * dy)
    
    # Outer hexagonal/tech ring
    if 27 <= dist <= 30:
        return (70, 200, 240, 255)
    
    # Dynamic lateral jet plumes
    # Plumes pointing outward left and right
    if abs(dy) <= 8:
        if -26 <= dx <= -10 or 10 <= dx <= 26:
            intensity = 1.0 - abs(dy) / 8.0
            return (int(100 + 155 * intensity), 255, 255, 240)
    
    # Center ship chevron
    if abs(dx) + abs(dy) * 0.8 <= 12:
        return (230, 140, 60, 255)
    
    if dist < 27:
        val = max(0, int(40 - dist))
        return (15 + val, 25 + val * 2, 38 + val * 3, 200)
    
    return (0, 0, 0, 0)

write_png(os.path.join("graphics", "icons", "hullmods", "decapod_locomotion.png"), 32, 32, hullmod_pix)
write_png(os.path.join("graphics", "icons", "shipsystems", "carcinus_skitter.png"), 64, 64, shipsys_pix)
print("Generated UI icons.")
