#!/usr/bin/env python3
"""Quick build script for Godot with PonSVG module"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    godot_path = Path(r"E:\Dev\godot-dev")
    if not godot_path.exists():
        print("ERROR: Godot path not found. Run setup_dev_environment.py first")
        return 1
    
    # Change to Godot directory
    os.chdir(godot_path)
      # Build command
    cmd = [
        sys.executable, "-c", "import SCons.Script; SCons.Script.main()",
        "target=editor",
        "platform=windows",
        "module_ponsvg_enabled=yes",
        "-j4"  # Use 4 cores
    ]
      print("Building Godot with PonSVG module...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Working directory: {godot_path}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print("SUCCESS: Build completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Build failed with return code {e.returncode}")
        return 1
    except KeyboardInterrupt:
        print("\nWARNING: Build interrupted by user")
        return 1

if __name__ == "__main__":
    sys.exit(main())
