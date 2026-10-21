# Carcinus Shipyards (Starsector Mod)

A Starsector 0.98 mod repository configured for rapid, accessible ship development, featuring novel movement paradigms and combat vessels.

Included showcase ship: **Carcinus-class Heavy Skitter Cruiser** — an armored, wide-silhouette vessel engineered for transverse vectoring with faster strafing speed than forward speed and snapping rotational agility.

---

## Quick Start

### 1. Link Mod to Starsector
Run the PowerShell link script to create a Windows directory junction directly into your Starsector `mods` folder:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\link_mod.ps1
```
*(Any edits you make in this git repository will be instantly reflected in the game without manual copying.)*

### 2. Launch & Enable
1. Start the Starsector launcher.
2. Click **Mods** and check **Carcinus Shipyards**.
3. Launch game.

### 3. Test In-Game
Using [Console Commands](https://fractalsoftworks.com/forum/index.php?topic=4106.0) (already enabled in your setup):
- Press `Ctrl + Backspace` in campaign or the combat simulator.
- Type:
  ```text
  addship carcinus_Assault
  ```
  or
  ```text
  addship carcinus_Strike
  ```

---

## Creating New Ships

We provide an automated CLI wizard that scaffolds complete, crash-free ship files in one command:

```bash
# Interactive wizard:
python tools/create_ship.py

# Or via command-line arguments:
python tools/create_ship.py --id birgus --name "Birgus" --size DESTROYER --tech Midline
```

This auto-generates:
- `graphics/ships/<id>/<id>.png` (pixel-art placeholder sprite)
- `data/hulls/<id>.ship` (bounds, engine slots, mounts)
- `data/hulls/ship_data.csv` (properly aligned 56-column row)
- `data/variants/<id>/<id>_Assault.variant` (playable fitted variant)
- `data/strings/descriptions.csv` (codex lore entry)

### Validate Your Mod
Catch CSV column misalignments, JSON syntax errors, and missing sprite references before launching:

```bash
python tools/validate_mod.py
```

---

## The Showcase Ship: Carcinus Cruiser

| Property | Value |
| :--- | :--- |
| **Hull Name** | Carcinus |
| **Designation** | Heavy Skitter Cruiser |
| **Role** | Broadside Skirmisher / Lateral Brawler |
| **Base Forward Speed** | 45 |
| **Lateral Strafe Speed** | 80 (+35 via Decapod Propulsion Grid) |
| **Turn Rate** | 30 deg/sec (+30% bonus, turn accel 55) |
| **Built-in Hullmod** | `Decapod Propulsion Grid` (dynamically accelerates transverse movement) |
| **Ship System** | `Lateral Skitter Drive` (high-velocity lateral evasive burst) |
| **Armament** | 1x Large Ballistic, 1x Medium Energy, 2x Medium Ballistic (Claws), 2x Small Missile, 4x Small PD |

---

## Documentation & Guides
- [docs/SHIP_CREATION_GUIDE.md](docs/SHIP_CREATION_GUIDE.md) — Comprehensive guide on ship creation, Trylobot Ship Editor workflow, coordinate math, balance standards, and testing.
