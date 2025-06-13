#!/usr/bin/env python3
"""
Script to rename all SVG classes to PonSVG in the source files.
"""

import os
import re
from pathlib import Path

def replace_in_file(file_path, replacements):
    """Replace text in a file using a list of (old, new) tuples."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    # Define replacements
    replacements = [
        # Class names
        ("SVGResource", "PonSVGResource"),
        ("SVGTexture", "PonSVGTexture"), 
        ("SVGSprite2D", "PonSVGSprite2D"),
        ("SVGCacheEntry", "PonSVGCacheEntry"),
        ("SVGStyleOverride", "PonSVGStyleOverride"),
        
        # Header guards
        ("SVG_RESOURCE_H", "PONSVG_RESOURCE_H"),
        ("SVG_TEXTURE_H", "PONSVG_TEXTURE_H"),
        ("SVG_SPRITE_H", "PONSVG_SPRITE_H"),
        ("SVG_INTEGRATION_H", "PONSVG_INTEGRATION_H"),
        
        # Module functions
        ("initialize_svg_module", "initialize_ponsvg_module"),
        ("uninitialize_svg_module", "uninitialize_ponsvg_module"),
        
        # File includes (we'll keep the file names for now)
        # ("svg_resource.h", "ponsvg_resource.h"),
        # ("svg_texture.h", "ponsvg_texture.h"),
        # ("svg_sprite.h", "ponsvg_sprite.h"),
    ]
    
    # Source files to update
    src_dir = Path("modules/ponsvg/src")
    if not src_dir.exists():
        print(f"Source directory not found: {src_dir}")
        return
    
    # Process all .cpp and .h files
    files_to_process = []
    files_to_process.extend(src_dir.glob("*.cpp"))
    files_to_process.extend(src_dir.glob("*.h"))
    
    updated_count = 0
    for file_path in files_to_process:
        if replace_in_file(file_path, replacements):
            updated_count += 1
    
    print(f"\nProcessed {len(files_to_process)} files, updated {updated_count} files")

if __name__ == "__main__":
    main()
