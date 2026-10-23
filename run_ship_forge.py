#!/usr/bin/env python3
"""
Launcher for Starsector Ship & Weapon Forge.
Can be run directly with: python run_ship_forge.py
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ship_forge.app import main

if __name__ == "__main__":
    main()
