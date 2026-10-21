#!/usr/bin/env python3
"""
Mod Validator for Starsector Mod Projects
-----------------------------------------
Performs health checks on:
- mod_info.json syntax and fields
- ship_data.csv column alignment and duplicate IDs
- .ship JSON syntax, bounds, engine slots, and sprite file references
- .variant JSON syntax and hullId linkages
- hull_mods.csv and ship_systems.csv formatting
- Java script package path consistency
"""

import csv
import glob
import json
import os
import re
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

errors = 0
warnings = 0

def log_pass(msg):
    print(f"  [OK] {msg}")

def log_warn(msg):
    global warnings
    warnings += 1
    print(f"  [WARN] {msg}")

def log_err(msg):
    global errors
    errors += 1
    print(f"  [FAIL] {msg}")

def parse_relaxed_json(filepath):
    """Parses JSON allowing comments (# and //) and trailing commas."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Strip single line comments
    lines = []
    for line in content.splitlines():
        clean = line
        # Strip # comment if not in quotes
        if "#" in clean:
            clean = re.sub(r'#.*$', '', clean)
        # Strip // comment
        if "//" in clean:
            clean = re.sub(r'//.*$', '', clean)
        lines.append(clean)
    
    clean_text = "\n".join(lines)
    # Remove trailing commas before } or ]
    clean_text = re.sub(r',\s*([\]}])', r'\1', clean_text)
    return json.loads(clean_text)

def check_mod_info():
    print("\nChecking mod_info.json...")
    path = os.path.join(BASE_DIR, "mod_info.json")
    if not os.path.isfile(path):
        log_err("mod_info.json not found!")
        return
    try:
        data = parse_relaxed_json(path)
        required = ["id", "name", "version", "gameVersion"]
        for field in required:
            if field in data and data[field]:
                log_pass(f"'{field}' is present ({data[field]})")
            else:
                log_err(f"Missing required field: '{field}'")
    except Exception as e:
        log_err(f"Failed to parse mod_info.json: {e}")

def check_csv_file(rel_path, expected_col_count=None):
    abs_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.isfile(abs_path):
        log_warn(f"CSV not found: {rel_path}")
        return []
    
    rows = []
    with open(abs_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            log_err(f"{rel_path} is completely empty!")
            return []
            
        header_len = len(header)
        log_pass(f"{rel_path} header found ({header_len} columns)")
        
        if expected_col_count and header_len != expected_col_count:
            log_warn(f"{rel_path} has {header_len} columns, expected {expected_col_count}")
            
        for line_idx, row in enumerate(reader, start=2):
            if not row or all(c.strip() == "" for c in row):
                continue
            if len(row) != header_len:
                log_err(f"{rel_path} Line {line_idx}: Column mismatch! Has {len(row)} values, expected {header_len}")
            rows.append((line_idx, row))
    return rows

def check_ships(csv_hull_ids):
    print("\nChecking ship definitions (.ship)...")
    ship_files = glob.glob(os.path.join(BASE_DIR, "data", "hulls", "*.ship"))
    if not ship_files:
        log_warn("No .ship files found in data/hulls/")
        return set()

    defined_hull_ids = set()
    for sf in ship_files:
        rel = os.path.relpath(sf, BASE_DIR)
        try:
            data = parse_relaxed_json(sf)
            hull_id = data.get("hullId")
            if not hull_id:
                log_err(f"{rel}: Missing 'hullId' field")
                continue
            defined_hull_ids.add(hull_id)
            
            # Check sprite existence
            sprite_rel = data.get("spriteName", "")
            if not sprite_rel:
                log_err(f"{rel} ({hull_id}): Missing 'spriteName'")
            else:
                sprite_abs = os.path.join(BASE_DIR, *sprite_rel.split("/"))
                if os.path.isfile(sprite_abs):
                    log_pass(f"{hull_id}: Sprite verified ({sprite_rel})")
                else:
                    log_err(f"{rel} ({hull_id}): Sprite file does not exist: {sprite_rel}")

            # Check bounds and engines
            bounds = data.get("bounds", [])
            if len(bounds) < 6 or len(bounds) % 2 != 0:
                log_warn(f"{rel} ({hull_id}): Bounds array contains {len(bounds)} numbers (expected even >= 6)")
            
            engines = data.get("engineSlots", [])
            if not engines:
                log_warn(f"{rel} ({hull_id}): No engine slots defined")

            # Check CSV cross-reference
            if hull_id not in csv_hull_ids:
                log_err(f"{rel} ({hull_id}) exists, but '{hull_id}' is missing from data/hulls/ship_data.csv!")

        except Exception as e:
            log_err(f"{rel}: Failed to parse JSON: {e}")
            
    return defined_hull_ids

def check_variants(defined_hull_ids):
    print("\nChecking variants (.variant)...")
    variant_files = glob.glob(os.path.join(BASE_DIR, "data", "variants", "**", "*.variant"), recursive=True)
    if not variant_files:
        log_warn("No .variant files found in data/variants/")
        return

    for vf in variant_files:
        rel = os.path.relpath(vf, BASE_DIR)
        try:
            data = parse_relaxed_json(vf)
            var_id = data.get("variantId")
            hull_id = data.get("hullId")
            if not var_id:
                log_err(f"{rel}: Missing 'variantId'")
            if not hull_id:
                log_err(f"{rel}: Missing 'hullId'")
            elif hull_id not in defined_hull_ids:
                log_err(f"{rel}: References unknown hullId '{hull_id}' (no matching .ship found)")
            else:
                log_pass(f"{var_id}: Links correctly to hull '{hull_id}'")
        except Exception as e:
            log_err(f"{rel}: Failed to parse JSON: {e}")

def check_scripts():
    print("\nChecking Java scripts and package declarations...")
    script_files = glob.glob(os.path.join(BASE_DIR, "data", "scripts", "**", "*.java"), recursive=True)
    for sf in script_files:
        rel = os.path.relpath(sf, BASE_DIR)
        with open(sf, "r", encoding="utf-8") as f:
            first_lines = "".join(f.readlines()[:10])
        
        match = re.search(r'package\s+([\w\.]+);', first_lines)
        if match:
            pkg = match.group(1)
            expected_dir = os.path.join(BASE_DIR, *pkg.split("."))
            actual_dir = os.path.dirname(sf)
            if os.path.normpath(expected_dir) == os.path.normpath(actual_dir):
                log_pass(f"{os.path.basename(sf)}: Package '{pkg}' matches folder structure")
            else:
                log_err(f"{rel}: Package '{pkg}' does not match file location {actual_dir}")
        else:
            log_warn(f"{rel}: No package declaration found")

def main():
    print("==================================================")
    print(" Starsector Mod Health & Validation Check")
    print("==================================================")
    
    check_mod_info()
    
    print("\nChecking CSV databases...")
    ship_data_rows = check_csv_file(os.path.join("data", "hulls", "ship_data.csv"), expected_col_count=56)
    csv_hull_ids = set()
    for line_idx, r in ship_data_rows:
        if len(r) > 1 and r[1]:
            hid = r[1].strip()
            if hid in csv_hull_ids:
                log_err(f"ship_data.csv Line {line_idx}: Duplicate hull ID '{hid}'!")
            csv_hull_ids.add(hid)
            
    check_csv_file(os.path.join("data", "hullmods", "hull_mods.csv"))
    check_csv_file(os.path.join("data", "shipsystems", "ship_systems.csv"))
    check_csv_file(os.path.join("data", "strings", "descriptions.csv"))

    defined_hull_ids = check_ships(csv_hull_ids)
    check_variants(defined_hull_ids)
    check_scripts()

    print("\n==================================================")
    print(f" Summary: {errors} Errors, {warnings} Warnings")
    print("==================================================")
    if errors > 0:
        sys.exit(1)
    else:
        print(" Mod passes all structural integrity checks!")

if __name__ == "__main__":
    main()
