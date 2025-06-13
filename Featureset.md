SVG Module for Godot 2D: Project Write-Up
Overview
Build a native Godot 2D module enabling high-fidelity, resolution-independent SVG rendering and sprite usage via <symbol> IDs, with full support for fill/stroke color and shader overrides.

Objectives
Full SVG Display: Render entire SVG files as Godot Texture2D.

Symbol-based Sprites: Render individual <symbol id="..."> elements as sprites.

Color Overrides: Apply per-element fill and stroke color overrides at runtime.

Shader Overrides: Attach custom shaders to individual SVG elements.

Architecture
Third-Party Parser
Lunasvg integrated under modules/svg_module/src/lunasvg as a static library, exposing a clean C++ API for parsing and DOM traversal.

Submodules & Core Classes
1. svg_resource Submodule
Location: modules/svg_module/src/svg_resource.cpp/.h

Class: SVGResource : Resource

Responsibilities:

Load and parse SVG files into an internal DOM-like representation.

Extract <symbol> entries into a Dictionary<String, SVGSymbol>.

Provide API for subtree retrieval, full element enumeration, and apply style overrides.

Key Methods:

bool load(const String &p_path)

SVGSymbol get_symbol(const String &id)

Vector<SVGElement> get_elements()

void override_fill(const String &element_id, Color fill_color)

void override_stroke(const String &element_id, Color stroke_color)

void override_shader(const String &element_id, Ref<Shader> shader)

2. svg_texture Submodule
Location: modules/svg_module/src/svg_texture.cpp/.h

Class: SVGTexture : Texture2D

Responsibilities:

Take an SVGResource and rasterize the entire SVG at target resolution.

Cache the resulting image and update on resource or resolution change.

Exports:

export(Resource) SVGResource resource

export(Vector2) target_size

3. svg_sprite Submodule
Location: modules/svg_module/src/svg_sprite.cpp/.h

Class: SVGSprite2D : Sprite2D

Responsibilities:

Render either the whole SVG or a single <symbol> by its ID.

Manage region rects for symbols and adjust draw size.

Forward style overrides to SVGResource and trigger re-rasterization via an internal SVGTexture or direct mesh draw.

Exports:

export(Resource) SVGResource resource

export(String) symbol_id

export(Vector2) draw_size

export(Color) fill_override

export(Color) stroke_override

export(Resource) shader_override

4. lunasvg_integration Submodule
Location: modules/svg_module/src/lunasvg_integration.cpp/.h

Responsibilities:

Compile and wrap Lunasvg into a static library.

Provide utility functions to convert between Lunasvg types and Godot types (e.g., path tessellation to PoolVector2Array).

5. register_types Submodule
Location: modules/svg_module/src/register_types.cpp

Responsibilities:

Register SVGResource, SVGTexture, and SVGSprite2D with Godot’s class database.

Define default property hints and tooltip strings.

6. plugin Submodule (Optional Editor Helpers)
Location: modules/svg_module/plugin/

Files:

svg_editor_plugin.gd — an EditorPlugin that injects docks and inspector controls.

svg_editor_panel.tscn — UI for previewing and selecting symbols.

svg_color_override_inspector.gd — custom inspector for fill/stroke pickers.

svg_shader_override_inspector.gd — inspector plugin for attaching shaders.

config.py — dock setup and menu registration.

Module Directory Structure
text
Copy
Edit
modules/svg_module/
├── src/
│   ├── lunasvg/                  # Third-party library source
│   ├── lunasvg_integration.cpp
│   ├── svg_resource.cpp
│   ├── svg_resource.h
│   ├── svg_texture.cpp
│   ├── svg_texture.h
│   ├── svg_sprite.cpp
│   ├── svg_sprite.h
│   └── register_types.cpp
└── plugin/                       # Optional editor tooling
    ├── icon.svg
    ├── script/
    │   ├── svg_editor_plugin.gd
    │   ├── svg_editor_panel.tscn
    │   ├── svg_color_override_inspector.gd
    │   └── svg_shader_override_inspector.gd
    └── config.py
