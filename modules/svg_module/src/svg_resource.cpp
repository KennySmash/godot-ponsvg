#include "svg_resource.h"
#include "core/io/file_access.h"
#include "core/error/error_macros.h"
#include "lunasvg.h"

SVGResource::SVGResource() {
    // Initialize empty
}

SVGResource::~SVGResource() {
    // Cleanup if needed
}

void SVGResource::_bind_methods() {
    // Core loading
    ClassDB::bind_method(D_METHOD("load_from_file", "path"), &SVGResource::load_from_file);
    ClassDB::bind_method(D_METHOD("load_from_string", "svg_string"), &SVGResource::load_from_string);
    
    // Symbol management
    ClassDB::bind_method(D_METHOD("get_symbol_ids"), &SVGResource::get_symbol_ids);
    ClassDB::bind_method(D_METHOD("has_symbol", "id"), &SVGResource::has_symbol);
    ClassDB::bind_method(D_METHOD("get_symbol_data", "id"), &SVGResource::get_symbol_data);
    
    // Style overrides
    ClassDB::bind_method(D_METHOD("override_fill", "element_id", "color"), &SVGResource::override_fill);
    ClassDB::bind_method(D_METHOD("override_stroke", "element_id", "color"), &SVGResource::override_stroke);
    ClassDB::bind_method(D_METHOD("override_shader", "element_id", "shader"), &SVGResource::override_shader);
    
    ClassDB::bind_method(D_METHOD("clear_fill_override", "element_id"), &SVGResource::clear_fill_override);
    ClassDB::bind_method(D_METHOD("clear_stroke_override", "element_id"), &SVGResource::clear_stroke_override);
    ClassDB::bind_method(D_METHOD("clear_shader_override", "element_id"), &SVGResource::clear_shader_override);
    ClassDB::bind_method(D_METHOD("clear_all_overrides"), &SVGResource::clear_all_overrides);
    
    // Getters
    ClassDB::bind_method(D_METHOD("get_svg_data"), &SVGResource::get_svg_data);
    ClassDB::bind_method(D_METHOD("get_symbols"), &SVGResource::get_symbols);
    ClassDB::bind_method(D_METHOD("get_fill_overrides"), &SVGResource::get_fill_overrides);
    ClassDB::bind_method(D_METHOD("get_stroke_overrides"), &SVGResource::get_stroke_overrides);
    ClassDB::bind_method(D_METHOD("get_shader_overrides"), &SVGResource::get_shader_overrides);
    
    // Rasterization
    ClassDB::bind_method(D_METHOD("rasterize_full", "size"), &SVGResource::rasterize_full);
    ClassDB::bind_method(D_METHOD("rasterize_symbol", "symbol_id", "size"), &SVGResource::rasterize_symbol);
}

Error SVGResource::load_from_file(const String &p_path) {
    Ref<FileAccess> file = FileAccess::open(p_path, FileAccess::READ);
    ERR_FAIL_COND_V_MSG(file.is_null(), ERR_FILE_CANT_OPEN, "Cannot open SVG file: " + p_path);
    
    String content = file->get_as_text();
    file->close();
    
    return load_from_string(content);
}

Error SVGResource::load_from_string(const String &p_svg_string) {
    if (p_svg_string.is_empty()) {
        ERR_PRINT("SVG string is empty");
        return ERR_INVALID_PARAMETER;
    }
    
    svg_data = p_svg_string;
    _parse_svg();
    _extract_symbols();
    
    emit_changed();
    return OK;
}

void SVGResource::_parse_svg() {
    document = LunaSVGIntegration::load_svg_from_string(svg_data);
    if (!document) {
        ERR_PRINT("Failed to parse SVG data");
    } else {
        print_line("SVGResource: Successfully parsed SVG document");
        _apply_stored_overrides();
    }
}

void SVGResource::_extract_symbols() {
    symbols.clear();
    
    if (!document) {
        return;
    }
    
    // Query for all symbol elements
    Vector<lunasvg::Element> symbol_elements = LunaSVGIntegration::query_elements(document.get(), "symbol");
    
    for (const auto& element : symbol_elements) {
        // Get the ID attribute
        String symbol_id = LunaSVGIntegration::get_element_attribute(element, "id");
        
        if (!symbol_id.is_empty()) {
            Dictionary symbol_data;
            
            // Store element reference (as pointer for internal use)
            symbol_data["has_element"] = true;
            
            // Get viewBox if available
            String viewbox = LunaSVGIntegration::get_element_attribute(element, "viewBox");
            if (!viewbox.is_empty()) {
                symbol_data["viewBox"] = viewbox;
            }
            
            // Calculate bounding box
            lunasvg::Box bbox = element.getBoundingBox();
            Rect2 bounds(bbox.x, bbox.y, bbox.w, bbox.h);
            symbol_data["bounds"] = bounds;
            
            symbols[symbol_id] = symbol_data;
            print_line("Found symbol with ID: " + symbol_id);
        }
    }
    
    print_line("SVGResource: Extracted " + String::num_int64(symbols.size()) + " symbols");
}

