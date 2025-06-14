# PonSVG - Advanced SVG Rendering for Godot 4

A high-performance GDExtension that brings professional-grade SVG rendering and manipulation capabilities to Godot 4, featuring resolution-independent graphics, runtime style overrides, intelligent caching, and seamless integration with official Godot builds.

## ✨ Key Features

- **🎨 Complete SVG Support**: Render full SVG files as Texture2D resources with perfect vector quality
- **🎯 Symbol Extraction**: Extract and render individual `<symbol>` elements as standalone sprites
- **🎨 Runtime Style Overrides**: Modify colors, opacity, CSS properties, and classes without touching source files
- **⚡ Performance Optimized**: Intelligent caching system with LOD (Level of Detail) support
- **🔧 GDExtension Architecture**: Works with official Godot builds - no source compilation required
- **🌐 Cross-Platform**: Windows, Linux, and macOS support with automated builds
- **📦 Easy Installation**: Drop-in addon format with automated packaging and releases

## 🏗️ Architecture Overview

### Core Classes

- **`PonSVGResource`**: Central SVG management with DOM traversal, style overrides, and caching
- **`PonSVGTexture`**: Full SVG document rendering as Texture2D with intelligent optimization
- **`PonSVGSprite2D`**: Individual symbol/element rendering with style controls and material support
- **LunaSVG Integration**: High-performance C++ SVG parser and renderer (v3.3.0)

### Performance Features

- **Smart Caching**: Automatic cache management with style-aware invalidation and timestamp tracking
- **LOD System**: Configurable quality/performance trade-offs with adaptive sizing (0.1x to 4.0x scale)
- **Memory Efficiency**: Efficient texture reuse, cache size limits, and cleanup automation
- **CPU Optimization**: O(1) cache lookups, minimal DOM queries, and batch style applications

### Enhanced Style Override System

- **Fill & Stroke Colors**: Runtime color changes with full alpha support
- **CSS Property Overrides**: Apply any CSS property to specific elements by ID
- **Class-Based Styling**: Target multiple elements using CSS class selectors (`.classname`)
- **Hierarchical Application**: Overrides automatically apply to child elements
- **Persistent Storage**: Overrides survive document reloads and are included in cache keys

## 🚀 Installation

### Automatic Installation (Recommended)

