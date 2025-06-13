# SVG Module for Godot 4

A high-performance, native Godot module that enables full SVG rendering capabilities with resolution-independent graphics, symbol-based sprites, dynamic style overrides, and advanced performance optimization.

## 🎯 Project Goals

This module brings professional-grade SVG support to Godot 4, enabling:

- **High-Fidelity SVG Rendering**: Display complete SVG files as Godot `Texture2D` resources with perfect vector quality
- **Symbol-Based Sprites**: Extract and render individual `<symbol>` elements as standalone sprites for efficient icon systems
- **Dynamic Style Overrides**: Modify fill colors, stroke properties, and apply custom shaders at runtime without touching source files
- **Resolution Independence**: True vector graphics that scale perfectly at any resolution without quality loss
- **Performance Optimization**: Intelligent caching, LOD systems, and optimized rendering paths for production use

## 🏗️ Architecture Overview

The module is built around several core components:

### Core Classes

- **`SVGResource`**: Parses and manages SVG files, handles DOM traversal, style overrides, and performance optimization
- **`SVGTexture`**: Rasterizes complete SVG documents as `Texture2D` resources with caching
- **`SVGSprite2D`**: Renders individual symbols or full SVGs as 2D sprites with style controls
- **LunaSVG Integration**: High-performance C++ SVG parser and renderer (v3.3.0)

### Performance Features

- **Intelligent Caching**: Automatic cache management with style-aware invalidation
- **LOD System**: Level-of-detail rendering with configurable quality/performance trade-offs  
- **Memory Optimization**: Efficient texture reuse and cache size management
- **CPU Optimization**: O(1) cache lookups and minimal re-rendering

### Module Structure

```text
modules/svg_module/
├── src/
│   ├── lunasvg/                  # LunaSVG v3.3.0 library
│   ├── lunasvg_integration.*     # C++ wrapper for LunaSVG
│   ├── svg_resource.*            # Core SVG data management + caching
│   ├── svg_texture.*             # Full SVG rasterization
│   ├── svg_sprite.*              # Symbol-based sprite rendering
│   └── register_types.cpp        # Godot class registration
├── plugin/                       # Editor integration (future)
└── config.py                     # Build configuration
```

## 🚀 Usage Examples

### Basic SVG Loading and Display

```gdscript
# Load an SVG file as a resource
var svg_resource = SVGResource.new()
svg_resource.load_from_file("res://icons/ui_icons.svg")

# Display the full SVG as a texture
var svg_texture = SVGTexture.new()
svg_texture.svg_resource = svg_resource
svg_texture.render_size = Vector2i(512, 512)

# Use in a TextureRect or Sprite2D
$TextureRect.texture = svg_texture
```

### Symbol-Based Sprite System

```gdscript
# Load SVG with multiple symbol definitions
var icon_set = SVGResource.new()
icon_set.load_from_file("res://ui/icon_library.svg")

# Create sprites for individual symbols
var play_button = SVGSprite2D.new()
play_button.svg_resource = icon_set
play_button.symbol_id = "play_icon"
play_button.draw_size = Vector2(64, 64)
add_child(play_button)

var pause_button = SVGSprite2D.new()
pause_button.svg_resource = icon_set
pause_button.symbol_id = "pause_icon"
pause_button.draw_size = Vector2(64, 64)
add_child(pause_button)
```

### Dynamic Style Overrides

```gdscript
# Load SVG with elements that have IDs
var svg_resource = SVGResource.new()
svg_resource.load_from_file("res://ui/icons.svg")

# Change colors at runtime by element ID
svg_resource.override_fill("star_path", Color.RED)
svg_resource.override_stroke("circle_border", Color.BLUE)

# Changes are applied immediately and persist
var modified_texture = SVGTexture.new()
modified_texture.svg_resource = svg_resource
modified_texture.render_size = Vector2i(256, 256)

# Clear specific overrides
svg_resource.clear_fill_override("star_path")
svg_resource.clear_all_overrides()
```

### Advanced Symbol Management

```gdscript
# Extract all symbol IDs from an SVG
var symbol_ids = svg_resource.get_symbol_ids()
print("Available symbols: ", symbol_ids)

# Get detailed symbol information
for symbol_id in symbol_ids:
    var symbol_data = svg_resource.get_symbol_data(symbol_id)
    print("Symbol ", symbol_id, " bounds: ", symbol_data.get("bounds", Rect2()))

# Render individual symbols at different sizes
var large_icon = svg_resource.rasterize_symbol("icon_star", Vector2i(128, 128))
var small_icon = svg_resource.rasterize_symbol("icon_star", Vector2i(32, 32))
```

### Responsive UI Icons

```gdscript
# Icons that scale perfectly for different screen densities
func update_ui_scale(scale_factor: float):
    for sprite in get_tree().get_nodes_in_group("ui_icons"):
        if sprite is SVGSprite2D:
            sprite.draw_size = sprite.draw_size * scale_factor
```

## � API Reference

### SVGResource

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

### SVGTexture

Texture2D implementation for displaying SVG content.

#### Properties

- `SVGResource svg_resource` - The source SVG resource
- `Vector2i render_size` - Target rendering resolution

#### Methods

- `void force_update()` - Force texture regeneration
- Standard Texture2D interface (get_width, get_height, etc.)

### SVGSprite2D

Node2D for displaying SVG content or individual symbols.

#### Properties

- `SVGResource svg_resource` - The source SVG resource
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
   git clone https://github.com/your-repo/gotot-svg-module.git svg_module
   ```

2. **Initialize the LunaSVG submodule:**
   ```bash
   cd svg_module/modules/svg_module/src/
   git clone https://github.com/sammycage/lunasvg.git
   ```

3. **Build Godot with the module:**
   ```bash
   cd path/to/godot/
   scons platform=windows target=editor module_svg_enabled=yes
   # or for other platforms:
   # scons platform=linux target=editor module_svg_enabled=yes
   # scons platform=macos target=editor module_svg_enabled=yes
   ```

### Verification

After building, the following classes should be available in Godot:
- `SVGResource`
- `SVGTexture` 
- `SVGSprite2D`

You can test the installation with:
```gdscript
var svg = SVGResource.new()
print("SVG Module loaded successfully!")
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
svg_resource.override_fill("main_circle", Color.RED)
svg_resource.override_stroke("star_path", Color.BLACK)
```

### Building from Source

1. Clone this repository into your Godot source `modules/` directory:

```bash
cd path/to/godot/modules/
git clone https://github.com/your-repo/gotot-svg-module.git svg_module
```

2. Initialize the LunaSVG submodule:

```bash
cd svg_module
git submodule update --init --recursive
```

3. Build Godot with the module:

```bash
cd ../../  # Back to Godot root
scons platform=windows target=editor module_svg_enabled=yes
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
  "module_name": "svg_module",
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
