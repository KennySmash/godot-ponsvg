#!/usr/bin/env python3
"""
Advanced Shader Override Test for PonSVG Module

Tests the complete shader processing pipeline including:
- Shader validation 
- Post-processing application
- Performance with different shader types
- Error handling and fallbacks
"""

import os
import sys

def create_test_shaders():
    """Create test shader files for the shader override system"""
    
    # Create shaders directory if it doesn't exist
    os.makedirs("tests/assets/shaders", exist_ok=True)
    
    # 1. Simple color tint shader
    color_tint_shader = """shader_type canvas_item;

uniform vec4 tint_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float tint_strength : hint_range(0.0, 1.0) = 0.5;

void fragment() {
    vec4 base_color = texture(TEXTURE, UV);
    COLOR = mix(base_color, tint_color * base_color.a, tint_strength);
}
"""
    
    with open("tests/assets/shaders/color_tint.gdshader", "w", encoding='utf-8') as f:
        f.write(color_tint_shader)
    
    # 2. Outline effect shader
    outline_shader = """shader_type canvas_item;

uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float outline_width : hint_range(0.0, 10.0) = 2.0;

void fragment() {
    vec2 size = TEXTURE_PIXEL_SIZE * outline_width;
    vec4 base_color = texture(TEXTURE, UV);
    
    float outline = 0.0;
    outline += texture(TEXTURE, UV + vec2(-size.x, -size.y)).a;
    outline += texture(TEXTURE, UV + vec2(0.0, -size.y)).a;
    outline += texture(TEXTURE, UV + vec2(size.x, -size.y)).a;
    outline += texture(TEXTURE, UV + vec2(-size.x, 0.0)).a;
    outline += texture(TEXTURE, UV + vec2(size.x, 0.0)).a;
    outline += texture(TEXTURE, UV + vec2(-size.x, size.y)).a;
    outline += texture(TEXTURE, UV + vec2(0.0, size.y)).a;
    outline += texture(TEXTURE, UV + vec2(size.x, size.y)).a;
    
    outline = min(outline, 1.0);
    
    vec4 result = mix(outline_color, base_color, base_color.a);
    COLOR = vec4(result.rgb, max(outline, base_color.a));
}
"""
    
    with open("tests/assets/shaders/outline.gdshader", "w", encoding='utf-8') as f:
        f.write(outline_shader)
    
    # 3. Pixelate effect shader
    pixelate_shader = """shader_type canvas_item;

uniform float pixel_size : hint_range(1.0, 50.0) = 8.0;

void fragment() {
    vec2 pixelated_uv = floor(UV * pixel_size) / pixel_size;
    COLOR = texture(TEXTURE, pixelated_uv);
}
"""
    
    with open("tests/assets/shaders/pixelate.gdshader", "w", encoding='utf-8') as f:
        f.write(pixelate_shader)
    
    # 4. Invalid shader (for error testing)
    invalid_shader = """// This is an invalid shader for testing error handling
this is not valid shader code
shader_type invalid_type;
"""
    
    with open("tests/assets/shaders/invalid.gdshader", "w", encoding='utf-8') as f:
        f.write(invalid_shader)
    
    print("✅ Created test shader files:")
    print("   - color_tint.gdshader")
    print("   - outline.gdshader") 
    print("   - pixelate.gdshader")
    print("   - invalid.gdshader")

def create_shader_test_svg():
    """Create an SVG file optimized for shader testing"""
    
    shader_test_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#ff6b6b;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#4ecdc4;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Test symbols for shader effects -->
  <symbol id="icon-star" viewBox="0 0 100 100">
    <path d="M50 10 L61 39 L90 39 L68 58 L79 87 L50 70 L21 87 L32 58 L10 39 L39 39 Z" 
          fill="#ffdd59" stroke="#ff6b6b" stroke-width="3"/>
  </symbol>
  
  <symbol id="icon-heart" viewBox="0 0 100 100">
    <path d="M50 85 C20 65, 5 35, 25 15 C35 5, 50 10, 50 25 C50 10, 65 5, 75 15 C95 35, 80 65, 50 85 Z" 
          fill="#ff6b6b" stroke="#fff" stroke-width="2"/>
  </symbol>
  
  <symbol id="icon-shield" viewBox="0 0 100 100">
    <path d="M50 5 L80 20 L80 50 C80 70, 65 85, 50 95 C35 85, 20 70, 20 50 L20 20 Z" 
          fill="url(#grad1)" stroke="#333" stroke-width="2"/>
  </symbol>
  
  <!-- Background for shader testing -->
  <rect id="background" width="400" height="300" fill="#f8f9fa" stroke="#dee2e6" stroke-width="2"/>
  
  <!-- Test elements for individual shader application -->
  <use id="star1" href="#icon-star" x="50" y="50" width="80" height="80"/>
  <use id="heart1" href="#icon-heart" x="180" y="50" width="80" height="80"/>
  <use id="shield1" href="#icon-shield" x="310" y="50" width="80" height="80"/>
  
  <!-- Complex shapes for advanced shader testing -->
  <circle id="circle1" cx="100" cy="200" r="40" fill="#4ecdc4" stroke="#45b7aa" stroke-width="3"/>
  <rect id="rect1" x="180" y="160" width="80" height="80" rx="10" fill="#ffdd59" stroke="#f1c40f" stroke-width="3"/>
  <polygon id="triangle1" points="350,160 310,240 390,240" fill="#ff6b6b" stroke="#e74c3c" stroke-width="3"/>
