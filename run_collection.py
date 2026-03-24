#!/usr/bin/env python3
"""
MANUAL RUN SCRIPT
=================
Double-click this file (or run it from terminal) to collect today's data.

Run this whenever you remember - aim for once a day, but don't stress about it!
"""

import subprocess
import sys
from datetime import datetime

print("=" * 60)
print("🍺 HOMEBREW DATA COLLECTION")
print("=" * 60)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
print("Running the tracker script...")
print()

try:
    # Run the main tracker script
    result = subprocess.run(
        [sys.executable, 'homebrew_tracker_sqlite.py'],
        check=True
    )
    
    print()
    print("=" * 60)
    print("✅ SUCCESS! Data collected for today.")
    print("=" * 60)
    print()
    print("REMINDERS:")
    print("• Try to run this once a day (but don't stress!)")
    print("• After 5-7 runs, you'll have enough data for graphs")
    print("• The database keeps growing - never resets")
    print()
    
except FileNotFoundError:
    print("❌ Error: homebrew_tracker_sqlite.py not found!")
    print("   Make sure this script is in the same folder as your tracker.")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Keep window open on Windows
input("Press ENTER to close this window...")
