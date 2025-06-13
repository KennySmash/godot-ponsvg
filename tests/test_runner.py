#!/usr/bin/env python3

"""
Main test runner for the SVG module.
Loads configuration from dev-settings.json and manages the test environment.
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

# Fix encoding issues on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class SVGModuleTestRunner:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.project_root = self.script_dir.parent
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Load development settings from dev-settings.json"""
        settings_path = self.project_root / "dev-settings.json"
          if not settings_path.exists():
            print(f"X Settings file not found: {settings_path}")
            print("Please create dev-settings.json with your Godot development path")
            sys.exit(1)
            
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            print(f"OK Loaded settings from {settings_path}")
            return settings
        except Exception as e:
            print(f"X Error loading settings: {e}")
            sys.exit(1)
    
    def validate_godot_path(self):
        """Validate that the Godot development path exists"""
        godot_path = Path(self.settings["godot_dev_path"])
        
        if not godot_path.exists():
            print(f"❌ Godot development path not found: {godot_path}")
            return False
            
        # Check for key Godot files
        scons_file = godot_path / "SConstruct"
        if not scons_file.exists():
            print(f"❌ Invalid Godot directory (no SConstruct): {godot_path}")
            return False
            
        modules_dir = godot_path / "modules"
        if not modules_dir.exists():
            print(f"❌ Modules directory not found: {modules_dir}")
            return False
            
        print(f"✅ Valid Godot development path: {godot_path}")
        return True
    
    def copy_module_to_godot(self):
        """Copy the SVG module to the Godot development directory"""
        if not self.validate_godot_path():
            return False
            
        godot_path = Path(self.settings["godot_dev_path"])
        source_module = self.project_root / "modules" / self.settings["module_name"]
        target_module = godot_path / "modules" / self.settings["module_name"]
        
        # Backup existing module if requested
        if self.settings["development"]["backup_existing_module"] and target_module.exists():
            backup_path = target_module.with_suffix(".backup")
            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.move(str(target_module), str(backup_path))
            print(f"🔄 Backed up existing module to {backup_path}")
        
        # Copy module
        if target_module.exists():
            shutil.rmtree(target_module)
            
        shutil.copytree(str(source_module), str(target_module))
        print(f"✅ Copied module to {target_module}")
        return True
    
    def build_godot(self):
        """Build Godot with the SVG module"""
        if not self.validate_godot_path():
            return False
            
        godot_path = Path(self.settings["godot_dev_path"])
        
        # Build scons command
        scons_cmd = ["scons"]
        for key, value in self.settings["scons_options"].items():
            scons_cmd.append(f"{key}={value}")
        
        if self.settings["development"]["clean_build"]:
            scons_cmd.append("-c")
            print("🧹 Running clean build...")
        
        print(f"🔨 Building Godot with command: {' '.join(scons_cmd)}")
        print(f"📁 Working directory: {godot_path}")
        
        try:
            result = subprocess.run(
                scons_cmd,
                cwd=str(godot_path),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ Build successful!")
                return True
            else:
                print("❌ Build failed!")
                print("STDOUT:", result.stdout[-1000:])  # Last 1000 chars
                print("STDERR:", result.stderr[-1000:])
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Build timed out after 10 minutes")
            return False
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
    
    def run_build_tests(self):
        """Run the build validation tests"""
        test_file = self.script_dir / "build_test.py"
        if not test_file.exists():
            print("❌ build_test.py not found")
            return False
            
        print("🔍 Running build validation tests...")
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
                
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Test execution error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all available tests"""
        print("🧪 Running all tests...")
        
        success = True
        
        # Build tests
        if not self.run_build_tests():
            success = False
        
        # List other test files
        test_files = list(self.script_dir.glob("test_*.py"))
        test_files = [f for f in test_files if f.name != "build_test.py"]
        
        if test_files:
            print(f"📋 Found additional test files: {[f.name for f in test_files]}")
            print("ℹ️  These contain GDScript tests to run manually in Godot")
        
        return success
    
    def show_status(self):
        """Show current development environment status"""
        print("SVG Module Development Status")
        print("=" * 40)
        print(f"Project root: {self.project_root}")
        print(f"Godot path: {self.settings['godot_dev_path']}")
        print(f"Module name: {self.settings['module_name']}")
        print(f"Platform: {self.settings['scons_options']['platform']}")
        print(f"Target: {self.settings['scons_options']['target']}")
        print()
        
        # Check paths
        godot_valid = self.validate_godot_path()
        module_source = self.project_root / "modules" / self.settings["module_name"]
        module_exists = module_source.exists()
        
        godot_path = Path(self.settings["godot_dev_path"])
        target_module = godot_path / "modules" / self.settings["module_name"]
        module_installed = target_module.exists() if godot_valid else False
        
        print(f"Source module exists: {'✅' if module_exists else '❌'}")
        print(f"Godot path valid: {'✅' if godot_valid else '❌'}")
        print(f"Module installed in Godot: {'✅' if module_installed else '❌'}")
        
        # Check test assets
        test_assets = self.script_dir / "assets"
        print(f"Test assets available: {'✅' if test_assets.exists() else '❌'}")
        
        if test_assets.exists():
            svg_files = list(test_assets.glob("*.svg"))
            print(f"  - SVG test files: {len(svg_files)}")

def main():
    if len(sys.argv) < 2:
        print("SVG Module Test Runner")
        print("Usage:")
        print("  python test_runner.py status       - Show development environment status")
        print("  python test_runner.py copy         - Copy module to Godot directory")
        print("  python test_runner.py build        - Build Godot with SVG module")
        print("  python test_runner.py test         - Run build validation tests")
        print("  python test_runner.py all          - Copy, build, and test")
        print("  python test_runner.py deploy       - Copy and build (no tests)")
        return 1
    
    runner = SVGModuleTestRunner()
    command = sys.argv[1].lower()
    
    if command == "status":
        runner.show_status()
        
    elif command == "copy":
        success = runner.copy_module_to_godot()
        return 0 if success else 1
        
    elif command == "build":
        success = runner.build_godot()
        return 0 if success else 1
        
    elif command == "test":
        success = runner.run_all_tests()
        return 0 if success else 1
        
    elif command == "all":
        print("🚀 Running full development cycle...")
        success = True
        success &= runner.copy_module_to_godot()
        success &= runner.build_godot()
        success &= runner.run_all_tests()
        
        if success:
            print("🎉 Full cycle completed successfully!")
        else:
            print("❌ Full cycle failed")
        return 0 if success else 1
        
    elif command == "deploy":
        print("📦 Deploying module...")
        success = True
        success &= runner.copy_module_to_godot()
        if runner.settings["development"]["auto_build_after_copy"]:
            success &= runner.build_godot()
        
        if success:
            print("✅ Module deployed successfully!")
        else:
            print("❌ Deployment failed")
        return 0 if success else 1
        
    else:
        print(f"❌ Unknown command: {command}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