PackedStringArray SVGResource::get_symbol_ids() const {
    PackedStringArray ids;
    Array keys = symbols.keys();
    for (int i = 0; i < keys.size(); i++) {
        ids.push_back(keys[i]);
    }
    return ids;
}

bool SVGResource::has_symbol(const String &p_id) const {
    return symbols.has(p_id);
}

Dictionary SVGResource::get_symbol_data(const String &p_id) const {
    if (!has_symbol(p_id)) {
        return Dictionary();
    }
    return symbols[p_id];
}

void SVGResource::override_fill(const String &p_element_id, const Color &p_color) {
    fill_overrides[p_element_id] = p_color;
    
    // Apply the override immediately if document is loaded
    if (document) {
        lunasvg::Element element = LunaSVGIntegration::find_element_by_id(document.get(), p_element_id);
        if (!element.isNull()) {
            LunaSVGIntegration::apply_fill_color(element, p_color);
        }
    }
    
    emit_changed();
}

void SVGResource::override_stroke(const String &p_element_id, const Color &p_color) {
    stroke_overrides[p_element_id] = p_color;
    
    // Apply the override immediately if document is loaded
    if (document) {
        lunasvg::Element element = LunaSVGIntegration::find_element_by_id(document.get(), p_element_id);
        if (!element.isNull()) {
            LunaSVGIntegration::apply_stroke_color(element, p_color);
        }
    }
    
    emit_changed();
}

void SVGResource::override_shader(const String &p_element_id, Ref<Shader> p_shader) {
    shader_overrides[p_element_id] = p_shader;
    emit_changed();
}

void SVGResource::clear_fill_override(const String &p_element_id) {
    fill_overrides.erase(p_element_id);
    emit_changed();
}

void SVGResource::clear_stroke_override(const String &p_element_id) {
    stroke_overrides.erase(p_element_id);
    emit_changed();
}

void SVGResource::clear_shader_override(const String &p_element_id) {
    shader_overrides.erase(p_element_id);
    emit_changed();
}

void SVGResource::clear_all_overrides() {
    fill_overrides.clear();
    stroke_overrides.clear();
    shader_overrides.clear();
    emit_changed();
}

Ref<Image> SVGResource::rasterize_full(const Vector2i &p_size) const {
    if (!document) {
        ERR_PRINT("SVG document not loaded");
        return Ref<Image>();
    }
    
    return LunaSVGIntegration::rasterize_document(document.get(), p_size);
}

Ref<Image> SVGResource::rasterize_symbol(const String &p_symbol_id, const Vector2i &p_size) const {
    if (!document) {
        ERR_PRINT("SVG document not loaded");
        return Ref<Image>();
    }
    
    // Find the symbol element by ID
    lunasvg::Element element = LunaSVGIntegration::find_element_by_id(document.get(), p_symbol_id);
    if (element.isNull()) {
        ERR_PRINT("Symbol not found: " + p_symbol_id);
        return Ref<Image>();
    }
      return LunaSVGIntegration::rasterize_element(element, p_size);
}

void SVGResource::_apply_stored_overrides() {
    if (!document) {
        return;
    }
    
    // Apply stored fill overrides
    Array fill_keys = fill_overrides.keys();
    for (int i = 0; i < fill_keys.size(); i++) {
        String element_id = fill_keys[i];
        Color color = fill_overrides[element_id];
        
        lunasvg::Element element = LunaSVGIntegration::find_element_by_id(document.get(), element_id);
        if (!element.isNull()) {
            LunaSVGIntegration::apply_fill_color(element, color);
        }
    }
    
    // Apply stored stroke overrides
    Array stroke_keys = stroke_overrides.keys();
    for (int i = 0; i < stroke_keys.size(); i++) {
        String element_id = stroke_keys[i];
        Color color = stroke_overrides[element_id];
        
        lunasvg::Element element = LunaSVGIntegration::find_element_by_id(document.get(), element_id);
        if (!element.isNull()) {
            LunaSVGIntegration::apply_stroke_color(element, color);
        }
    }
    
    print_line("Applied " + String::num_int64(fill_keys.size() + stroke_keys.size()) + " style overrides");
}
