"""
Preset Manager Dialog for saving, loading, and applying custom ship baseline presets.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from .constants import DEFAULT_PRESETS

PRESETS_DIR = os.path.join(os.path.dirname(__file__), "presets")

class PresetManagerDialog(tk.Toplevel):
    def __init__(self, parent, project, on_apply_callback):
        super().__init__(parent)
        self.project = project
        self.on_apply_callback = on_apply_callback
        
        self.title("Ship Preset Manager")
        self.geometry("520x420")
        self.configure(bg="#161b22")

        os.makedirs(PRESETS_DIR, exist_ok=True)
        self.setup_ui()

    def setup_ui(self):
        pad = tk.Frame(self, bg="#161b22", padx=15, pady=12)
        pad.pack(fill="both", expand=True)

        tk.Label(pad, text="Ship Archetype & Baseline Presets",
                 font=("Segoe UI", 12, "bold"), fg="#38bdf8", bg="#161b22").pack(anchor="w")
        tk.Label(pad, text="Apply baseline stats, shield values, and logistics to accelerate balancing.",
                 font=("Segoe UI", 9), fg="#94a3b8", bg="#161b22").pack(anchor="w", pady=(2, 10))

        # Preset Listbox
        self.preset_list = tk.Listbox(pad, bg="#0d1117", fg="#ffffff", selectbackground="#2563eb",
                                      relief="flat", font=("Segoe UI", 10), height=10)
        self.preset_list.pack(fill="both", expand=True, pady=5)

        self.refresh_presets()

        # Action Buttons
        btn_f = tk.Frame(pad, bg="#161b22")
        btn_f.pack(fill="x", pady=(10, 0))

        tk.Button(btn_f, text="Save Current as Preset...", command=self.save_current_as_preset,
                  bg="#21262d", fg="#c9d1d9", padx=10, pady=4, relief="flat").pack(side="left")

        tk.Button(btn_f, text="Apply to Project", command=self.apply_preset,
                  bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8",
                  font=("Segoe UI", 9, "bold"), padx=14, pady=4, relief="flat", cursor="hand2").pack(side="right")

    def refresh_presets(self):
        self.preset_list.delete(0, tk.END)
        # Built-in presets
        for k in DEFAULT_PRESETS.keys():
            self.preset_list.insert(tk.END, f"[Built-in] {k}")
        
        # Custom user presets
        if os.path.isdir(PRESETS_DIR):
            for f in os.listdir(PRESETS_DIR):
                if f.endswith(".json"):
                    self.preset_list.insert(tk.END, f"[Custom] {f[:-5]}")

    def apply_preset(self):
        sel = self.preset_list.curselection()
        if not sel:
            messagebox.showwarning("Notice", "Please select a preset from the list.")
            return

        item = self.preset_list.get(sel[0])
        if item.startswith("[Built-in]"):
            key = item.replace("[Built-in] ", "").strip()
            self.project.apply_preset(key)
        else:
            name = item.replace("[Custom] ", "").strip()
            fpath = os.path.join(PRESETS_DIR, f"{name}.json")
            if os.path.isfile(fpath):
                with open(fpath, "r", encoding="utf-8") as fp:
                    custom_data = json.load(fp)
                    for k, v in custom_data.items():
                        if k in self.project.stats:
                            self.project.stats[k] = str(v)

        if self.on_apply_callback:
            self.on_apply_callback()
        messagebox.showinfo("Preset Applied", f"Successfully applied '{item}' to current project.")
        self.destroy()

    def save_current_as_preset(self):
        name = simpledialog.askstring("Save Preset", "Enter a name for this custom preset:", parent=self)
        if not name:
            return

        clean_name = "".join(c for c in name if c.isalnum() or c in ("_", "-")).strip()
        if not clean_name:
            return

        save_dict = {
            "size": self.project.hull_size,
            "tech": self.project.tech,
            **self.project.stats
        }
        fpath = os.path.join(PRESETS_DIR, f"{clean_name}.json")
        with open(fpath, "w", encoding="utf-8") as fp:
            json.dump(save_dict, fp, indent=2)

        self.refresh_presets()
        messagebox.showinfo("Saved", f"Saved preset: {clean_name}")
