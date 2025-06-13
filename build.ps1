# PonSVG Build Management Script
# PowerShell script for building and managing PonSVG Godot builds

param(
    [string]$Action = "build",  # build, clean, list
    [switch]$DryRun,
    [switch]$All,
    [int]$MaxBuilds = 5
)

$ErrorActionPreference = "Stop"

function Show-Usage {
    Write-Host "PonSVG Build Management Script"
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\build.ps1                    # Build Godot with PonSVG"
    Write-Host "  .\build.ps1 -Action clean      # Clean old builds"
    Write-Host "  .\build.ps1 -Action list       # List existing builds"
    Write-Host "  .\build.ps1 -Action clean -All # Clean all builds"
    Write-Host ""
}

function Invoke-Build {
    Write-Host "Building Godot with PonSVG module..." -ForegroundColor Green
    
    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Using: $pythonVersion"
    }
    catch {
        Write-Error "Python not found. Please install Python and add it to PATH."
        return
    }
    
    # Run the Python build script
    try {
        python build_godot.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Build completed successfully!" -ForegroundColor Green
            Write-Host "Built package available in: build/latest/" -ForegroundColor Cyan
        }
        else {
            Write-Error "Build failed with exit code $LASTEXITCODE"
        }
    }
    catch {
        Write-Error "Failed to run build script: $_"
    }
}

function Invoke-Clean {
    Write-Host "Cleaning build directories..." -ForegroundColor Yellow
    
    $cleanArgs = @()
    if ($DryRun) { $cleanArgs += "--dry-run" }
    if ($All) { $cleanArgs += "--all" }
    if (-not $All) { $cleanArgs += "--max-builds", $MaxBuilds }
    
    try {
        python clean_builds.py @cleanArgs
    }
    catch {
        Write-Error "Failed to run clean script: $_"
    }
}

function Invoke-List {
    Write-Host "Listing build directories..." -ForegroundColor Cyan
    
    try {
        python clean_builds.py --list
    }
    catch {
        Write-Error "Failed to run list command: $_"
    }
}

# Main execution
switch ($Action.ToLower()) {
    "build" { Invoke-Build }
    "clean" { Invoke-Clean }
    "list" { Invoke-List }
    "help" { Show-Usage }
    default {
        Write-Error "Unknown action: $Action"
        Show-Usage
    }
}
