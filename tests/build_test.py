#!/usr/bin/env python3
"""
Build test for the SVG module using the dev-settings configuration.
This script copies the module to the Godot repository and builds it.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

def load_dev_settings():
    """Load development settings from dev-settings.json"""
    script_dir = Path(__file__).parent
    settings_file = script_dir.parent / "dev-settings.json"
    
    if not settings_file.exists():
        raise FileNotFoundError(f"dev-settings.json not found at {settings_file}")
    
    with open(settings_file, 'r') as f:
        return json.load(f)

def ensure_godot_path_exists(godot_path):
    """Verify that the Godot development path exists"""
    if not Path(godot_path).exists():
        raise FileNotFoundError(f"Godot development path not found: {godot_path}")
    
    # Check if it looks like a Godot repository
    required_files = ["SConstruct", "modules", "core", "editor"]
    missing = [f for f in required_files if not (Path(godot_path) / f).exists()]
    
    if missing:
        raise ValueError(f"Path doesn't appear to be a Godot repository. Missing: {missing}")

def copy_module_to_godot(settings):
    """Copy the SVG module to the Godot modules directory"""
    module_source = Path(__file__).parent.parent / "modules" / settings["module_name"]
    godot_modules_dir = Path(settings["godot_dev_path"]) / "modules"
    module_dest = godot_modules_dir / settings["module_name"]
    
    print(f"Copying module from {module_source} to {module_dest}")
    
    # Backup existing module if requested
    if settings["development"]["backup_existing_module"] and module_dest.exists():
        backup_path = module_dest.with_suffix(".backup")
        if backup_path.exists():
            try:
                shutil.rmtree(backup_path)
            except PermissionError:
                print(f"Warning: Could not remove old backup, skipping backup")
        try:
            shutil.move(str(module_dest), str(backup_path))
            print(f"Backed up existing module to {backup_path}")
        except PermissionError:
            print(f"Warning: Could not backup module, continuing...")
    
    # Remove existing module
    if module_dest.exists():
        shutil.rmtree(module_dest)
    
    # Copy new module, excluding git metadata
    def ignore_git_and_cache(dir, files):
        ignore = []
        for file in files:
            if file.startswith('.git') or file == '__pycache__' or file.endswith('.pyc'):
                ignore.append(file)
        return ignore
    
    shutil.copytree(module_source, module_dest, ignore=ignore_git_and_cache)
    print(f"Module copied successfully")

def build_godot(settings):
    """Build Godot with the SVG module"""
    godot_path = Path(settings["godot_dev_path"])
    
    # Prepare SCons command - use Python to run SCons module
    scons_cmd = [sys.executable, "-c", "import SCons.Script; SCons.Script.main()"]
    
    # Add options from settings
    for key, value in settings["scons_options"].items():
        if isinstance(value, bool):
            value = "yes" if value else "no"
        scons_cmd.append(f"{key}={value}")
    
    # Add clean build if requested
    if settings["development"]["clean_build"]:
        scons_cmd.append("--clean")
    
    # Add parallel build
    scons_cmd.extend(["-j", "4"])
    
    print(f"Building Godot with command: {' '.join(scons_cmd)}")
    print(f"Working directory: {godot_path}")
    
    # Run the build
    result = subprocess.run(
        scons_cmd,
        cwd=godot_path,
        text=True
    )
    
    return result

def main():
    """Main build test function"""
    try:
        print("Loading dev-settings...")
        settings = load_dev_settings()
        
        print("Verifying Godot path...")
        ensure_godot_path_exists(settings["godot_dev_path"])
        
        if settings["development"]["auto_copy_module"]:
            print("Copying module to Godot...")
            copy_module_to_godot(settings)
        
        if settings["development"]["auto_build_after_copy"]:
            print("Building Godot...")
            result = build_godot(settings)            
            if result.returncode == 0:
                print("Build successful!")
                return True
            else:
                print("Build failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False
        else:
            print("Auto-build disabled. Module copied successfully.")
            return True
            
    except Exception as e:
        print(f"Build test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
