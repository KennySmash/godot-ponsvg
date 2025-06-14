# Convert Godot Module to GDExtension
# PowerShell script to convert source files from module format to GDExtension format

param(
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

function Write-ConversionStep {
    param([string]$Message)
    Write-Host "🔄 $Message" -ForegroundColor Cyan
}

function Write-ConversionSuccess {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-ConversionError {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Define the conversion mappings
$headerMappings = @{
    '#include "core/object/class_db.h"' = '#include <godot_cpp/core/class_db.hpp>'
    '#include "core/io/file_access.h"' = '#include <godot_cpp/classes/file_access.hpp>'
    '#include "core/error/error_macros.h"' = '#include <godot_cpp/variant/utility_functions.hpp>'
    '#include "core/os/time.h"' = '#include <godot_cpp/classes/time.hpp>'
    '#include "core/variant/variant.h"' = '#include <godot_cpp/variant/utility_functions.hpp>'
    '#include "core/io/resource.h"' = '#include <godot_cpp/classes/resource.hpp>'
    '#include "scene/resources/texture.h"' = '#include <godot_cpp/classes/texture2d.hpp>'
    '#include "scene/resources/image.h"' = '#include <godot_cpp/classes/image.hpp>'
    '#include "scene/2d/node_2d.h"' = '#include <godot_cpp/classes/node2d.hpp>'
    '#include "scene/2d/sprite_2d.h"' = '#include <godot_cpp/classes/sprite2d.hpp>'
    '#include "core/object/ref_counted.h"' = '#include <godot_cpp/classes/ref_counted.hpp>'
    '#include "core/math/vector2.h"' = '#include <godot_cpp/variant/vector2.hpp>'
    '#include "core/math/color.h"' = '#include <godot_cpp/variant/color.hpp>'
    '#include "core/variant/dictionary.h"' = '#include <godot_cpp/variant/dictionary.hpp>'
    '#include "scene/resources/shader.h"' = '#include <godot_cpp/classes/shader.hpp>'
    '#include "scene/resources/shader_material.h"' = '#include <godot_cpp/classes/shader_material.hpp>'
}

$classMappings = @{
    'GDCLASS\(' = 'GDCLASS('
    'GDREGISTER_CLASS\(' = 'ClassDB::register_class<'
    'ERR_PRINT\(' = 'UtilityFunctions::push_error('
    'ERR_FAIL_COND_V_MSG\(' = 'if ('
    'ClassDB::bind_method\(' = 'ClassDB::bind_method('
    'ADD_PROPERTY\(' = 'ClassDB::bind_get_set_property('
}

# Files to convert
$filesToConvert = @(
    @{ Source = "modules\ponsvg\src\svg_texture.h"; Dest = "src\svg_texture.h" },
    @{ Source = "modules\ponsvg\src\svg_texture.cpp"; Dest = "src\svg_texture.cpp" },
    @{ Source = "modules\ponsvg\src\svg_sprite.h"; Dest = "src\svg_sprite.h" },
    @{ Source = "modules\ponsvg\src\svg_sprite.cpp"; Dest = "src\svg_sprite.cpp" }
)

Write-ConversionStep "Starting GDExtension conversion..."

foreach ($file in $filesToConvert) {
    if (-not (Test-Path $file.Source)) {
        Write-ConversionError "Source file not found: $($file.Source)"
        continue
    }
    
    Write-ConversionStep "Converting $($file.Source) -> $($file.Dest)"
    
    if (-not $DryRun) {
        # Copy the file
        Copy-Item -Path $file.Source -Destination $file.Dest -Force
        
        # Read content
        $content = Get-Content -Path $file.Dest -Raw
        
        # Apply header mappings
        foreach ($mapping in $headerMappings.GetEnumerator()) {
            $content = $content -replace [regex]::Escape($mapping.Key), $mapping.Value
        }
        
        # Apply class name changes
        $content = $content -replace "PonPonSVG", "PonSVG"
        
        # Add using namespace godot; after includes
        if ($content -match '#include <godot_cpp/') {
            $content = $content -replace '(#include <godot_cpp/.*?\n)', "`$1`nusing namespace godot;`n"
        }
        
        # Apply error macro changes  
        $content = $content -replace 'ERR_PRINT\((.*?)\)', 'UtilityFunctions::push_error($1)'
        $content = $content -replace 'ERR_FAIL_COND_V_MSG\((.*?), (.*?), (.*?)\)', 'if ($1) { UtilityFunctions::push_error($3); return $2; }'
        
        # Write back
        Set-Content -Path $file.Dest -Value $content
        
        Write-ConversionSuccess "Converted: $($file.Dest)"
    } else {
        Write-Host "Would convert: $($file.Source) -> $($file.Dest)" -ForegroundColor Yellow
    }
}

Write-ConversionSuccess "Conversion complete!"

if (-not $DryRun) {
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Review converted files for any remaining issues"
    Write-Host "2. Run: python build_gdextension.py --build-type Debug"
    Write-Host "3. Test the extension in Godot"
}
