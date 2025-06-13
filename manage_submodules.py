#!/usr/bin/env python3
"""
Submodule management script for PonSVG module
Provides easy commands for working with LunaSVG submodule
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

class SubmoduleManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.project_root = self.script_dir
        self.lunasvg_path = self.project_root / "modules" / "ponsvg" / "src" / "lunasvg"
        
    def run_command(self, command, cwd=None):
        """Run a shell command and return the result"""
        if cwd is None:
            cwd = self.project_root
        
        print(f"Running: {' '.join(command)}")
        print(f"Working directory: {cwd}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                print("Output:", result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return None
    
    def init_submodules(self):
        """Initialize and update all submodules"""
        print("Initializing submodules...")
        
        result = self.run_command(["git", "submodule", "update", "--init", "--recursive"])
        if result:
            print("✅ Submodules initialized successfully")
            return True
        else:
            print("❌ Failed to initialize submodules")
            return False
    
    def update_submodules(self):
        """Update all submodules to latest commits"""
        print("Updating submodules...")
        
        result = self.run_command(["git", "submodule", "update", "--recursive"])
        if result:
            print("✅ Submodules updated successfully")
            return True
        else:
            print("❌ Failed to update submodules")
            return False
    
    def status_submodules(self):
        """Show status of all submodules"""
        print("Checking submodule status...")
        
        result = self.run_command(["git", "submodule", "status"])
        if result:
            print("✅ Submodule status retrieved")
            return True
        else:
            print("❌ Failed to get submodule status")
            return False
    
    def update_lunasvg(self, version=None):
        """Update LunaSVG to a specific version or latest"""
        print(f"Updating LunaSVG to {'latest' if not version else version}...")
        
        if not self.lunasvg_path.exists():
            print("❌ LunaSVG submodule not found. Run 'init' first.")
            return False
        
        # Fetch latest changes
        result = self.run_command(["git", "fetch", "origin"], cwd=self.lunasvg_path)
        if not result:
            return False
        
        # Checkout specific version or master
        target = version if version else "master"
        result = self.run_command(["git", "checkout", target], cwd=self.lunasvg_path)
        if not result:
            return False
        
        # Get the commit hash
        result = self.run_command(["git", "rev-parse", "HEAD"], cwd=self.lunasvg_path)
        if result:
            commit_hash = result.stdout.strip()
            print(f"LunaSVG updated to commit: {commit_hash}")
        
        # Add the change to the main repository
        result = self.run_command(["git", "add", str(self.lunasvg_path)])
        if result:
            print("✅ LunaSVG update staged. Don't forget to commit the change!")
            print(f"git commit -m \"Update LunaSVG to {target}\"")
            return True
        else:
            print("❌ Failed to stage LunaSVG update")
            return False
    
    def check_lunasvg_version(self):
        """Check current LunaSVG version"""
        print("Checking LunaSVG version...")
        
        if not self.lunasvg_path.exists():
            print("❌ LunaSVG submodule not found")
            return False
        
        # Get current commit
        result = self.run_command(["git", "log", "--oneline", "-1"], cwd=self.lunasvg_path)
        if result:
            commit_info = result.stdout.strip()
            print(f"Current LunaSVG commit: {commit_info}")
        
        # Get current tag if any
        result = self.run_command(["git", "describe", "--tags", "--exact-match"], cwd=self.lunasvg_path)
        if result:
            tag = result.stdout.strip()
            print(f"Current LunaSVG tag: {tag}")
        else:
            print("Not on a tagged release")
        
        return True
    
    def reset_submodules(self):
        """Reset submodules to the committed state"""
        print("Resetting submodules to committed state...")
        
        result = self.run_command(["git", "submodule", "update", "--init", "--recursive"])
        if result:
            print("✅ Submodules reset successfully")
            return True
        else:
            print("❌ Failed to reset submodules")
            return False
    
    def verify_submodules(self):
        """Comprehensive verification of submodule integrity"""
        print("🔍 Performing comprehensive submodule verification...")
        
        all_good = True
        
        # Check if LunaSVG submodule exists and is initialized
        if not self.lunasvg_path.exists():
            print("❌ LunaSVG submodule directory not found")
            all_good = False
        else:
            print("✅ LunaSVG submodule directory exists")
        
        # Check if we're on a tagged release
        result = self.run_command(["git", "describe", "--tags", "--exact-match"], cwd=self.lunasvg_path)
        if result:
            tag = result.stdout.strip()
            print(f"✅ LunaSVG is on tagged release: {tag}")
        else:
            print("⚠️  LunaSVG is not on a tagged release (development commit)")
        
        # Verify key LunaSVG files exist
        lunasvg_files = [
            "include/lunasvg.h",
            "source/lunasvg.cpp",
            "source/svgelement.cpp",
            "source/svgparser.cpp",
            "CMakeLists.txt"
        ]
        
        for file in lunasvg_files:
            file_path = self.lunasvg_path / file
            if file_path.exists():
                print(f"✅ {file}")
            else:
                print(f"❌ Missing: {file}")
                all_good = False
        
        # Verify PlutoVG files (embedded in LunaSVG)
        plutovg_path = self.lunasvg_path / "plutovg"
        if not plutovg_path.exists():
            print("❌ PlutoVG directory not found")
            all_good = False
        else:
            print("✅ PlutoVG directory exists")
            
            plutovg_files = [
                "include/plutovg.h",
                "source/plutovg-canvas.c",
                "source/plutovg-rasterize.c",
                "source/plutovg-path.c"
            ]
            
            for file in plutovg_files:
                file_path = plutovg_path / file
                if file_path.exists():
                    print(f"✅ plutovg/{file}")
                else:
                    print(f"❌ Missing: plutovg/{file}")
                    all_good = False
        
        # Check submodule commit matches repository expectation
        result = self.run_command(["git", "ls-tree", "HEAD", str(self.lunasvg_path.relative_to(self.project_root))])
        if result:
            expected_commit = result.stdout.split()[2]
            result2 = self.run_command(["git", "rev-parse", "HEAD"], cwd=self.lunasvg_path)
            if result2:
                actual_commit = result2.stdout.strip()
                if expected_commit == actual_commit:
                    print(f"✅ Submodule commit matches repository: {expected_commit[:8]}")
                else:
                    print(f"⚠️  Submodule commit mismatch:")
                    print(f"   Repository expects: {expected_commit[:8]}")
                    print(f"   Submodule is at:    {actual_commit[:8]}")
        
        # Summary
        if all_good:
            print("\n🎉 All submodule checks passed!")
            return True
        else:
            print("\n⚠️  Some submodule issues were found. Consider running 'reset' or 'init'.")
            return False

def main():
    parser = argparse.ArgumentParser(description="Manage PonSVG submodules")
    parser.add_argument("command", choices=[
        "init", "update", "status", "update-lunasvg", "version", "reset", "verify"
    ], help="Command to execute")
    parser.add_argument("--version", help="Specific version/tag for update-lunasvg")
    
    args = parser.parse_args()
    
    manager = SubmoduleManager()
    
    if args.command == "init":
        success = manager.init_submodules()
    elif args.command == "update":
        success = manager.update_submodules()
    elif args.command == "status":
        success = manager.status_submodules()
    elif args.command == "update-lunasvg":
        success = manager.update_lunasvg(args.version)
    elif args.command == "version":
        success = manager.check_lunasvg_version()
    elif args.command == "reset":
        success = manager.reset_submodules()
    elif args.command == "verify":
        success = manager.verify_submodules()
    else:
        print(f"Unknown command: {args.command}")
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