1. **Download** the latest release from [GitHub Releases](https://github.com/KennySmash/godot-ponsvg/releases)
2. **Extract** the archive to your project's root directory
3. **Enable** the plugin in Project Settings > Plugins > PonSVG

### Manual Installation

1. **Copy** the `addons/ponsvg/` folder to your project's `addons/` directory
2. **Enable** "PonSVG" in Project Settings > Plugins
3. **Restart** Godot if prompted

### Build from Source

```powershell
# Clone repository with submodules
git clone --recursive https://github.com/KennySmash/godot-ponsvg.git
cd godot-ponsvg

# Build GDExtension (Windows)
python build_gdextension.py --platform windows --config release

# Build GDExtension (Linux/macOS)
python build_gdextension.py --platform linux --config release

## 🚀 Usage Examples

### Basic SVG Loading and Display

```gdscript
# Load an SVG file as a resource
var svg_resource = PonSVGResource.new()
svg_resource.load_from_file("res://icons/ui_icons.svg")

# Display the full SVG as a texture
var svg_texture = PonSVGTexture.new()
svg_texture.ponsvg_resource = svg_resource
svg_texture.render_size = Vector2i(512, 512)

# Use in a TextureRect or Sprite2D
$TextureRect.texture = svg_texture
```

### Symbol-Based Sprite System

```gdscript
# Load SVG with multiple symbol definitions
var icon_library = PonSVGResource.new()
icon_library.load_from_file("res://ui/icon_library.svg")

# Create sprites for individual symbols
var play_button = PonSVGSprite2D.new()
play_button.ponsvg_resource = icon_library
play_button.symbol_id = "play_icon"
play_button.draw_size = Vector2(64, 64)
add_child(play_button)

var pause_button = PonSVGSprite2D.new()
pause_button.ponsvg_resource = icon_library
pause_button.symbol_id = "pause_icon"
pause_button.draw_size = Vector2(64, 64)
add_child(pause_button)
```

### Runtime Style Overrides

```gdscript
# Load SVG with elements that have IDs
var svg_resource = PonSVGResource.new()
svg_resource.load_from_file("res://ui/button.svg")

# Change individual element colors by ID
svg_resource.override_fill_color("star_path", Color.GOLD)
svg_resource.override_stroke_color("circle_border", Color.NAVY)

# Apply CSS properties to elements
svg_resource.override_css_property("text_element", "font-size", "24px")
svg_resource.override_css_property("background", "opacity", "0.8")

# Apply style to all elements with a specific class
svg_resource.override_fill_color(".highlight", Color.YELLOW)
svg_resource.override_stroke_color(".border", Color.BLACK)

# Changes are applied immediately to all textures using this resource
var styled_texture = PonSVGTexture.new()
styled_texture.ponsvg_resource = svg_resource
styled_texture.render_size = Vector2i(256, 256)
```

### Performance Optimization

```gdscript
# Enable caching for frequently used SVGs
var svg_resource = PonSVGResource.new()
svg_resource.cache_enabled = true
svg_resource.load_from_file("res://ui/icons.svg")

# Configure LOD for quality/performance balance
svg_resource.lod_enabled = true
svg_resource.lod_bias = 1.2  # Slightly higher quality

# Monitor cache performance
print("Cache size: ", svg_resource.get_cache_size())
print("Cache enabled: ", svg_resource.is_cache_enabled())

# Manual cache management
svg_resource.clear_cache()  # Clear when memory is needed
```

### Advanced Symbol Management

```gdscript
# Extract all available symbols
var symbol_ids = svg_resource.get_symbol_ids()
print("Available symbols: ", symbol_ids)

# Get detailed symbol information
for symbol_id in symbol_ids:
    var symbol_data = svg_resource.get_symbol_data(symbol_id)
    print("Symbol: ", symbol_id)
    print("  Bounds: ", symbol_data.get("bounds", Rect2()))
    print("  ViewBox: ", symbol_data.get("viewbox", ""))

# Render individual symbols at different sizes
var large_icon = svg_resource.rasterize_symbol("star", Vector2i(128, 128))
var small_icon = svg_resource.rasterize_symbol("star", Vector2i(32, 32))
```

## 📚 API Reference

### PonSVGResource

Core class for loading and managing SVG documents.

#### Methods

- `Error load_from_file(String path)` - Load SVG from file
- `Error load_from_string(String svg_data)` - Load SVG from string
- `PackedStringArray get_symbol_ids()` - Get all symbol IDs
- `bool has_symbol(String id)` - Check if symbol exists
- `Dictionary get_symbol_data(String id)` - Get symbol information
- `void override_fill(String element_id, Color color)` - Override fill color
- `void override_stroke(String element_id, Color color)` - Override stroke color
- `void clear_fill_override(String element_id)` - Clear fill override
- `void clear_all_overrides()` - Clear all overrides
- `Ref<Image> rasterize_full(Vector2i size)` - Render full SVG to image
- `Ref<Image> rasterize_symbol(String symbol_id, Vector2i size)` - Render symbol to image

### PonSVGTexture

Texture2D implementation for displaying SVG content.

#### Properties

- `PonSVGResource ponsvg_resource` - The source SVG resource
- `Vector2i render_size` - Target rendering resolution

#### Methods

- `void force_update()` - Force texture regeneration
- Standard Texture2D interface (get_width, get_height, etc.)

### PonSVGSprite2D

Node2D for displaying SVG content or individual symbols.

#### Properties

- `PonSVGResource ponsvg_resource` - The source SVG resource
- `String symbol_id` - ID of symbol to display (empty for full SVG)
- `Vector2 draw_size` - Display size in pixels
- `bool centered` - Whether to center the sprite
- `Color modulate` - Color modulation
- `ShaderMaterial material_override` - Custom material

#### Methods

- `void force_update()` - Force sprite regeneration
- `Rect2 get_rect()` - Get sprite bounds

## ⚙️ Installation & Build

### Prerequisites

- Godot 4.x source code
- C++ compiler with C++17 support
- Git for cloning repositories

### Installation Steps

1. **Clone this module into your Godot source tree:**
   ```bash
   cd path/to/godot/modules/
   git clone https://github.com/your-repo/gotot-svg-module.git ponsvg
   ```

2. **Initialize the LunaSVG submodule:**
   ```bash
   cd ponsvg/modules/ponsvg/src/
   git clone https://github.com/sammycage/lunasvg.git
   ```

3. **Build Godot with the module:**
   ```bash
   cd path/to/godot/
   scons platform=windows target=editor module_ponsvg_enabled=yes
   # or for other platforms:
   # scons platform=linux target=editor module_ponsvg_enabled=yes
   # scons platform=macos target=editor module_ponsvg_enabled=yes
   ```

### Verification

After building, the following classes should be available in Godot:
- `PonSVGResource`
- `PonSVGTexture` 
- `PonSVGSprite2D`

You can test the installation with:
```gdscript
var svg = PonSVGResource.new()
print("PonSVG Module loaded successfully!")
```

## 🔧 Advanced Features

### Performance Optimization

The module includes several performance optimizations:

- **Intelligent Caching**: Rendered images are cached and only regenerated when necessary
- **Lazy Loading**: SVG parsing and symbol extraction happen on-demand
- **Efficient Updates**: Style overrides trigger minimal re-rendering

### Element Targeting

SVG elements can be targeted for style overrides using their `id` attribute:

```xml
<svg>
  <circle id="main_circle" cx="50" cy="50" r="25" fill="blue"/>
  <path id="star_path" d="..." fill="gold"/>
</svg>
```

```gdscript
# Target specific elements by ID
ponsvg_resource.override_fill("main_circle", Color.RED)
ponsvg_resource.override_stroke("star_path", Color.BLACK)
```

### Building from Source

1. Clone this repository into your Godot source `modules/` directory:

```bash
cd path/to/godot/modules/
git clone https://github.com/your-repo/gotot-svg-module.git ponsvg
```

2. Initialize the LunaSVG submodule:

```bash
cd ponsvg
git submodule update --init --recursive
```

3. Build Godot with the module:

```bash
cd ../../  # Back to Godot root
scons platform=windows target=editor module_ponsvg_enabled=yes
```

### Requirements

- Godot 4.x source code
- C++17 compatible compiler
- LunaSVG library (included as submodule)

## 📋 Current Implementation Status

### ✅ Completed Features

- [x] **Core Infrastructure**: Module structure, build system, and Godot integration
- [x] **LunaSVG Integration**: Complete v3.3.0 library integration with C++ wrapper
- [x] **SVG Loading & Parsing**: File and string loading with full DOM access
- [x] **Symbol Extraction**: Complete symbol ID mapping with bounds calculation
- [x] **Rendering Pipeline**: Full SVG and individual symbol rasterization
- [x] **Style Overrides**: Real-time fill/stroke color changes with immediate application
- [x] **Performance Optimization**: Intelligent caching system with automatic invalidation
- [x] **LOD System**: Level-of-detail rendering with configurable quality/performance trade-offs
- [x] **Memory Management**: Efficient cache storage with size tracking and clearing
- [x] **Image Processing**: High-quality Lanczos scaling for LOD size differences
- [x] **API Completeness**: Comprehensive GDScript API with properties and methods

### 🚧 In Progress

- [ ] **Shader Override System**: Complete implementation with Godot rendering pipeline integration
- [ ] **Cache Management**: LRU eviction and memory limit configuration
- [ ] **Editor Integration**: Visual symbol browser and inspector plugins

### 📅 Planned Features

- [ ] **Advanced Editor Tools**: SVG preview, symbol picker, and performance profiler
- [ ] **Rendering Enhancements**: SDF rendering, custom filters, and collision shape generation
- [ ] **Platform Optimization**: GPU-accelerated paths and mobile-specific optimizations
- [ ] **Extended Format Support**: SVG 2.0 features and advanced CSS properties

## 🧪 Testing

A comprehensive test suite is included in the `tests/` directory:

```bash
# Check development environment status
python tests/test_runner.py status

# Deploy module to Godot development environment  
python tests/test_runner.py deploy

# Run full development cycle (copy, build, test)
python tests/test_runner.py all
```

Configure your Godot development path in `dev-settings.json`:

```json
{
  "godot_dev_path": "E:\\Dev\\godot-dev",
  "module_name": "ponsvg",
  "build_target": "editor",
  "platform": "windows"
}
```

See `tests/README.md` for detailed testing documentation and GDScript test examples.

## 🎨 Advanced Features (Roadmap)

### Signed Distance Field (SDF) Rendering

- Ultra-sharp vector graphics at any scale
- GPU-accelerated anti-aliasing
- Minimal memory footprint for complex shapes

### Smart Caching & LOD

- Automatic level-of-detail based on screen size
- Intelligent texture caching for static elements
- Render-to-texture optimization for complex SVGs

### Vector Collision Shapes

- Auto-generate `CollisionShape2D` from SVG paths
- Perfect collision detection matching visual appearance

### Rich Filter Support

- SVG gradient rendering (`<linearGradient>`, `<radialGradient>`)
- Filter effects (blur, drop shadow, color matrix)
- Pattern fills and advanced styling

## 🤝 Contributing

This project follows Godot's contribution guidelines. Key areas where help is needed:

1. **LunaSVG Integration**: C++ wrapper implementation
2. **Performance Optimization**: Caching and rendering pipeline
3. **Editor Tools**: Inspector plugins and symbol selection UI
4. **Testing**: Cross-platform compatibility and edge cases
5. **Documentation**: API reference and usage examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

LunaSVG is included under its own license terms.

## 🙏 Acknowledgments

- [LunaSVG](https://github.com/sammycage/lunasvg) - High-performance SVG parsing and rendering
- Godot Engine community for module development resources
- Contributors and testers who help improve this project

---

**Status**: Production Ready (Core Features) | **Godot Version**: 4.x | **Platform Support**: Windows, Linux, macOS

**Performance**: Intelligent caching, LOD system, memory optimization | **Quality**: High-fidelity vector rendering

## 🔄 Release & Automation

### Automated Releases

This project uses GitHub Actions for automated building and releasing:

- **Release Creation**: Create releases by pushing git tags (e.g., `git tag v1.0.0 && git push origin v1.0.0`)
- **Multi-platform Builds**: Automatic builds for Windows, Linux, and macOS
- **Auto-generated Changelogs**: Smart changelog generation from commit history
- **Cross-platform Packages**: ZIP for Windows, tar.gz for Unix systems

### Local Development

Use the provided PowerShell script for local builds:

```powershell
# Test and validate module
.\build_package.ps1 -Test

# Create release package
.\build_package.ps1 -Package -Version "v1.0.0"

# Clean build artifacts
.\build_package.ps1 -Clean
```

### Manual Release Process

1. **Tag the release**:

   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Actions automatically**:
   - Validates module structure
   - Builds packages for all platforms
   - Generates changelog from commits
   - Creates GitHub release with assets

3. **Download and install** the module package for your platform
