# Push PonSVG to GitHub Repository
# Sets up the remote repository and pushes the current state

param(
    [string]$RemoteUrl = "https://github.com/KennySmash/godot-ponsvg.git",
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "🔧 $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

Write-Step "Setting up PonSVG GitHub repository..."

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Error "Not in a git repository. Please run from the project root."
    exit 1
}

# Check if remote already exists
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote -and -not $Force) {
    Write-Warning "Remote 'origin' already exists: $existingRemote"
    Write-Host "Use -Force to override"
    exit 1
}

try {
    # Set up the remote
    if ($existingRemote) {
        Write-Step "Updating remote origin URL..."
        git remote set-url origin $RemoteUrl
    } else {
        Write-Step "Adding remote origin..."
        git remote add origin $RemoteUrl
    }
    
    # Verify remote
    $currentRemote = git remote get-url origin
    Write-Success "Remote configured: $currentRemote"
    
    # Create main branch if we're on master
    $currentBranch = git branch --show-current
    if ($currentBranch -eq "master") {
        Write-Step "Creating main branch..."
        git branch -M main
    }
    
    # Push to repository
    Write-Step "Pushing to GitHub..."
    if ($Force) {
        git push -u origin main --force
    } else {
        git push -u origin main
    }
    
    Write-Success "Successfully pushed PonSVG to GitHub!"
    Write-Host ""
    Write-Host "Repository URL: $RemoteUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Fix the remaining GDExtension compilation issues"
    Write-Host "2. Test the extension in Godot 4.3"
    Write-Host "3. Set up GitHub Actions for automated builds"
    Write-Host "4. Create release packages for distribution"
    
} catch {
    Write-Error "Failed to push to GitHub: $($_.Exception.Message)"
    exit 1
}

# Create README update with current status
$readmeUpdate = @"

## 🚀 Current Status (December 2025)

**Architecture**: Converting from Godot built-in module to GDExtension for compatibility with official Godot releases.

### ✅ Completed
- Core SVG parsing and rendering using LunaSVG 3.3.0
- Symbol extraction and style override system
- Basic caching and LOD support
- GDExtension project structure
- CMake build system
- godot-cpp integration

### 🔧 In Progress  
- Fixing GDExtension API compatibility issues
- Texture2D virtual method signatures
- Dictionary cache entry conversion
- Include path corrections

### 📋 Next Steps
1. Complete GDExtension conversion
2. Cross-platform build testing
3. GitHub Actions automation
4. Release packaging system

## Installation (Coming Soon)

Once the GDExtension conversion is complete, installation will be as simple as:

1. Download the latest release package
2. Extract to your project's `addons/` folder
3. Enable the plugin in Project Settings

No Godot compilation required! 🎉

"@

# Append to README if it doesn't already contain status
$readmePath = "README.md"
if (Test-Path $readmePath) {
    $currentReadme = Get-Content $readmePath -Raw
    if (-not ($currentReadme -match "Current Status")) {
        Add-Content $readmePath $readmeUpdate
        Write-Success "Updated README.md with current status"
    }
}
