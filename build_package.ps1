# Build and Package PonSVG Module
# PowerShell script for local development and release preparation

param(
    [string]$Version = "",
    [switch]$Package = $false,
    [switch]$Test = $false,
    [switch]$Clean = $false,
    [string]$OutputDir = "build"
)

$ErrorActionPreference = "Stop"
$ModuleName = "ponsvg"

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Yellow
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message)
    Write-Host "🔧 $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Test-Requirements {
    Write-Step "Checking build requirements..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "   Python: $pythonVersion"
    }
    catch {
        Write-Error "Python not found. Please install Python 3.8+"
        exit 1
    }
    
    # Check Git
    try {
        $gitVersion = git --version
        Write-Host "   Git: $gitVersion"
    }
    catch {
        Write-Error "Git not found. Please install Git"
        exit 1
    }
    
    # Check module structure
    if (-not (Test-Path "modules\$ModuleName\config.py")) {
        Write-Error "Module not found at modules\$ModuleName"
        exit 1
    }
    
    # Check LunaSVG submodule
    if (-not (Test-Path "modules\$ModuleName\src\lunasvg\include\lunasvg.h")) {
        Write-Warning "LunaSVG submodule not initialized. Initializing..."
        git submodule update --init --recursive
        if (-not (Test-Path "modules\$ModuleName\src\lunasvg\include\lunasvg.h")) {
            Write-Error "Failed to initialize LunaSVG submodule"
            exit 1
        }
    }
    
    Write-Success "All requirements met"
}

function Invoke-ModuleValidation {
    Write-Step "Validating module structure..."
    
    $requiredFiles = @(
        "modules\$ModuleName\config.py",
        "modules\$ModuleName\src\register_types.h",
        "modules\$ModuleName\src\register_types.cpp",
        "modules\$ModuleName\src\svg_resource.h",
        "modules\$ModuleName\src\svg_resource.cpp",
        "modules\$ModuleName\src\lunasvg_integration.h",
        "modules\$ModuleName\src\lunasvg_integration.cpp"
    )
    
    $missingFiles = @()
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Error "Missing required files:"
        foreach ($file in $missingFiles) {
            Write-Host "   - $file" -ForegroundColor Red
        }
        exit 1
    }
    
    # Test config.py syntax
    Write-Step "Testing config.py syntax..."
    $configTest = python -c "
import sys
sys.path.insert(0, 'modules/$ModuleName')
try:
    import config
    print('Config import: OK')
    result = config.can_build(None, 'windows')
    print(f'can_build(): {result}')
    classes = config.get_doc_classes()
    print(f'doc_classes: {classes}')
    print('VALIDATION_PASSED')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>&1
    
    if ($configTest -match "VALIDATION_PASSED") {
        Write-Success "Module validation passed"
    } else {
        Write-Error "Module validation failed:"
        Write-Host $configTest -ForegroundColor Red
        exit 1
    }
}

function New-ModulePackage {
    param([string]$Version, [string]$OutputDir)
    
    Write-Step "Creating module package..."
    
    if (-not $Version) {
        # Try to get version from git tags
        try {
            $Version = git describe --tags --abbrev=0 2>$null
            if (-not $Version) {
                $Version = "v0.1.0-dev"
            }
        }
        catch {
            $Version = "v0.1.0-dev"
        }
    }
      $buildDir = New-Item -ItemType Directory -Path $OutputDir -Force
    $packageName = "ponsvg-module-$Version-windows-x86_64"
    $packageDir = New-Item -ItemType Directory -Path "$buildDir\$packageName" -Force
    
    Write-Host "   Package: $packageName"
    Write-Host "   Output: $packageDir"
    
    # Copy module files
    $moduleSource = "modules\$ModuleName"
    $moduleDestination = "$packageDir\modules\$ModuleName"
    
    Write-Step "Copying module files..."
    
    # Create directory structure
    New-Item -ItemType Directory -Path "$packageDir\modules" -Force | Out-Null
    
    # Copy files excluding git and build artifacts
    robocopy $moduleSource $moduleDestination /E /XD .git build __pycache__ .vscode /XF *.pyc *.pyo | Out-Null
    
    # Copy documentation
    $docFiles = @("README.md", "Featureset.md", "tests\test_module.py")
    foreach ($doc in $docFiles) {
        if (Test-Path $doc) {
            Copy-Item $doc $packageDir
        }
    }
    
    # Create installation guide
    $installGuide = @"
# PonSVG Module Installation

Version: $Version
Platform: Windows (x86_64)
Build Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")

## Quick Installation

1. **Copy module to Godot source**:
   ``````
   Copy-Item -Recurse modules\ponsvg C:\path\to\godot\modules\
   ``````

2. **Build Godot with the module**:
   ``````
   cd C:\path\to\godot
   scons platform=windows target=editor module_ponsvg_enabled=yes
   ``````

3. **Verify installation** by checking if PonSVGResource is available in Godot

## Requirements

- Godot Engine 4.2+ source code
- SCons build system  
- Visual Studio Build Tools 2019+
- Python 3.8+

## Usage Example

``````gdscript
# Load SVG
var ponsvg = PonSVGResource.new()
ponsvg.load_from_file("res://icon.svg")

# Create texture  
var texture = PonSVGTexture.new()
texture.ponsvg_resource = ponsvg
texture.render_size = Vector2i(256, 256)

# Use in sprite
var sprite = PonSVGSprite2D.new()
sprite.ponsvg_resource = ponsvg
add_child(sprite)
``````

## Support

For issues and documentation, visit:
https://github.com/yourusername/ponsvg-module
"@
    
    Set-Content -Path "$packageDir\INSTALLATION.md" -Value $installGuide
    
    # Create ZIP package
    Write-Step "Creating ZIP archive..."
    $zipPath = "$buildDir\$packageName.zip"
    
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($packageDir, $zipPath)
    
    # Create latest symlink
    $latestPath = "$buildDir\latest.txt"
    Set-Content -Path $latestPath -Value $packageName
    
    Write-Success "Package created: $zipPath"
    return $zipPath
}