Implementation Plan
Milestone 1: Parser Integration
Integrate Lunasvg via lunasvg_integration.

Implement SVGResource::load() and populate symbols.

Milestone 2: Full SVG Rasterization
Develop SVGTexture to rasterize and cache full SVG images.

Validate in a test scene.

Milestone 3: Symbol Rasterization
Extend SVGResource with get_symbol() support.

Implement SVGSprite2D logic for partial rasterization based on symbol_id.

Milestone 4: Color & Stroke Overrides
Wire up override methods in SVGResource.

Ensure both SVGTexture and SVGSprite2D respect overrides and re-render correctly.

Milestone 5: Shader Overrides & Mesh Path Rendering
Prototype direct mesh-based rendering of paths to apply custom ShaderMaterial.

Integrate into SVGSprite2D as an alternate draw path when shader_override is set.

Milestone 6: Editor Integration (Optional)
Create inspector plugins for symbol selection and style overrides.

Hook into Godot’s editor menus via svg_editor_plugin.

Additional Features (Bells & Whistles)
Signed-Distance-Field (SDF) Rendering

Import-time SDF atlas generation for ultra-sharp, scalable strokes and fills.

Custom shader to sample the SDF for crisp anti-aliasing at any zoom.

Auto-Tessellation Level-of-Detail

Runtime path simplification based on on-screen size.

Switch between simplified vector meshes and full-detail SDF as you zoom.

Offscreen Caching & Render-to-Texture

FBO caching of static SVGs or symbol instances to avoid repeated rasterization.

Vector Collision Shapes

Auto-generate CollisionShape2D from fills or stroke outlines, matching art perfectly.

Gradient & Filter Support

Parse and convert SVG <linearGradient>, <radialGradient>, and <filter> tags.

Bake into GradientTexture and ShaderMaterial passes (blur, drop shadow, color-matrix).

Boolean Path Operations

Expose union, difference, intersect ops via Lunasvg to combine or subtract shapes at runtime.

Live Vector Editing In-Engine

2D viewport tools for adjusting anchor points, handles, stroke widths, and colors directly in Godot.

Variable-Font & Rich Text Layout

Full <text> support with kerning, wrapping, and variable font axes.

Render as vectors or SDF for crisp scaling on UI.

Style-Overrides & Theming

CSS-style variables or Godot theme resources to swap palettes or tints globally.

Pattern & Tile Fills

Support for SVG <pattern> elements as repeatable vector fills or 9-slice panels.

Interactive Hit-Testing

Map SVG element IDs to Godot input events for per-element clicks and hovers.

Asset Bundling & Packing

Vector atlas generator to combine multiple symbols into one file, minimizing draw calls.

Procedural SVG Generators

GDScript/C++ helpers to spawn common shapes (polygons, stars, noise clouds) at runtime.

Export Hooks

“Bake Animation” tool to export rigged SVG bones and keyframes as Godot .anim tracks or glTF.

GDScript API Example
gdscript
Copy
Edit
var svg = SVGResource.new()
svg.load("res://icons.svg")
svg.override_fill("icon_alert", Color.red)
svg.override_shader("icon_alert", load("res://shaders/glow.shader"))

var sprite = SVGSprite2D.new()
sprite.resource = svg
sprite.symbol_id = "icon_alert"
sprite.draw_size = Vector2(64, 64)
add_child(sprite)
Acceptance Criteria
 Display full SVG with correct aspect ratio and resolution independence.

 Render individual symbols by ID, adjusting region rects correctly.

 Runtime fill and stroke color overrides apply immediately.

 Shader overrides on elements render via mesh + ShaderMaterial.

 All listed bells & whistles can be phased in as optional optional sub-features.

Next Steps
Assign Copilot tasks per submodule and feature:

Scaffold directories and file stubs.

Implement parser, resource loading, rasterization, sprite logic.

Layer in overrides, caching, LOD, collisions, filters, editing tools.

Review PRs with sample SVGs, SDF tests, LOD benchmarks, and Editor UX prototypes.

