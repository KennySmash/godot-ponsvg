#include "lunasvg_integration.h"
#include "core/io/file_access.h"
#include "core/error/error_macros.h"

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

void LunaSVGIntegration::apply_style_overrides(lunasvg::Element element, const Dictionary& style_overrides) {
    // TODO: Implement style override application
    // This would involve manipulating CSS properties of the element
    // For now, this is a placeholder
    print_line("Style overrides not yet implemented");
}

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