function Invoke-Tests {
    Write-Step "Running module tests..."
    
    # Run Python validation tests
    python -c "
import sys
from pathlib import Path

print('🔍 Running comprehensive module tests...')

# Test 1: Module structure
print('📁 Testing module structure...')
required_files = [
    'modules/ponsvg/config.py',
    'modules/ponsvg/src/register_types.h',
    'modules/ponsvg/src/register_types.cpp',
    'modules/ponsvg/src/svg_resource.h'
]

for file_path in required_files:
    if not Path(file_path).exists():
        print(f'❌ Missing: {file_path}')
        sys.exit(1)

print('✅ Module structure OK')

# Test 2: Config validation  
print('⚙️  Testing config.py...')
sys.path.insert(0, 'modules/ponsvg')
import config

try:
    can_build_result = config.can_build(None, 'windows')
    doc_classes = config.get_doc_classes()
    print(f'✅ can_build: {can_build_result}')
    print(f'✅ doc_classes: {doc_classes}')
except Exception as e:
    print(f'❌ Config test failed: {e}')
    sys.exit(1)

# Test 3: LunaSVG integration
print('🎨 Testing LunaSVG integration...')
lunasvg_header = Path('modules/ponsvg/src/lunasvg/include/lunasvg.h')
if not lunasvg_header.exists():
    print('❌ LunaSVG header not found')
    sys.exit(1)

print('✅ LunaSVG integration OK')

print('🎉 All tests passed!')
"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "All tests passed"
    } else {
        Write-Error "Tests failed"
        exit 1
    }
}

function Clear-BuildArtifacts {
    Write-Step "Cleaning build artifacts..."
    
    $cleanPaths = @(
        $OutputDir,
        "modules\$ModuleName\src\*.o",
        "modules\$ModuleName\src\*.obj", 
        "**\__pycache__",
        "**\*.pyc"
    )
    
    foreach ($path in $cleanPaths) {
        if (Test-Path $path) {
            Write-Host "   Removing: $path"
            Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Success "Clean complete"
}

# Main execution
try {
    Write-Header "PonSVG Module Build Script"
    
    if ($Clean) {
        Clear-BuildArtifacts
        exit 0
    }
    
    Test-Requirements
    Invoke-ModuleValidation
    
    if ($Test) {
        Invoke-Tests
    }
    
    if ($Package) {
        $packagePath = New-ModulePackage -Version $Version -OutputDir $OutputDir
        Write-Host ""
        Write-Success "Build complete!"
        Write-Host "Package created: $packagePath" -ForegroundColor Cyan
        
        # Show package contents
        Write-Host ""
        Write-Host "Package contents:" -ForegroundColor Yellow
        $extractDir = "$OutputDir\temp_extract"
        Expand-Archive -Path $packagePath -DestinationPath $extractDir -Force
        Get-ChildItem $extractDir -Recurse | ForEach-Object {
            $relativePath = $_.FullName.Replace("$extractDir\", "")
            if ($_.PSIsContainer) {
                Write-Host "   📁 $relativePath" -ForegroundColor Blue
            } else {
                Write-Host "   📄 $relativePath" -ForegroundColor Gray
            }
        }
        Remove-Item $extractDir -Recurse -Force
    }
    
    Write-Host ""
    Write-Success "Script completed successfully!"
}
catch {
    Write-Error "Script failed: $($_.Exception.Message)"
    exit 1
}
