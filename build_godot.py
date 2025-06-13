#!/usr/bin/env python3
"""Enhanced build script for Godot with PonSVG module"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def load_dev_settings():
    """Load development settings from dev-settings.json"""
    script_dir = Path(__file__).parent
    settings_file = script_dir / "dev-settings.json"
    
    if not settings_file.exists():
        raise FileNotFoundError(f"dev-settings.json not found at {settings_file}")
    
    with open(settings_file, 'r') as f:
        return json.load(f)

def setup_build_directory():
    """Create and prepare build output directory"""
    script_dir = Path(__file__).parent
    build_dir = script_dir / "build"
    
    # Create build directory if it doesn't exist
    build_dir.mkdir(exist_ok=True)
    
    # Create timestamped subdirectory for this build
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_build_dir = build_dir / f"godot_ponsvg_{timestamp}"
    current_build_dir.mkdir(exist_ok=True)
    
    # Create symlink to latest build
    latest_link = build_dir / "latest"
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    
    try:
        latest_link.symlink_to(current_build_dir.name, target_is_directory=True)
    except OSError:
        # Fallback for systems without symlink support
        with open(build_dir / "latest.txt", 'w') as f:
            f.write(str(current_build_dir))
    
    return current_build_dir

def copy_module_to_godot(settings):
    """Copy the PonSVG module to Godot modules directory"""
    script_dir = Path(__file__).parent
    module_source = script_dir / "modules" / settings["module_name"]
    godot_modules_dir = Path(settings["godot_dev_path"]) / "modules"
    module_dest = godot_modules_dir / settings["module_name"]
    
    print(f"Copying module from {module_source} to {module_dest}")
    
    # Remove existing module if it exists
    if module_dest.exists():
        shutil.rmtree(module_dest)
    
    # Copy new module, excluding git metadata and cache files
    def ignore_patterns(dir, files):
        ignore = []
        for file in files:
            if (file.startswith('.git') or 
                file == '__pycache__' or 
                file.endswith('.pyc') or
                file.endswith('.pyo')):
                ignore.append(file)
        return ignore
    
    shutil.copytree(module_source, module_dest, ignore=ignore_patterns)
    print(f"Module copied successfully")

def find_built_executable(godot_path, platform, target):
    """Find the built Godot executable"""
    # Common executable patterns for different platforms
    patterns = {
        "windows": [
            f"bin/godot.windows.{target}.x86_64.exe",
            f"bin/godot.windows.{target}.64.exe", 
            f"bin/godot.windows.{target}.exe"
        ],
        "linux": [
            f"bin/godot.linuxbsd.{target}.x86_64",
            f"bin/godot.linuxbsd.{target}.64"
        ],
        "macos": [
            f"bin/godot.macos.{target}.universal",
            f"bin/godot.macos.{target}.x86_64"
        ]
    }
    
    for pattern in patterns.get(platform, patterns["windows"]):
        exe_path = godot_path / pattern
        if exe_path.exists():
            return exe_path
    
    return None

def copy_build_artifacts(godot_path, build_dir, settings):
    """Copy built artifacts to build directory"""
    platform = settings["scons_options"]["platform"]
    target = settings["scons_options"]["target"]
    
    print(f"Looking for built executable...")
    
    # Find the executable
    exe_path = find_built_executable(godot_path, platform, target)
    if not exe_path:
        print("WARNING: Could not find built executable")
        return False
    
    print(f"Found executable: {exe_path}")
    
    # Copy executable to build directory
    exe_dest = build_dir / f"godot_ponsvg.exe"
    shutil.copy2(exe_path, exe_dest)
    print(f"Copied executable to: {exe_dest}")
    
    # Copy any additional files if they exist
    additional_files = ["COPYRIGHT.txt", "LICENSE.txt", "README.md"]
    for file_name in additional_files:
        src_file = godot_path / file_name
        if src_file.exists():
            shutil.copy2(src_file, build_dir / file_name)
    
    # Create build info file
    build_info = {
        "build_time": datetime.now().isoformat(),
        "module_name": settings["module_name"],
        "platform": platform,
        "target": target,
        "godot_path": str(godot_path),
        "executable": str(exe_dest)
    }
    
    with open(build_dir / "build_info.json", 'w') as f:
        json.dump(build_info, f, indent=2)
    
    return True

def main():
    try:
        print("Loading development settings...")
        settings = load_dev_settings()
        
        godot_path = Path(settings["godot_dev_path"])
        if not godot_path.exists():
            print("ERROR: Godot path not found. Run setup_dev_environment.py first")
            return 1
        
        print("Setting up build directory...")
        build_dir = setup_build_directory()
        
        print("Copying PonSVG module to Godot...")
        copy_module_to_godot(settings)
        
        # Change to Godot directory for build
        original_cwd = os.getcwd()
        os.chdir(godot_path)
        
        # Build command using settings
        cmd = [sys.executable, "-c", "import SCons.Script; SCons.Script.main()"]
        
        # Add SCons options from settings
        for key, value in settings["scons_options"].items():
            if isinstance(value, bool):
                value = "yes" if value else "no"
            cmd.append(f"{key}={value}")
        
        # Add parallel build
        cmd.extend(["-j", "4"])
        
        print("Building Godot with PonSVG module...")
        print(f"Command: {' '.join(cmd)}")
        print(f"Working directory: {godot_path}")
        print()
        
        result = subprocess.run(cmd, check=True)
        
        # Return to original directory
        os.chdir(original_cwd)
        
        print("Build completed successfully!")
        
        # Copy build artifacts
        print("Copying build artifacts...")
        if copy_build_artifacts(godot_path, build_dir, settings):
            print(f"SUCCESS: Build package ready in: {build_dir}")
            print(f"Latest build link: {build_dir.parent / 'latest'}")
        else:
            print("WARNING: Build completed but artifacts not fully copied")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Build failed with return code {e.returncode}")
        return 1
    except KeyboardInterrupt:
        print("\nWARNING: Build interrupted by user")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
