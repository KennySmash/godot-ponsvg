#include "lunasvg_integration.h"
#include <godot_cpp/classes/file_access.hpp>
#include <godot_cpp/variant/utility_functions.hpp>

using namespace godot;

void LunaSVGIntegration::_bind_methods() {
    // Bind methods to Godot if needed for editor tools
}

std::unique_ptr<lunasvg::Document> LunaSVGIntegration::load_svg_from_string(const String& svg_data) {
    std::string std_string = svg_data.utf8().get_data();
    return lunasvg::Document::loadFromData(std_string);
}

std::unique_ptr<lunasvg::Document> LunaSVGIntegration::load_svg_from_file(const String& file_path) {
    Ref<FileAccess> file = FileAccess::open(file_path, FileAccess::READ);
    if (file.is_null()) {
        ERR_PRINT("Cannot open SVG file: " + file_path);
        return nullptr;
    }
    
    String content = file->get_as_text();
    file->close();
    
    return load_svg_from_string(content);
}

Ref<Image> LunaSVGIntegration::rasterize_document(lunasvg::Document* document, const Vector2i& target_size, uint32_t background_color) {
    if (!document) {
        ERR_PRINT("Document is null");
        return Ref<Image>();
    }
    
    // Use LunaSVG to render to bitmap
    lunasvg::Bitmap bitmap = document->renderToBitmap(target_size.x, target_size.y, background_color);
    
    return lunasvg_bitmap_to_godot_image(bitmap);
}

Ref<Image> LunaSVGIntegration::rasterize_element(lunasvg::Element element, const Vector2i& target_size, uint32_t background_color) {
    if (element.isNull()) {
        ERR_PRINT("Element is null");
        return Ref<Image>();
    }
    
    // Use LunaSVG to render element to bitmap
    lunasvg::Bitmap bitmap = element.renderToBitmap(target_size.x, target_size.y, background_color);
    
    return lunasvg_bitmap_to_godot_image(bitmap);
}

lunasvg::Element LunaSVGIntegration::find_element_by_id(lunasvg::Document* document, const String& id) {
    if (!document) {
        return lunasvg::Element();
    }
    
    std::string std_id = id.utf8().get_data();
    return document->getElementById(std_id);
}

Vector<lunasvg::Element> LunaSVGIntegration::query_elements(lunasvg::Document* document, const String& selector) {
    Vector<lunasvg::Element> result;
    
    if (!document) {
        return result;
    }
    
    std::string std_selector = selector.utf8().get_data();
    lunasvg::ElementList elements = document->querySelectorAll(std_selector);
    
    for (const auto& element : elements) {
        result.push_back(element);
    }
    
    return result;
}

String LunaSVGIntegration::get_element_attribute(const lunasvg::Element& element, const String& attribute_name) {
    if (element.isNull()) {
        return String();
    }
    
    std::string attr_name = attribute_name.utf8().get_data();
    const std::string& attr_value = element.getAttribute(attr_name);
    return String(attr_value.c_str());
}

void LunaSVGIntegration::set_element_attribute(lunasvg::Element& element, const String& attribute_name, const String& value) {
    if (element.isNull()) {
        return;
    }
    
    std::string attr_name = attribute_name.utf8().get_data();
    std::string attr_value = value.utf8().get_data();
    element.setAttribute(attr_name, attr_value);
}

bool LunaSVGIntegration::has_element_attribute(const lunasvg::Element& element, const String& attribute_name) {
    if (element.isNull()) {
        return false;
    }
    
    std::string attr_name = attribute_name.utf8().get_data();
    return element.hasAttribute(attr_name);
}

void LunaSVGIntegration::apply_fill_color(lunasvg::Element& element, const Color& color) {
    if (element.isNull()) {
        return;
    }
    
    // Convert Godot Color to CSS color string with alpha support
    String color_str;
    if (color.a < 1.0f) {
        color_str = String("rgba(") + 
                   String::num_int64((int)(color.r * 255)) + "," +
                   String::num_int64((int)(color.g * 255)) + "," +
                   String::num_int64((int)(color.b * 255)) + "," +
                   String::num(color.a) + ")";
    } else {
        color_str = String("rgb(") + 
                   String::num_int64((int)(color.r * 255)) + "," +
                   String::num_int64((int)(color.g * 255)) + "," +
                   String::num_int64((int)(color.b * 255)) + ")";
    }
    
    set_element_attribute(element, "fill", color_str);
}

void LunaSVGIntegration::apply_stroke_color(lunasvg::Element& element, const Color& color) {
    if (element.isNull()) {
        return;
    }
    
    // Convert Godot Color to CSS color string with alpha support
    String color_str;
    if (color.a < 1.0f) {
        color_str = String("rgba(") + 
                   String::num_int64((int)(color.r * 255)) + "," +
                   String::num_int64((int)(color.g * 255)) + "," +
                   String::num_int64((int)(color.b * 255)) + "," +
                   String::num(color.a) + ")";
    } else {
        color_str = String("rgb(") + 
                   String::num_int64((int)(color.r * 255)) + "," +
                   String::num_int64((int)(color.g * 255)) + "," +
                   String::num_int64((int)(color.b * 255)) + ")";
    }
    
    set_element_attribute(element, "stroke", color_str);
}

