#!/usr/bin/env python3
"""
GDExtension Build Script for PonSVG
Builds the GDExtension for multiple platforms and packages it for distribution.
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

def print_header(title):
    print("\n" + "="*60)
    print(f"🔧 {title}")
    print("="*60)

def print_step(message):
    print(f"📋 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def check_requirements():
    """Check if all required tools are available"""
    print_step("Checking build requirements...")
    
    # Check CMake
    try:
        result = subprocess.run(["cmake", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"   CMake: {version}")
        else:
            raise FileNotFoundError()
    except FileNotFoundError:
        print_error("CMake not found. Please install CMake 3.20+")
        return False
    
    # Check Git
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   Git: {version}")
        else:
            raise FileNotFoundError()
    except FileNotFoundError:
        print_error("Git not found. Please install Git")
        return False
    
    # Check godot-cpp submodule
    godot_cpp_path = Path("godot-cpp")
    if not godot_cpp_path.exists() or not (godot_cpp_path / "CMakeLists.txt").exists():
        print_step("Initializing godot-cpp submodule...")
        subprocess.run(["git", "submodule", "update", "--init", "--recursive"], check=True)
    
    if (godot_cpp_path / "CMakeLists.txt").exists():
        print("   godot-cpp: Found")
    else:
        print_error("godot-cpp submodule not properly initialized")
        return False
    
    print_success("All requirements met")
    return True

def setup_build_directory(build_type="Release"):
    """Create and prepare build directory"""
    print_step(f"Setting up build directory for {build_type}...")
    
    build_dir = Path("build") / build_type.lower()
    build_dir.mkdir(parents=True, exist_ok=True)
    
    return build_dir

def build_extension(build_dir, build_type="Release", target_platform=None):
    """Build the GDExtension using CMake"""
    print_step(f"Building GDExtension ({build_type})...")
    
    cmake_args = [
        "cmake",
        "-B", str(build_dir),
        "-DCMAKE_BUILD_TYPE=" + build_type,
        "."
    ]
    
    if target_platform:
        if target_platform == "windows":
            cmake_args.extend(["-G", "Visual Studio 17 2022"])
        elif target_platform == "linux":
            cmake_args.extend(["-G", "Unix Makefiles"])
    
    # Configure
    print("   Configuring...")
    result = subprocess.run(cmake_args, cwd=Path.cwd())
    if result.returncode != 0:
        print_error("CMake configuration failed")
        return False
    
    # Build
    print("   Compiling...")
    build_args = ["cmake", "--build", str(build_dir), "--config", build_type]
    result = subprocess.run(build_args, cwd=Path.cwd())
    if result.returncode != 0:
        print_error("Build failed")
        return False
    
    print_success(f"Build completed: {build_type}")
    return True

def package_extension(version="1.0.0"):
    """Package the extension for distribution"""
    print_step("Packaging GDExtension...")
    
    # Create package directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"ponsvg-gdextension-{version}-{timestamp}"
    package_dir = Path("dist") / package_name
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy addon structure
    addon_dir = package_dir / "addons" / "ponsvg"
    addon_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy extension file
    shutil.copy2("ponsvg.gdextension", addon_dir)
    
    # Copy binaries
    bin_src = Path("bin")
    bin_dest = addon_dir / "bin"
    if bin_src.exists():
        shutil.copytree(bin_src, bin_dest, dirs_exist_ok=True)
    
    # Copy documentation
    docs = ["README.md", "LICENSE"]
    for doc in docs:
        if Path(doc).exists():
            shutil.copy2(doc, addon_dir)
    
    # Create plugin.cfg
    plugin_cfg = f"""[plugin]

name="PonSVG"
description="High-performance SVG rendering and manipulation for Godot using LunaSVG"
author="PonSVG Team"
version="{version}"
script="plugin.gd"
"""
    
    with open(addon_dir / "plugin.cfg", 'w') as f:
        f.write(plugin_cfg)
    
    # Create basic plugin.gd
    plugin_gd = '''@tool
extends EditorPlugin

func _enter_tree():
	print("PonSVG plugin activated")

func _exit_tree():
	print("PonSVG plugin deactivated")
'''
    
    with open(addon_dir / "plugin.gd", 'w') as f:
        f.write(plugin_gd)
    
    # Create ZIP package
    zip_path = package_dir.with_suffix('.zip')
    shutil.make_archive(str(package_dir), 'zip', str(package_dir.parent), package_name)
    
    print_success(f"Package created: {zip_path}")
    return zip_path

def main():
    parser = argparse.ArgumentParser(description="Build PonSVG GDExtension")
    parser.add_argument("--build-type", choices=["Debug", "Release"], default="Release",
                       help="Build type (default: Release)")
    parser.add_argument("--platform", choices=["windows", "linux", "macos"],
                       help="Target platform (auto-detect if not specified)")
    parser.add_argument("--package", action="store_true",
                       help="Create distribution package after building")
    parser.add_argument("--version", default="1.0.0",
                       help="Version for packaging (default: 1.0.0)")
    parser.add_argument("--clean", action="store_true",
                       help="Clean build directory before building")
    
    args = parser.parse_args()
    
    print_header("PonSVG GDExtension Build Script")
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Clean if requested
    if args.clean:
        print_step("Cleaning build directory...")
        build_root = Path("build")
        if build_root.exists():
            shutil.rmtree(build_root)
        bin_dir = Path("bin")
        if bin_dir.exists():
            shutil.rmtree(bin_dir)
    
    # Setup build directory
    build_dir = setup_build_directory(args.build_type)
    
    # Build extension
    if not build_extension(build_dir, args.build_type, args.platform):
        return 1
    
    # Package if requested
    if args.package:
        package_path = package_extension(args.version)
        print_success(f"Build and package complete!")
        print(f"Package: {package_path}")
    else:
        print_success("Build complete!")
        print(f"Binaries: {Path('bin').absolute()}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
