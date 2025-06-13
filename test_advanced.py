#!/usr/bin/env python3

"""
Enhanced test script to verify advanced SVG module functionality.
"""

# Enhanced GDScript test code (to be run in Godot)
gdscript_test = '''
extends Node

func _ready():
    print("Testing Enhanced SVG Module...")
    
    # Test loading complex SVG with symbols
    var svg_resource = SVGResource.new()
    var result = svg_resource.load_from_file("res://test_complex.svg")
    
    if result == OK:
        print("✓ Complex SVG loaded successfully")
        
        # Test symbol extraction
        var symbol_ids = svg_resource.get_symbol_ids()
        print("✓ Found symbols: ", symbol_ids)
        
        for symbol_id in symbol_ids:
            var symbol_data = svg_resource.get_symbol_data(symbol_id)
            print("  - Symbol '", symbol_id, "': ", symbol_data)
        
        # Test style overrides
        print("Testing style overrides...")
        
        # Override star to be red instead of gold
        svg_resource.override_fill("star_path", Color.RED)
        print("✓ Applied fill override to star")
        
        # Override circle to be green instead of blue
        svg_resource.override_fill("main_circle", Color.GREEN)
        svg_resource.override_stroke("main_circle", Color.DARK_GREEN)
        print("✓ Applied fill and stroke overrides to circle")
        
        # Override heart to be blue instead of red
        svg_resource.override_fill("heart_path", Color.BLUE)
        print("✓ Applied fill override to heart")
        
        # Test rasterization with overrides
        var full_image = svg_resource.rasterize_full(Vector2i(400, 400))
        if full_image != null:
            print("✓ Full SVG rasterized with overrides: ", full_image.get_size())
        
        # Test individual symbol rasterization
        var star_image = svg_resource.rasterize_symbol("icon_star", Vector2i(128, 128))
        if star_image != null:
            print("✓ Star symbol rasterized: ", star_image.get_size())
        
        var circle_image = svg_resource.rasterize_symbol("icon_circle", Vector2i(128, 128))
        if circle_image != null:
            print("✓ Circle symbol rasterized: ", circle_image.get_size())
        
        # Test SVGTexture with overrides
        var svg_texture = SVGTexture.new()
        svg_texture.svg_resource = svg_resource
        svg_texture.render_size = Vector2i(256, 256)
        print("✓ SVGTexture created with style overrides")
        
        # Test multiple sprites with different symbols
        var star_sprite = SVGSprite2D.new()
        star_sprite.svg_resource = svg_resource
        star_sprite.symbol_id = "icon_star"
        star_sprite.draw_size = Vector2(64, 64)
        star_sprite.position = Vector2(100, 100)
        add_child(star_sprite)
        
        var circle_sprite = SVGSprite2D.new()
        circle_sprite.svg_resource = svg_resource
        circle_sprite.symbol_id = "icon_circle"
        circle_sprite.draw_size = Vector2(64, 64)
        circle_sprite.position = Vector2(200, 100)
        add_child(circle_sprite)
        
        var heart_sprite = SVGSprite2D.new()
        heart_sprite.svg_resource = svg_resource
        heart_sprite.symbol_id = "icon_heart"
        heart_sprite.draw_size = Vector2(64, 64)
        heart_sprite.position = Vector2(300, 100)
        add_child(heart_sprite)
        
        print("✓ Created multiple sprite instances with different symbols")
        
        # Test runtime override changes
        await get_tree().create_timer(2.0).timeout
        print("Changing colors at runtime...")
        
        svg_resource.override_fill("star_path", Color.YELLOW)
        svg_resource.override_fill("main_circle", Color.MAGENTA)
        svg_resource.override_fill("heart_path", Color.CYAN)
        
        print("✓ Runtime color changes applied")
        
        # Test override clearing
        await get_tree().create_timer(2.0).timeout
        print("Clearing overrides...")
        
        svg_resource.clear_fill_override("star_path")
        svg_resource.clear_fill_override("main_circle")
        svg_resource.clear_all_overrides()
        
        print("✓ Style overrides cleared")
        
    else:
        print("✗ Failed to load complex SVG")

func test_basic_svg():
    """Test with a simple programmatically created SVG"""
    print("Testing basic SVG creation...")
    
    var simple_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <circle id="simple_circle" cx="50" cy="50" r="40" fill="red" stroke="blue" stroke-width="3"/>
  <rect id="simple_rect" x="10" y="10" width="30" height="20" fill="green"/>
</svg>"""
    
    var svg_resource = SVGResource.new()
    var result = svg_resource.load_from_string(simple_svg)
    
    if result == OK:
        print("✓ Simple SVG loaded")
        
        # Test override
        svg_resource.override_fill("simple_circle", Color.ORANGE)
        svg_resource.override_stroke("simple_circle", Color.PURPLE)
        
        var image = svg_resource.rasterize_full(Vector2i(200, 200))
        if image != null:
            print("✓ Simple SVG rasterized with overrides")
        
        return svg_resource
    
    return null
'''

print("Enhanced SVG Module Test Script")
print("==============================")
print()
print("This script tests:")
print("- Complex SVG loading with multiple symbols")
print("- Symbol extraction and identification") 
print("- Style overrides (fill and stroke colors)")
print("- Individual symbol rasterization")
print("- Runtime style changes")
print("- Override clearing")
print()
print("To test the module:")
print("1. Compile Godot with the SVG module")
print("2. Copy test_complex.svg to your project")
print("3. Run this GDScript code in a scene")
print()
print("GDScript test code:")
print("===================")
print(gdscript_test)
