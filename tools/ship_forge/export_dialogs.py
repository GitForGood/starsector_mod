"""
Export Dialog providing flexible options to export configuration files,
copy CSV rows to clipboard, append to existing tables, or write complete CSVs.
"""

import csv
import json
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .constants import SHIP_DATA_HEADERS, WEAPON_DATA_HEADERS

class ExportDialog(tk.Toplevel):
    def __init__(self, parent, project, mode="SHIP"):
        super().__init__(parent)
        self.project = project
        self.mode = mode
        
        title_str = f"Export {project.hull_name} to Mod" if mode == "SHIP" else f"Export {project.weapon_name} to Mod"
        self.title(title_str)
        self.geometry("640x540")
        self.minsize(560, 440)
        self.configure(bg="#161b22")

        # Guess base mod directory
        curr_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.mod_dir_var = tk.StringVar(value=curr_dir)

        self.setup_ui()

    def setup_ui(self):
        pad = tk.Frame(self, bg="#161b22", padx=16, pady=14)
        pad.pack(fill="both", expand=True)

        # Header
        item_name = self.project.hull_name if self.mode == "SHIP" else self.project.weapon_name
        item_id = self.project.hull_id if self.mode == "SHIP" else self.project.weapon_id

        tk.Label(pad, text=f"Export: {item_name} ({item_id})",
                 font=("Segoe UI", 12, "bold"), fg="#38bdf8", bg="#161b22").pack(anchor="w")

        # Mod Destination Folder
        dest_f = tk.LabelFrame(pad, text="Target Mod Directory", bg="#161b22", fg="#94a3b8", padx=10, pady=8)
        dest_f.pack(fill="x", pady=10)

        df_row = tk.Frame(dest_f, bg="#161b22")
        df_row.pack(fill="x")
        e_dir = tk.Entry(df_row, textvariable=self.mod_dir_var, bg="#0d1117", fg="#ffffff", insertbackground="#fff", relief="flat")
        e_dir.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Button(df_row, text="Browse...", command=self.browse_dir,
                  bg="#21262d", fg="#c9d1d9", font=("Segoe UI", 8), relief="flat").pack(side="right")

        # Export Elements
        elem_f = tk.LabelFrame(pad, text="Files to Export", bg="#161b22", fg="#94a3b8", padx=10, pady=8)
        elem_f.pack(fill="x", pady=5)

        if self.mode == "SHIP":
            self.export_main_var = tk.BooleanVar(value=True)
            tk.Checkbutton(elem_f, text=f"Generate .ship definition file (data/hulls/{item_id}.ship)",
                           variable=self.export_main_var, bg="#161b22", fg="#e2e8f0", selectcolor="#0d1117").pack(anchor="w")

            self.export_var_var = tk.BooleanVar(value=True)
            tk.Checkbutton(elem_f, text=f"Generate starter .variant file (data/variants/{item_id}/{item_id}_Assault.variant)",
                           variable=self.export_var_var, bg="#161b22", fg="#e2e8f0", selectcolor="#0d1117").pack(anchor="w")

            self.copy_sprite_var = tk.BooleanVar(value=True)
            tk.Checkbutton(elem_f, text=f"Copy ship sprite to graphics/ships/{item_id}/",
                           variable=self.copy_sprite_var, bg="#161b22", fg="#e2e8f0", selectcolor="#0d1117").pack(anchor="w")
        else:
            self.export_main_var = tk.BooleanVar(value=True)
            tk.Checkbutton(elem_f, text=f"Generate .wpn definition file (data/weapons/{item_id}.wpn)",
                           variable=self.export_main_var, bg="#161b22", fg="#e2e8f0", selectcolor="#0d1117").pack(anchor="w")

            self.copy_sprite_var = tk.BooleanVar(value=True)
            tk.Checkbutton(elem_f, text=f"Copy weapon sprites to graphics/weapons/",
                           variable=self.copy_sprite_var, bg="#161b22", fg="#e2e8f0", selectcolor="#0d1117").pack(anchor="w")

        self.export_desc_var = tk.BooleanVar(value=True)
        tk.Checkbutton(elem_f, text="Append/update codex lore entry in data/strings/descriptions.csv",
                       variable=self.export_desc_var, bg="#161b22", fg="#e2e8f0", selectcolor="#0d1117").pack(anchor="w")

        # CSV Table Options
        csv_f = tk.LabelFrame(pad, text="CSV Data Export Options", bg="#161b22", fg="#94a3b8", padx=10, pady=8)
        csv_f.pack(fill="x", pady=10)

        self.csv_mode_var = tk.StringVar(value="APPEND")
        csv_name = "data/hulls/ship_data.csv" if self.mode == "SHIP" else "data/weapons/weapon_data.csv"

        tk.Radiobutton(csv_f, text=f"Append or update row in mod {csv_name}",
                       variable=self.csv_mode_var, value="APPEND", bg="#161b22", fg="#e2e8f0", selectcolor="#0d1117").pack(anchor="w")
        tk.Radiobutton(csv_f, text="Export as full standalone CSV table to custom location",
                       variable=self.csv_mode_var, value="FULL_TABLE", bg="#161b22", fg="#e2e8f0", selectcolor="#0d1117").pack(anchor="w")
        tk.Radiobutton(csv_f, text="Do not write CSV (Copy row data to clipboard only)",
                       variable=self.csv_mode_var, value="CLIPBOARD", bg="#161b22", fg="#e2e8f0", selectcolor="#0d1117").pack(anchor="w")

        # Action Buttons
        btn_f = tk.Frame(pad, bg="#161b22")
        btn_f.pack(fill="x", pady=(15, 0))

        tk.Button(btn_f, text="Cancel", command=self.destroy,
                  bg="#21262d", fg="#c9d1d9", padx=12, pady=5, relief="flat").pack(side="right", padx=(6, 0))

        tk.Button(btn_f, text="Export Now", command=self.do_export,
                  bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8",
                  font=("Segoe UI", 9, "bold"), padx=16, pady=5, relief="flat", cursor="hand2").pack(side="right")

    def browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.mod_dir_var.get(), title="Select Target Starsector Mod Directory")
        if d:
            self.mod_dir_var.set(d)

    def do_export(self):
        mod_root = self.mod_dir_var.get()
        if not mod_root or not os.path.isdir(mod_root):
            messagebox.showerror("Error", "Please select a valid destination mod folder.")
            return

        csv_mode = self.csv_mode_var.get()
        exported_summary = []

        try:
            if self.mode == "SHIP":
                self.export_ship(mod_root, csv_mode, exported_summary)
            else:
                self.export_weapon(mod_root, csv_mode, exported_summary)

            summary_text = "\n".join(exported_summary)
            messagebox.showinfo("Export Complete", f"Successfully exported:\n\n{summary_text}")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred during export:\n{e}")

    def export_ship(self, mod_root, csv_mode, summary):
        sp = self.project
        hull_id = sp.hull_id

        # 1. Copy Sprite
        rel_sprite = f"graphics/ships/{hull_id}/{hull_id}.png"
        if self.copy_sprite_var.get() and sp.sprite_path and os.path.isfile(sp.sprite_path):
            dest_sprite = os.path.join(mod_root, *rel_sprite.split("/"))
            os.makedirs(os.path.dirname(dest_sprite), exist_ok=True)
            if os.path.abspath(sp.sprite_path) != os.path.abspath(dest_sprite):
                shutil.copy2(sp.sprite_path, dest_sprite)
            summary.append(f"• Sprite: {rel_sprite}")

        # 2. Export .ship JSON
        if self.export_main_var.get():
            ship_dict = sp.to_ship_dict(rel_sprite)
            dest_ship = os.path.join(mod_root, "data", "hulls", f"{hull_id}.ship")
            os.makedirs(os.path.dirname(dest_ship), exist_ok=True)
            with open(dest_ship, "w", encoding="utf-8") as f:
                json.dump(ship_dict, f, indent=2)
            summary.append(f"• Hull: data/hulls/{hull_id}.ship")

        # 3. Export .variant
        if self.export_var_var.get():
            var_id = f"{hull_id}_Assault"
            dest_var = os.path.join(mod_root, "data", "variants", hull_id, f"{var_id}.variant")
            os.makedirs(os.path.dirname(dest_var), exist_ok=True)
            
            # Group weapons
            groups = []
            for slot in sp.weapon_slots:
                groups.append({
                    "autofire": False,
                    "mode": "LINKED",
                    "weapons": {slot.id: "heavymortar" if slot.size == "MEDIUM" else "pdlaser"}
                })

            var_json = {
                "displayName": "Assault",
                "fluxCapacitors": 10,
                "fluxVents": 15,
                "goalVariant": True,
                "hullId": hull_id,
                "hullMods": ["targetingunit"],
                "permaMods": [],
                "sMods": [],
                "variantId": var_id,
                "weaponGroups": groups[:5],
                "wings": []
            }
            with open(dest_var, "w", encoding="utf-8") as f:
                json.dump(var_json, f, indent=2)
            summary.append(f"• Variant: data/variants/{hull_id}/{var_id}.variant")

        # 4. Descriptions
        if self.export_desc_var.get():
            desc_path = os.path.join(mod_root, "data", "strings", "descriptions.csv")
            self.write_or_update_desc(desc_path, hull_id, "SHIP", sp.description)
            summary.append("• Lore: data/strings/descriptions.csv")

        # 5. CSV handling
        row_values = sp.get_csv_row_values()
        if csv_mode == "CLIPBOARD":
            row_str = ",".join(f'"{v}"' if "," in str(v) else str(v) for v in row_values)
            self.clipboard_clear()
            self.clipboard_append(row_str)
            summary.append("• CSV row copied to Windows clipboard!")
        elif csv_mode == "FULL_TABLE":
            save_csv = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                                    initialfile="ship_data.csv")
            if save_csv:
                with open(save_csv, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(SHIP_DATA_HEADERS)
                    writer.writerow(row_values)
                summary.append(f"• Standalone CSV: {save_csv}")
        elif csv_mode == "APPEND":
            dest_csv = os.path.join(mod_root, "data", "hulls", "ship_data.csv")
            self.write_or_update_csv(dest_csv, SHIP_DATA_HEADERS, row_values, id_col_idx=1)
            summary.append("• Appended to: data/hulls/ship_data.csv")

    def export_weapon(self, mod_root, csv_mode, summary):
        wp = self.project
        wpn_id = wp.weapon_id

        # 1. Copy Sprites
        t_rel = f"graphics/weapons/{wpn_id}_turret.png"
        h_rel = f"graphics/weapons/{wpn_id}_hardpoint.png"
        if self.copy_sprite_var.get():
            if wp.turret_sprite_path and os.path.isfile(wp.turret_sprite_path):
                t_dest = os.path.join(mod_root, *t_rel.split("/"))
                os.makedirs(os.path.dirname(t_dest), exist_ok=True)
                shutil.copy2(wp.turret_sprite_path, t_dest)
                summary.append(f"• Turret Sprite: {t_rel}")
            if wp.hardpoint_sprite_path and os.path.isfile(wp.hardpoint_sprite_path):
                h_dest = os.path.join(mod_root, *h_rel.split("/"))
                os.makedirs(os.path.dirname(h_dest), exist_ok=True)
                shutil.copy2(wp.hardpoint_sprite_path, h_dest)
                summary.append(f"• Hardpoint Sprite: {h_rel}")

        # 2. Export .wpn JSON
        if self.export_main_var.get():
            wpn_dict = wp.to_wpn_dict(t_rel, h_rel)
            dest_wpn = os.path.join(mod_root, "data", "weapons", f"{wpn_id}.wpn")
            os.makedirs(os.path.dirname(dest_wpn), exist_ok=True)
            with open(dest_wpn, "w", encoding="utf-8") as f:
                json.dump(wpn_dict, f, indent=2)
            summary.append(f"• Weapon Spec: data/weapons/{wpn_id}.wpn")

        # 3. Descriptions
        if self.export_desc_var.get():
            desc_path = os.path.join(mod_root, "data", "strings", "descriptions.csv")
            self.write_or_update_desc(desc_path, wpn_id, "WEAPON", wp.description)
            summary.append("• Lore: data/strings/descriptions.csv")

        # 4. CSV handling
        row_values = wp.get_csv_row_values()
        if csv_mode == "CLIPBOARD":
            row_str = ",".join(f'"{v}"' if "," in str(v) else str(v) for v in row_values)
            self.clipboard_clear()
            self.clipboard_append(row_str)
            summary.append("• CSV row copied to Windows clipboard!")
        elif csv_mode == "FULL_TABLE":
            save_csv = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                                    initialfile="weapon_data.csv")
            if save_csv:
                with open(save_csv, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(WEAPON_DATA_HEADERS)
                    writer.writerow(row_values)
                summary.append(f"• Standalone CSV: {save_csv}")
        elif csv_mode == "APPEND":
            dest_csv = os.path.join(mod_root, "data", "weapons", "weapon_data.csv")
            self.write_or_update_csv(dest_csv, WEAPON_DATA_HEADERS, row_values, id_col_idx=1)
            summary.append("• Appended to: data/weapons/weapon_data.csv")

    def write_or_update_csv(self, file_path, headers, new_row, id_col_idx=1):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        existing_rows = []
        replaced = False
        target_id = str(new_row[id_col_idx]).strip()

        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                try:
                    file_headers = next(reader)
                except StopIteration:
                    file_headers = headers

                for r in reader:
                    if len(r) > id_col_idx and r[id_col_idx].strip() == target_id:
                        existing_rows.append(new_row)
                        replaced = True
                    else:
                        existing_rows.append(r)

        if not replaced:
            existing_rows.append(new_row)

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in existing_rows:
                writer.writerow(r)

    def write_or_update_desc(self, file_path, item_id, item_type, text):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        headers = ["id", "type", "text1", "text2", "text3", "text4", "text5", "notes"]
        existing_rows = []
        replaced = False

        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                try:
                    headers = next(reader)
                except StopIteration:
                    pass
                for r in reader:
                    if len(r) > 1 and r[0].strip() == item_id and r[1].strip() == item_type:
                        existing_rows.append([item_id, item_type, text, "", "", "", "", ""])
                        replaced = True
                    else:
                        existing_rows.append(r)

        if not replaced:
            existing_rows.append([item_id, item_type, text, "", "", "", "", ""])

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in existing_rows:
                writer.writerow(r)
