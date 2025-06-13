#!/usr/bin/env python3

"""
Build test script for the SVG module.
This tests if the module can be built properly.
"""

import os
import sys
import subprocess

def check_lunasvg_files():
    """Check if LunaSVG files are present"""
    lunasvg_path = "modules/svg_module/src/lunasvg"
    required_files = [
        "include/lunasvg.h",
        "source/lunasvg.cpp",
        "plutovg/source/plutovg-canvas.c"
    ]
    
    missing_files = []
    for file in required_files:
        full_path = os.path.join(lunasvg_path, file)
        if not os.path.exists(full_path):
            missing_files.append(full_path)
    
    if missing_files:
        print("❌ Missing LunaSVG files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ LunaSVG files are present")
    return True

def check_module_structure():
    """Check if module files are properly structured"""
    module_path = "modules/svg_module"
    required_files = [
        "config.py",
        "src/register_types.cpp",
        "src/register_types.h",
        "src/svg_resource.cpp",
        "src/svg_resource.h",
        "src/svg_texture.cpp", 
        "src/svg_texture.h",
        "src/svg_sprite.cpp",
        "src/svg_sprite.h",
        "src/lunasvg_integration.cpp",
        "src/lunasvg_integration.h"
    ]
    
    missing_files = []
    for file in required_files:
        full_path = os.path.join(module_path, file)
        if not os.path.exists(full_path):
            missing_files.append(full_path)
    
    if missing_files:
        print("❌ Missing module files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Module structure is correct")
    return True

def run_syntax_check():
    """Run basic syntax checks on C++ files"""
    module_path = "modules/svg_module/src"
    cpp_files = [
        "register_types.cpp",
        "svg_resource.cpp", 
        "svg_texture.cpp",
        "svg_sprite.cpp",
        "lunasvg_integration.cpp"
    ]
    
    print("🔍 Running syntax checks...")
    
    # This is a basic check - in a real build environment you'd use the actual compiler
    for file in cpp_files:
        full_path = os.path.join(module_path, file)
        try:
            with open(full_path, 'r') as f:
                content = f.read()
                
            # Basic syntax checks
            if content.count('{') != content.count('}'):
                print(f"❌ Brace mismatch in {file}")
                return False
                
            if '#include' not in content:
                print(f"⚠️  No includes found in {file}")
                
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
            return False
    
    print("✅ Basic syntax checks passed")
    return True

def main():
    print("SVG Module Build Test")
    print("====================")
    print()
    
    # Change to the correct directory if needed
    if os.path.basename(os.getcwd()) != "gotot-svg-module":
        if os.path.exists("gotot-svg-module"):
            os.chdir("gotot-svg-module")
        elif os.path.exists("modules/svg_module"):
            pass  # We're in the Godot root
        else:
            print("❌ Cannot find SVG module directory")
            return 1
    
    success = True
    success &= check_module_structure()
    success &= check_lunasvg_files() 
    success &= run_syntax_check()
    
    if success:
        print()
        print("🎉 All checks passed! Module appears ready for compilation.")
        print()
        print("Next steps:")
        print("1. Copy this module to a Godot source tree under modules/svg_module")
        print("2. Run: scons platform=windows target=editor module_svg_enabled=yes")
        print("3. Test with the provided test script")
        return 0
    else:
        print()
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
