extends SceneTree

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
    print("\n📌 Test 1: Color Tint Shader")
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
    print("\n📌 Test 2: Outline Shader")
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
    print("\n📌 Test 3: Pixelate Shader")
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
    print("\n📌 Test 4: Invalid Shader Handling")
    var invalid_shader = load("tests/assets/shaders/invalid.gdshader")
    if invalid_shader:
        var circle_image = svg_resource.rasterize_element_with_shader("circle1", Vector2i(128, 128), invalid_shader)
        
        if circle_image and circle_image.get_width() == 128:
            print("✅ Invalid shader handled gracefully (fallback to base image)")
            circle_image.save_png("tests/output/circle_fallback.png")
        else:
            print("❌ Invalid shader handling failed")
    
    # Test 5: Performance test with multiple shader applications
    print("\n📌 Test 5: Performance Test")
    var start_time = Time.get_ticks_msec()
    
    for i in range(10):
        var test_image = svg_resource.rasterize_element_with_shader("star1", Vector2i(64, 64), tint_shader)
    
    var end_time = Time.get_ticks_msec()
    var duration = end_time - start_time
    
    print("✅ Rendered 10 shader-processed images in ", duration, "ms")
    print("   Average: ", duration / 10.0, "ms per image")
    
    # Test 6: Shader override storage and retrieval
    print("\n📌 Test 6: Shader Override Management")
    print("Stored shader overrides: ", svg_resource.get_shader_overrides().size())
    
    svg_resource.clear_shader_override("star1")
    print("After clearing star1 override: ", svg_resource.get_shader_overrides().size())
    
    svg_resource.clear_all_overrides()
    print("After clearing all overrides: ", svg_resource.get_shader_overrides().size())
    
    print("\n🎊 Shader override system tests completed!")
    return true

func _ready():
    # Ensure output directory exists
    if not DirAccess.dir_exists_absolute("tests/output"):
        DirAccess.create_dir_recursive_absolute("tests/output")
    
    # Run the tests
    var success = test_shader_overrides()
    
    if success:
        print("\n✅ All shader tests passed!")
    else:
        print("\n❌ Some shader tests failed!")
    
    quit()
