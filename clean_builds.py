#!/usr/bin/env python3
"""Build cleanup utility for PonSVG Godot builds"""

import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta

def load_dev_settings():
    """Load development settings from dev-settings.json"""
    script_dir = Path(__file__).parent
    settings_file = script_dir / "dev-settings.json"
    
    if not settings_file.exists():
        raise FileNotFoundError(f"dev-settings.json not found at {settings_file}")
    
    with open(settings_file, 'r') as f:
        return json.load(f)

def clean_old_builds(build_dir, max_builds, dry_run=False):
    """Clean old build directories, keeping only the most recent ones"""
    if not build_dir.exists():
        print("No build directory found")
        return
    
    # Find all timestamped build directories
    build_pattern = "godot_ponsvg_*"
    build_dirs = [d for d in build_dir.iterdir() 
                 if d.is_dir() and d.name.startswith("godot_ponsvg_")]
    
    if len(build_dirs) <= max_builds:
        print(f"Found {len(build_dirs)} builds, no cleanup needed (max: {max_builds})")
        return
    
    # Sort by modification time (newest first)
    build_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    
    # Keep the newest max_builds, remove the rest
    to_keep = build_dirs[:max_builds]
    to_remove = build_dirs[max_builds:]
    
    print(f"Found {len(build_dirs)} builds")
    print(f"Keeping {len(to_keep)} newest builds")
    print(f"Removing {len(to_remove)} old builds")
    
    for build_dir_to_remove in to_remove:
        if dry_run:
            print(f"Would remove: {build_dir_to_remove}")
        else:
            print(f"Removing: {build_dir_to_remove}")
            shutil.rmtree(build_dir_to_remove)

def clean_all_builds(build_dir, dry_run=False):
    """Remove all build directories"""
    if not build_dir.exists():
        print("No build directory found")
        return
    
    build_dirs = [d for d in build_dir.iterdir() 
                 if d.is_dir() and d.name.startswith("godot_ponsvg_")]
    
    if not build_dirs:
        print("No build directories found")
        return
    
    print(f"Found {len(build_dirs)} build directories")
    
    for build_dir_to_remove in build_dirs:
        if dry_run:
            print(f"Would remove: {build_dir_to_remove}")
        else:
            print(f"Removing: {build_dir_to_remove}")
            shutil.rmtree(build_dir_to_remove)
    
    # Also remove the latest symlink/reference
    latest_link = build_dir / "latest"
    latest_txt = build_dir / "latest.txt"
    
    for link_file in [latest_link, latest_txt]:
        if link_file.exists():
            if dry_run:
                print(f"Would remove: {link_file}")
            else:
                print(f"Removing: {link_file}")
                link_file.unlink()

def list_builds(build_dir):
    """List all existing builds with their info"""
    if not build_dir.exists():
        print("No build directory found")
        return
    
    build_dirs = [d for d in build_dir.iterdir() 
                 if d.is_dir() and d.name.startswith("godot_ponsvg_")]
    
    if not build_dirs:
        print("No build directories found")
        return
    
    # Sort by modification time (newest first)
    build_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    
    print(f"Found {len(build_dirs)} builds:")
    print("-" * 80)
    
    for i, build_dir_item in enumerate(build_dirs, 1):
        stat = build_dir_item.stat()
        mod_time = datetime.fromtimestamp(stat.st_mtime)
        size_mb = sum(f.stat().st_size for f in build_dir_item.rglob('*') if f.is_file()) / (1024 * 1024)
        
        # Check if this is the latest build
        latest_marker = ""
        latest_link = build_dir / "latest"
        if latest_link.exists():
            try:
                if latest_link.resolve() == build_dir_item.resolve():
                    latest_marker = " [LATEST]"
            except:
                pass
        
        print(f"{i:2d}. {build_dir_item.name}{latest_marker}")
        print(f"    Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    Size: {size_mb:.1f} MB")
        
        # Show build info if available
        build_info_file = build_dir_item / "build_info.json"
        if build_info_file.exists():
            try:
                with open(build_info_file, 'r') as f:
                    build_info = json.load(f)
                print(f"    Target: {build_info.get('target', 'unknown')}")
                print(f"    Platform: {build_info.get('platform', 'unknown')}")
            except:
                pass
        print()

def main():
    parser = argparse.ArgumentParser(description="Clean PonSVG Godot build directories")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without actually doing it")
    parser.add_argument("--all", action="store_true", 
                       help="Remove all build directories")
    parser.add_argument("--list", action="store_true", 
                       help="List all existing builds")
    parser.add_argument("--max-builds", type=int, 
                       help="Maximum number of builds to keep (overrides settings)")
    
    args = parser.parse_args()
    
    try:
        settings = load_dev_settings()
        script_dir = Path(__file__).parent
        build_dir = script_dir / "build"
        
        if args.list:
            list_builds(build_dir)
        elif args.all:
            clean_all_builds(build_dir, args.dry_run)
        else:
            max_builds = args.max_builds or settings.get("build_output", {}).get("max_old_builds", 5)
            clean_old_builds(build_dir, max_builds, args.dry_run)
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
