#!/usr/bin/env python3
"""
Godot Development Environment Setup Script
Sets up the complete toolchain for building Godot with the SVG module on Windows.
"""

import os
import sys
import json
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path
import tempfile

class GodotDevSetup:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.project_root = self.script_dir
        self.settings = self.load_settings()
        self.godot_path = Path(self.settings["godot_dev_path"])
        
    def load_settings(self):
        """Load development settings"""
        settings_file = self.project_root / "dev-settings.json"
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
        else:
            # Create default settings
            default_settings = {
                "godot_dev_path": "E:\\Dev\\godot-dev",
                "module_name": "svg_module",
                "build_target": "editor",
                "platform": "windows"
            }
            with open(settings_file, 'w') as f:
                json.dump(default_settings, f, indent=2)
            return default_settings
    
    def check_python_version(self):
        """Verify Python version compatibility"""
        print("🐍 Checking Python version...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
            return False
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    
    def install_python_dependencies(self):
        """Install required Python packages"""
        print("📦 Installing Python dependencies...")
        
        packages = [
            "scons>=4.0",
            "requests",
            "certifi"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True, check=True)
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                print("STDERR:", e.stderr)
                return False
        
        return True
    
    def check_git_installation(self):
        """Verify Git is installed and accessible"""
        print("🔧 Checking Git installation...")
        try:
            result = subprocess.run(["git", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Git found: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Git not found. Please install Git for Windows:")
            print("   https://git-scm.com/download/win")
            return False
    
    def setup_visual_studio_tools(self):
        """Check for Visual Studio Build Tools"""
        print("🔨 Checking Visual Studio Build Tools...")
        
        # Common VS installation paths
        vs_paths = [
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools",
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools", 
            "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community",
            "C:\\Program Files\\Microsoft Visual Studio\\2019\\Community",
            "C:\\Program Files\\Microsoft Visual Studio\\2022\\Professional",
            "C:\\Program Files\\Microsoft Visual Studio\\2019\\Professional"
        ]
        
        vs_found = False
        for vs_path in vs_paths:
            if Path(vs_path).exists():
                print(f"✅ Found Visual Studio at: {vs_path}")
                vs_found = True
                break
        
        if not vs_found:
            print("❌ Visual Studio Build Tools not found")
            print("Please install Visual Studio Build Tools 2019 or later:")
            print("   https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022")
            print("Required components:")
            print("   - MSVC v143 compiler toolset")
            print("   - Windows 10/11 SDK")
            print("   - CMake tools for Visual Studio")
            return False
        
        # Check for vcvarsall.bat
        vcvars_paths = [
            "VC\\Auxiliary\\Build\\vcvarsall.bat",
            "VC\\Auxiliary\\Build\\vcvars64.bat"
        ]
        
        for vs_path in vs_paths:
            if not Path(vs_path).exists():
                continue
            for vcvars in vcvars_paths:
                vcvars_full = Path(vs_path) / vcvars
                if vcvars_full.exists():
                    print(f"✅ Found vcvarsall.bat at: {vcvars_full}")
                    return True
        
        print("⚠️  Visual Studio found but vcvarsall.bat not located")
        print("   Build may still work, continuing...")
        return True
    
    def clone_or_update_godot(self):
        """Clone Godot repository or update existing"""
        print(f"📥 Setting up Godot repository at {self.godot_path}...")
        
        if self.godot_path.exists():
            if (self.godot_path / ".git").exists():
                print("🔄 Updating existing Godot repository...")
                try:
                    subprocess.run(["git", "fetch"], cwd=self.godot_path, check=True)
                    subprocess.run(["git", "pull"], cwd=self.godot_path, check=True)
                    print("✅ Godot repository updated")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to update repository: {e}")
                    return False
            else:
                print(f"❌ Directory {self.godot_path} exists but is not a git repository")
                response = input("Remove and re-clone? (y/N): ")
                if response.lower() == 'y':
                    shutil.rmtree(self.godot_path)
                else:
                    return False
        
        # Clone fresh repository
        print("📦 Cloning Godot repository...")
        self.godot_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            subprocess.run([
                "git", "clone", 
                "https://github.com/godotengine/godot.git",
                str(self.godot_path)
            ], check=True)
            print("✅ Godot repository cloned successfully")
            
            # Switch to stable branch
            print("🔀 Switching to stable branch...")
            subprocess.run([
                "git", "checkout", "4.3-stable"
            ], cwd=self.godot_path, check=True)
            print("✅ Switched to 4.3-stable branch")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone repository: {e}")
            return False
    
    def setup_build_environment(self):
        """Set up the build environment variables"""
        print("⚙️  Setting up build environment...")
        
        # Create a batch file for setting up the environment
        setup_bat = self.project_root / "setup_build_env.bat"
        
        # Find Visual Studio installation
        vs_paths = [
            "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community",
            "C:\\Program Files\\Microsoft Visual Studio\\2022\\Professional", 
            "C:\\Program Files\\Microsoft Visual Studio\\2022\\Enterprise",
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community",
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Professional",
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Enterprise",
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools",
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools"
        ]
        
        vs_install_path = None
        for path in vs_paths:
            if Path(path).exists():
                vs_install_path = path
                break
        
        if vs_install_path:
            vcvarsall = Path(vs_install_path) / "VC" / "Auxiliary" / "Build" / "vcvarsall.bat"
            if vcvarsall.exists():
                setup_content = f'''@echo off
echo Setting up Godot build environment...
call "{vcvarsall}" x64
echo Environment ready for building!
echo.
echo Usage:
echo   cd {self.godot_path}
echo   scons target=editor platform=windows
echo.
cmd /k
'''
            else:
                setup_content = '''@echo off
echo Visual Studio environment not found
echo Please run this from a Visual Studio Developer Command Prompt
echo.
echo Or install Visual Studio Build Tools:
echo https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
echo.
pause
'''
        else:
            setup_content = '''@echo off
echo Visual Studio not found
echo Please install Visual Studio Build Tools:
echo https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
echo.
pause
'''
        
        setup_bat.write_text(setup_content)
        print(f"✅ Created build environment setup: {setup_bat}")
        return True
    
    def create_build_scripts(self):
        """Create convenient build scripts"""
        print("📝 Creating build scripts...")
        
        # Quick build script
        build_script = self.project_root / "build_godot.py"
        build_content = f'''#!/usr/bin/env python3
"""Quick build script for Godot with SVG module"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    godot_path = Path(r"{self.godot_path}")
    if not godot_path.exists():
        print("❌ Godot path not found. Run setup_dev_environment.py first")
        return 1
    
    # Change to Godot directory
    os.chdir(godot_path)
    
    # Build command
    cmd = [
        sys.executable, "-c", "import SCons.Script; SCons.Script.main()",
        "target=editor",
        "platform=windows",
        "module_svg_enabled=yes",
        "-j4"  # Use 4 cores
    ]
    
    print("🔨 Building Godot with SVG module...")
    print(f"Command: {{' '.join(cmd)}}")
    print(f"Working directory: {{godot_path}}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ Build completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with return code {{e.returncode}}")
        return 1
    except KeyboardInterrupt:
        print("\\n⚠️  Build interrupted by user")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        
        build_script.write_text(build_content)
        print(f"✅ Created build script: {build_script}")
        
        return True
    
    def test_build_system(self):
        """Test that the build system works"""
        print("🧪 Testing build system...")
        
        if not self.godot_path.exists():
            print("❌ Godot path doesn't exist")
            return False
        
        try:
            # Test SCons import
            subprocess.run([
                sys.executable, "-c", "import SCons; print('SCons version:', SCons.__version__)"
            ], check=True, cwd=self.godot_path)
            print("✅ SCons import test passed")
            
            # Test basic SCons functionality
            result = subprocess.run([
                sys.executable, "-c", "import SCons.Script; print('SCons.Script available')"
            ], capture_output=True, text=True, cwd=self.godot_path)
            
            if result.returncode == 0:
                print("✅ SCons build system test passed")
                return True
            else:
                print("❌ SCons build system test failed")
                print("STDERR:", result.stderr)
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Build system test failed: {e}")
            return False
    
    def create_development_readme(self):
        """Create a development guide"""
        print("📚 Creating development guide...")
        
        readme_content = f"""# Godot SVG Module Development Environment

## Setup Complete!

Your Godot development environment is now ready for building the SVG module.

### Paths
- **Godot Repository**: `{self.godot_path}`
- **SVG Module Source**: `{self.project_root}/modules/svg_module`

### Quick Start

1. **Copy module to Godot**:
   ```bash
   python tests/test_runner.py copy
   ```

2. **Build Godot with SVG module**:
   ```bash
   python build_godot.py
   ```

3. **Or use the test runner**:
   ```bash
   python tests/test_runner.py all
   ```

### Manual Build

If you prefer to build manually:

```bash
cd {self.godot_path}
python -c "import SCons.Script; SCons.Script.main()" target=editor platform=windows module_svg_enabled=yes
```

### Visual Studio Environment

To use Visual Studio Developer Command Prompt:
```bash
setup_build_env.bat
```

### Troubleshooting

- **Build errors**: Make sure Visual Studio Build Tools are installed
- **SCons not found**: Run `pip install scons`
- **Git errors**: Ensure Git for Windows is installed
- **Path issues**: Check that all paths in dev-settings.json are correct

### Development Workflow

1. Make changes to the SVG module in `modules/svg_module/`
2. Copy to Godot: `python tests/test_runner.py copy`
3. Build: `python build_godot.py`
4. Test in Godot editor

### Files Created
- `setup_build_env.bat` - Visual Studio environment setup
- `build_godot.py` - Quick build script
- `DEVELOPMENT_SETUP.md` - This guide

Happy coding! 🚀
"""
        
        readme_file = self.project_root / "DEVELOPMENT_SETUP.md"
        readme_file.write_text(readme_content)
        print(f"✅ Created development guide: {readme_file}")
        return True
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 Godot Development Environment Setup")
        print("=" * 50)
        print()
        
        steps = [
            ("Check Python version", self.check_python_version),
            ("Install Python dependencies", self.install_python_dependencies),
            ("Check Git installation", self.check_git_installation),
            ("Setup Visual Studio tools", self.setup_visual_studio_tools),
            ("Clone/update Godot repository", self.clone_or_update_godot),
            ("Setup build environment", self.setup_build_environment),
            ("Create build scripts", self.create_build_scripts),
            ("Test build system", self.test_build_system),
            ("Create development guide", self.create_development_readme)
        ]
        
        failed_steps = []
        
        for step_name, step_func in steps:
            print(f"📋 {step_name}...")
            try:
                if not step_func():
                    failed_steps.append(step_name)
                    print(f"❌ {step_name} failed")
                else:
                    print(f"✅ {step_name} completed")
            except Exception as e:
                print(f"❌ {step_name} failed with error: {e}")
                failed_steps.append(step_name)
            print()
        
        # Summary
        print("📊 Setup Summary")
        print("=" * 30)
        
        if not failed_steps:
            print("🎉 Setup completed successfully!")
            print()
            print("Next steps:")
            print("1. python tests/test_runner.py copy")
            print("2. python build_godot.py")
            print()
            print("See DEVELOPMENT_SETUP.md for detailed instructions.")
            return True
        else:
            print(f"❌ Setup completed with {len(failed_steps)} failed steps:")
            for step in failed_steps:
                print(f"   - {step}")
            print()
            print("Please resolve the failed steps and run setup again.")
            return False

def main():
    """Main setup function"""
    setup = GodotDevSetup()
    success = setup.run_setup()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