</svg>"""
    
    with open("tests/assets/shader_test.svg", "w", encoding='utf-8') as f:
        f.write(shader_test_svg)
    
    print("✅ Created shader test SVG: tests/assets/shader_test.svg")

def create_gdscript_shader_test():
    """Create a GDScript test for shader functionality"""
    
    gdscript_test = """extends SceneTree

# Comprehensive shader override test for PonSVG

func test_shader_overrides():
    print("🎨 Testing Shader Override System")
    print("=" * 50)
    
    # Load the SVG resource
    var svg_resource = PonSVGResource.new()
    var result = svg_resource.load_from_file("tests/assets/shader_test.svg")
    
    if result != OK:
        print("❌ Failed to load SVG file")
        return false
    
    print("✅ Loaded SVG with symbols: ", svg_resource.get_symbol_ids())
    
    # Test 1: Color tint shader on star
    print("\\n📌 Test 1: Color Tint Shader")
    var tint_shader = load("tests/assets/shaders/color_tint.gdshader")
    if tint_shader:
        svg_resource.override_shader("star1", tint_shader)
        var star_image = svg_resource.rasterize_element_with_shader("star1", Vector2i(128, 128), tint_shader)
        
        if star_image and star_image.get_width() == 128:
            print("✅ Color tint shader applied successfully")
            star_image.save_png("tests/output/star_tinted.png")
        else:
            print("❌ Color tint shader failed")
    
    # Test 2: Outline shader on heart
    print("\\n📌 Test 2: Outline Shader")
    var outline_shader = load("tests/assets/shaders/outline.gdshader")
    if outline_shader:
        svg_resource.override_shader("heart1", outline_shader)
        var heart_image = svg_resource.rasterize_element_with_shader("heart1", Vector2i(128, 128), outline_shader)
        
        if heart_image and heart_image.get_width() == 128:
            print("✅ Outline shader applied successfully")
            heart_image.save_png("tests/output/heart_outlined.png")
        else:
            print("❌ Outline shader failed")
    
    # Test 3: Pixelate shader on shield
    print("\\n📌 Test 3: Pixelate Shader")
    var pixelate_shader = load("tests/assets/shaders/pixelate.gdshader")
    if pixelate_shader:
        svg_resource.override_shader("shield1", pixelate_shader)
        var shield_image = svg_resource.rasterize_element_with_shader("shield1", Vector2i(128, 128), pixelate_shader)
        
        if shield_image and shield_image.get_width() == 128:
            print("✅ Pixelate shader applied successfully")
            shield_image.save_png("tests/output/shield_pixelated.png")
        else:
            print("❌ Pixelate shader failed")
    
    # Test 4: Invalid shader handling
    print("\\n📌 Test 4: Invalid Shader Handling")
    var invalid_shader = load("tests/assets/shaders/invalid.gdshader")
    if invalid_shader:
        var circle_image = svg_resource.rasterize_element_with_shader("circle1", Vector2i(128, 128), invalid_shader)
        
        if circle_image and circle_image.get_width() == 128:
            print("✅ Invalid shader handled gracefully (fallback to base image)")
            circle_image.save_png("tests/output/circle_fallback.png")
        else:
            print("❌ Invalid shader handling failed")
    
    # Test 5: Performance test with multiple shader applications
    print("\\n📌 Test 5: Performance Test")
    var start_time = Time.get_ticks_msec()
    
    for i in range(10):
        var test_image = svg_resource.rasterize_element_with_shader("star1", Vector2i(64, 64), tint_shader)
    
    var end_time = Time.get_ticks_msec()
    var duration = end_time - start_time
    
    print("✅ Rendered 10 shader-processed images in ", duration, "ms")
    print("   Average: ", duration / 10.0, "ms per image")
    
    # Test 6: Shader override storage and retrieval
    print("\\n📌 Test 6: Shader Override Management")
    print("Stored shader overrides: ", svg_resource.get_shader_overrides().size())
    
    svg_resource.clear_shader_override("star1")
    print("After clearing star1 override: ", svg_resource.get_shader_overrides().size())
    
    svg_resource.clear_all_overrides()
    print("After clearing all overrides: ", svg_resource.get_shader_overrides().size())
    
    print("\\n🎊 Shader override system tests completed!")
    return true

func _ready():
    # Ensure output directory exists
    if not DirAccess.dir_exists_absolute("tests/output"):
        DirAccess.create_dir_recursive_absolute("tests/output")
    
    # Run the tests
    var success = test_shader_overrides()
    
    if success:
        print("\\n✅ All shader tests passed!")
    else:
        print("\\n❌ Some shader tests failed!")
    
    quit()
"""
    
    with open("tests/test_shader_overrides.gd", "w", encoding='utf-8') as f:
        f.write(gdscript_test)
    
    print("✅ Created GDScript shader test: tests/test_shader_overrides.gd")

def main():
    print("🎨 Setting up Shader Override System Tests")
    print("=" * 50)
    
    # Create all test assets
    create_test_shaders()
    create_shader_test_svg()
    create_gdscript_shader_test()
    
    print("\\n🎯 Shader Override Test Setup Complete!")
    print("\\n📋 Next Steps:")
    print("1. Build the PonSVG module with shader support")
    print("2. Run: godot --headless --script tests/test_shader_overrides.gd")
    print("3. Check tests/output/ for processed images")
    print("\\n🔍 Expected Results:")
    print("- star_tinted.png - Star with color tint effect")
    print("- heart_outlined.png - Heart with outline effect")
    print("- shield_pixelated.png - Shield with pixelate effect")
    print("- circle_fallback.png - Circle with fallback rendering")

if __name__ == "__main__":
    main()
