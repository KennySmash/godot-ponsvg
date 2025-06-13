# SVG Module for Godot 4

A high-performance, native Godot module that enables full SVG rendering capabilities with resolution-independent graphics, symbol-based sprites, and dynamic style overrides.

## 🎯 Project Goals

This module brings professional-grade SVG support to Godot 4, enabling:

- **High-Fidelity SVG Rendering**: Display complete SVG files as Godot `Texture2D` resources with perfect vector quality
- **Symbol-Based Sprites**: Extract and render individual `<symbol>` elements as standalone sprites for efficient icon systems
- **Dynamic Style Overrides**: Modify fill colors, stroke properties, and apply custom shaders at runtime without touching source files
- **Resolution Independence**: True vector graphics that scale perfectly at any resolution without quality loss
- **Performance Optimization**: Intelligent caching, LOD systems, and GPU-accelerated rendering paths

## 🏗️ Architecture Overview

The module is built around several core components:

### Core Classes

- **`SVGResource`**: Parses and manages SVG files, handles DOM traversal and style overrides
- **`SVGTexture`**: Rasterizes complete SVG documents as `Texture2D` resources
- **`SVGSprite2D`**: Renders individual symbols or full SVGs as 2D sprites with style controls
- **LunaSVG Integration**: High-performance C++ SVG parser and renderer

### Module Structure

```text
modules/svg_module/
├── src/
│   ├── lunasvg/                  # Third-party SVG parsing library
│   ├── lunasvg_integration.*     # C++ wrapper for LunaSVG
│   ├── svg_resource.*            # Core SVG data management
│   ├── svg_texture.*             # Full SVG rasterization
│   ├── svg_sprite.*              # Symbol-based sprite rendering
│   └── register_types.cpp        # Godot class registration
├── plugin/                       # Editor integration (optional)
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
# Change colors at runtime without modifying source files
svg_resource.override_fill("icon_alert", Color.RED)
svg_resource.override_stroke("icon_border", Color.BLUE)

# Apply custom shaders to specific elements
var glow_shader = load("res://shaders/glow_effect.gdshader")
svg_resource.override_shader("icon_highlight", glow_shader)

# Clear overrides
svg_resource.clear_fill_override("icon_alert")
svg_resource.clear_all_overrides()
```

### Responsive UI Icons

```gdscript
# Icons that scale perfectly for different screen densities
func update_ui_scale(scale_factor: float):
    for sprite in get_tree().get_nodes_in_group("ui_icons"):
        if sprite is SVGSprite2D:
            sprite.draw_size = sprite.draw_size * scale_factor
```

## 🛠️ Installation

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

- [x] Basic module structure and build system
- [x] LunaSVG library integration (v3.3.0)
- [x] Core class definitions and registration
- [x] SVGResource API for loading and style overrides
- [x] SVGTexture and SVGSprite2D class frameworks
- [x] Working SVG parsing and rasterization pipeline
- [x] LunaSVG integration wrapper with proper API mapping
- [x] Image format conversion (ARGB→RGBA)
- [x] Basic symbol extraction framework

### 🚧 In Progress

- [ ] Advanced symbol extraction with proper ID mapping
- [ ] Runtime color and shader override implementation
- [ ] Performance optimizations and intelligent caching
- [ ] Editor plugin for symbol preview and selection

### 📅 Planned Features

- [ ] Advanced style manipulation (CSS property overrides)
- [ ] Performance optimizations and caching
- [ ] Editor plugin for symbol preview and selection
- [ ] Advanced features (SDF rendering, collision shapes, filters)

## 🧪 Testing

A comprehensive test suite is included:

```bash
# Run build verification
python build_test.py

# Test with sample SVG
# (See test_svg.svg for a sample file with symbols)
```

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

**Status**: Early Development | **Godot Version**: 4.x | **Platform Support**: Windows, Linux, macOS
