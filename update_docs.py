#!/usr/bin/env python3
"""
Script to update documentation files to use PonSVG naming.
"""

import os
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
    # Define replacements for documentation
    replacements = [
        # Class names in documentation
        ("SVGResource", "PonSVGResource"),
        ("SVGTexture", "PonSVGTexture"), 
        ("SVGSprite2D", "PonSVGSprite2D"),
        
        # Module references
        ("SVG Module", "PonSVG Module"),
        ("svg_module", "ponsvg"),
        ("module_svg_enabled", "module_ponsvg_enabled"),
        ("SVG module", "PonSVG module"),
        
        # Variable names in examples
        ("svg_resource", "ponsvg_resource"),
        ("svg_texture", "ponsvg_texture"),
        ("icon_set", "ponsvg_icon_set"),
        
        # Project titles but be careful not to replace "SVG" when referring to the file format
        ("# SVG Module", "# PonSVG Module"),
    ]
    
    # Documentation files to update
    doc_files = [
        "README.md",
        "PROJECT_STATUS.md", 
        "DEVELOPMENT_SETUP.md",
        "Featureset.md",
        "WORKING_JOURNAL.md",
        "tests/README.md",
        "tests/test_module.py",
        "tests/test_advanced.py",
        "tests/test_enhanced.py",
    ]
    
    updated_count = 0
    for file_name in doc_files:
        file_path = Path(file_name)
        if file_path.exists():
            if replace_in_file(file_path, replacements):
                updated_count += 1
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nProcessed {len(doc_files)} files, updated {updated_count} files")

if __name__ == "__main__":
    main()
