#ifndef LUNAPONSVG_INTEGRATION_H
#define LUNAPONSVG_INTEGRATION_H

#include "core/object/ref_counted.h"
#include "core/templates/vector.h"
#include "core/math/vector2.h"
#include "core/math/color.h"
#include "core/io/resource.h"
#include "scene/resources/texture.h"
#include "scene/resources/image.h"

// Include LunaSVG headers
#include "lunasvg.h"

class LunaSVGIntegration : public RefCounted {
    GDCLASS(LunaSVGIntegration, RefCounted);

protected:
    static void _bind_methods();

public:
    // Static utility functions for SVG operations
    static std::unique_ptr<lunasvg::Document> load_svg_from_string(const String& svg_data);
    static std::unique_ptr<lunasvg::Document> load_svg_from_file(const String& file_path);
    
    // Rasterization functions
    static Ref<Image> rasterize_document(lunasvg::Document* document, const Vector2i& target_size, uint32_t background_color = 0x00000000);
    static Ref<Image> rasterize_element(lunasvg::Element element, const Vector2i& target_size, uint32_t background_color = 0x00000000);
    
    // Element manipulation and attribute access
    static lunasvg::Element find_element_by_id(lunasvg::Document* document, const String& id);
    static Vector<lunasvg::Element> query_elements(lunasvg::Document* document, const String& selector);
    static String get_element_attribute(const lunasvg::Element& element, const String& attribute_name);
    static void set_element_attribute(lunasvg::Element& element, const String& attribute_name, const String& value);
    static bool has_element_attribute(const lunasvg::Element& element, const String& attribute_name);
    
    // Style manipulation
    static void apply_fill_color(lunasvg::Element& element, const Color& color);
    static void apply_stroke_color(lunasvg::Element& element, const Color& color);
    static void apply_style_overrides(lunasvg::Element element, const Dictionary& style_overrides);
    
    // Conversion utilities
    static lunasvg::Bitmap to_lunasvg_bitmap(const lunasvg::Bitmap& bitmap);
    static Ref<Image> lunasvg_bitmap_to_godot_image(const lunasvg::Bitmap& bitmap);

    LunaSVGIntegration();
    ~LunaSVGIntegration();
};

#endif // LUNAPONSVG_INTEGRATION_H