void LunaSVGIntegration::apply_style_overrides(lunasvg::Element element, const Dictionary& style_overrides) {
    if (element.isNull()) {
        return;
    }
    
    // Apply style overrides from the dictionary
    Array keys = style_overrides.keys();
    for (int i = 0; i < keys.size(); i++) {
        String property = keys[i];
        Variant value = style_overrides[property];
        
        if (property == "fill" && value.get_type() == Variant::VECTOR3) {
            Vector3 color_vec = value;
            Color color(color_vec.x, color_vec.y, color_vec.z, 1.0f);
            apply_fill_color(element, color);
        } else if (property == "stroke" && value.get_type() == Variant::VECTOR3) {
            Vector3 color_vec = value;
            Color color(color_vec.x, color_vec.y, color_vec.z, 1.0f);
            apply_stroke_color(element, color);
        } else if (value.get_type() == Variant::STRING) {
            // Generic string attribute setting
            set_element_attribute(element, property, value);
        }
    }
}

void LunaSVGIntegration::apply_css_style(lunasvg::Element& element, const String& css_property, const String& css_value) {
    if (element.isNull()) {
        return;
    }
    
    // Apply CSS-style properties directly
    set_element_attribute(element, css_property, css_value);
}

void LunaSVGIntegration::apply_multiple_overrides(lunasvg::Element& element, const Dictionary& fill_overrides, const Dictionary& stroke_overrides) {
    if (element.isNull()) {
        return;
    }
    
    String element_id = get_element_attribute(element, "id");
    String element_class = get_element_attribute(element, "class");
    
    // Apply ID-based fill override
    if (!element_id.is_empty() && fill_overrides.has(element_id)) {
        Color color = fill_overrides[element_id];
        apply_fill_color(element, color);
    }
    
    // Apply class-based fill override  
    if (!element_class.is_empty()) {
        String class_key = "." + element_class;
        if (fill_overrides.has(class_key)) {
            Color color = fill_overrides[class_key];
            apply_fill_color(element, color);
        }
    }
    
    // Apply ID-based stroke override
    if (!element_id.is_empty() && stroke_overrides.has(element_id)) {
        Color color = stroke_overrides[element_id];
        apply_stroke_color(element, color);
    }
    
    // Apply class-based stroke override
    if (!element_class.is_empty()) {
        String class_key = "." + element_class;
        if (stroke_overrides.has(class_key)) {
            Color color = stroke_overrides[class_key];
            apply_stroke_color(element, color);
        }
    }
}

// Enhanced style overrides function with more flexibility

lunasvg::Bitmap LunaSVGIntegration::to_lunasvg_bitmap(const lunasvg::Bitmap& bitmap) {
    // Direct return since it's the same type
    return bitmap;
}

Ref<Image> LunaSVGIntegration::lunasvg_bitmap_to_godot_image(const lunasvg::Bitmap& bitmap) {
    if (bitmap.isNull()) {
        ERR_PRINT("LunaSVG bitmap is null");
        return Ref<Image>();
    }
    
    int width = bitmap.width();
    int height = bitmap.height();
    uint8_t* data = bitmap.data();
    
    if (!data) {
        ERR_PRINT("LunaSVG bitmap data is null");
        return Ref<Image>();
    }
    
    // LunaSVG uses ARGB32 Premultiplied format
    // We need to convert to Godot's expected RGBA8 format
    PackedByteArray godot_data;
    godot_data.resize(width * height * 4);
    
    for (int i = 0; i < width * height; i++) {
        int src_offset = i * 4;
        int dst_offset = i * 4;
        
        // LunaSVG format: ARGB (byte order depends on endianness)
        // Godot format: RGBA
        uint8_t a = data[src_offset + 3];
        uint8_t r = data[src_offset + 2]; 
        uint8_t g = data[src_offset + 1];
        uint8_t b = data[src_offset + 0];
        
        // Convert from premultiplied alpha if needed
        if (a > 0 && a < 255) {
            r = (r * 255) / a;
            g = (g * 255) / a;
            b = (b * 255) / a;
        }
        
        godot_data[dst_offset + 0] = r;
        godot_data[dst_offset + 1] = g;
        godot_data[dst_offset + 2] = b;
        godot_data[dst_offset + 3] = a;
    }
    
    Ref<Image> image = Image::create_from_data(width, height, false, Image::FORMAT_RGBA8, godot_data);
    return image;
}

LunaSVGIntegration::LunaSVGIntegration() {
    // Constructor
}

LunaSVGIntegration::~LunaSVGIntegration() {
    // Destructor
}