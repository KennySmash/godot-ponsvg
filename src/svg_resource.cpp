#include "svg_resource.h"

#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/classes/file_access.hpp>
#include <godot_cpp/classes/time.hpp>
#include <godot_cpp/classes/sub_viewport.hpp>
#include <godot_cpp/classes/texture_rect.hpp>
#include <godot_cpp/classes/image_texture.hpp>
#include <godot_cpp/classes/viewport_texture.hpp>
#include <godot_cpp/variant/utility_functions.hpp>

#include "lunasvg.h"

using namespace godot;

PonSVGResource::PonSVGResource() {
    last_modification_time = 0;
    needs_cache_clear = false;
    cache_enabled = true;
    lod_enabled = false;
    lod_bias = 1.0f;
}

PonSVGResource::~PonSVGResource() {
    _clear_cache();
}

void PonSVGResource::_bind_methods() {
    // Core loading
    ClassDB::bind_method(D_METHOD("load_from_file", "path"), &PonSVGResource::load_from_file);
    ClassDB::bind_method(D_METHOD("load_from_string", "svg_string"), &PonSVGResource::load_from_string);
    
    // Symbol management
    ClassDB::bind_method(D_METHOD("get_symbol_ids"), &PonSVGResource::get_symbol_ids);
    ClassDB::bind_method(D_METHOD("has_symbol", "id"), &PonSVGResource::has_symbol);
    ClassDB::bind_method(D_METHOD("get_symbol_data", "id"), &PonSVGResource::get_symbol_data);
    
    // Style overrides
    ClassDB::bind_method(D_METHOD("override_fill", "element_id", "color"), &PonSVGResource::override_fill);
    ClassDB::bind_method(D_METHOD("override_stroke", "element_id", "color"), &PonSVGResource::override_stroke);
    ClassDB::bind_method(D_METHOD("override_shader", "element_id", "shader"), &PonSVGResource::override_shader);
    
    // Class-based overrides
    ClassDB::bind_method(D_METHOD("override_fill_by_class", "class_name", "color"), &PonSVGResource::override_fill_by_class);
    ClassDB::bind_method(D_METHOD("override_stroke_by_class", "class_name", "color"), &PonSVGResource::override_stroke_by_class);
    
    // CSS property overrides
    ClassDB::bind_method(D_METHOD("override_css_property", "element_id", "property", "value"), &PonSVGResource::override_css_property);
    
    ClassDB::bind_method(D_METHOD("clear_fill_override", "element_id"), &PonSVGResource::clear_fill_override);
    ClassDB::bind_method(D_METHOD("clear_stroke_override", "element_id"), &PonSVGResource::clear_stroke_override);
    ClassDB::bind_method(D_METHOD("clear_shader_override", "element_id"), &PonSVGResource::clear_shader_override);
    ClassDB::bind_method(D_METHOD("clear_all_overrides"), &PonSVGResource::clear_all_overrides);
    
    // Getters
    ClassDB::bind_method(D_METHOD("get_svg_data"), &PonSVGResource::get_svg_data);
    ClassDB::bind_method(D_METHOD("get_symbols"), &PonSVGResource::get_symbols);
    ClassDB::bind_method(D_METHOD("get_fill_overrides"), &PonSVGResource::get_fill_overrides);
    ClassDB::bind_method(D_METHOD("get_stroke_overrides"), &PonSVGResource::get_stroke_overrides);
    ClassDB::bind_method(D_METHOD("get_shader_overrides"), &PonSVGResource::get_shader_overrides);
      // Rasterization
    ClassDB::bind_method(D_METHOD("rasterize_full", "size"), &PonSVGResource::rasterize_full);
    ClassDB::bind_method(D_METHOD("rasterize_symbol", "symbol_id", "size"), &PonSVGResource::rasterize_symbol);
    ClassDB::bind_method(D_METHOD("rasterize_element_with_shader", "element_id", "size", "shader"), &PonSVGResource::rasterize_element_with_shader);
      // Cache management
    ClassDB::bind_method(D_METHOD("clear_cache"), &PonSVGResource::clear_cache);
    ClassDB::bind_method(D_METHOD("get_cache_size"), &PonSVGResource::get_cache_size);
    ClassDB::bind_method(D_METHOD("set_cache_enabled", "enabled"), &PonSVGResource::set_cache_enabled);
    ClassDB::bind_method(D_METHOD("is_cache_enabled"), &PonSVGResource::is_cache_enabled);
    
    // LOD system
    ClassDB::bind_method(D_METHOD("set_lod_enabled", "enabled"), &PonSVGResource::set_lod_enabled);
    ClassDB::bind_method(D_METHOD("is_lod_enabled"), &PonSVGResource::is_lod_enabled);
    ClassDB::bind_method(D_METHOD("set_lod_bias", "bias"), &PonSVGResource::set_lod_bias);
    ClassDB::bind_method(D_METHOD("get_lod_bias"), &PonSVGResource::get_lod_bias);
    ClassDB::bind_method(D_METHOD("calculate_lod_size", "requested_size"), &PonSVGResource::calculate_lod_size);
    
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "cache_enabled"), "set_cache_enabled", "is_cache_enabled");
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "lod_enabled"), "set_lod_enabled", "is_lod_enabled");
    ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "lod_bias", PROPERTY_HINT_RANGE, "0.1,4.0,0.1"), "set_lod_bias", "get_lod_bias");
}

Error PonSVGResource::load_from_file(const String &p_path) {
    Ref<FileAccess> file = FileAccess::open(p_path, FileAccess::READ);
    if (file.is_null()) {
        UtilityFunctions::push_error("Cannot open SVG file: " + p_path);
        return ERR_FILE_CANT_OPEN;
    }
    
    String content = file->get_as_text();
    file->close();
    
    return load_from_string(content);
}

Error PonSVGResource::load_from_string(const String &p_svg_string) {
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

void PonSVGResource::_parse_svg() {
    document = LunaSVGIntegration::load_svg_from_string(svg_data);
    if (!document) {
        ERR_PRINT("Failed to parse SVG data");
    } else {
        print_line("PonSVGResource: Successfully parsed SVG document");
        _apply_stored_overrides();
    }
}

void PonSVGResource::_extract_symbols() {
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
    
    print_line("PonSVGResource: Extracted " + String::num_int64(symbols.size()) + " symbols");
}

PackedStringArray PonSVGResource::get_symbol_ids() const {
    PackedStringArray ids;
    Array keys = symbols.keys();
    for (int i = 0; i < keys.size(); i++) {
        ids.push_back(keys[i]);
    }
    return ids;
}

bool PonSVGResource::has_symbol(const String &p_id) const {
    return symbols.has(p_id);
}

Dictionary PonSVGResource::get_symbol_data(const String &p_id) const {
    if (!has_symbol(p_id)) {
        return Dictionary();
    }
    return symbols[p_id];
}

void PonSVGResource::override_fill(const String &p_element_id, const Color &p_color) {
    fill_overrides[p_element_id] = p_color;
    
    // Apply the override immediately if document is loaded
    if (document) {
        lunasvg::Element element = LunaSVGIntegration::find_element_by_id(document.get(), p_element_id);
        if (!element.isNull()) {
            LunaSVGIntegration::apply_fill_color(element, p_color);
        }
    }
    
    // Invalidate cache
    needs_cache_clear = true;
    emit_changed();
}

void PonSVGResource::override_stroke(const String &p_element_id, const Color &p_color) {
    stroke_overrides[p_element_id] = p_color;
    
    // Apply the override immediately if document is loaded
    if (document) {
        lunasvg::Element element = LunaSVGIntegration::find_element_by_id(document.get(), p_element_id);
        if (!element.isNull()) {
            LunaSVGIntegration::apply_stroke_color(element, p_color);
        }
    }
    
    // Invalidate cache
    needs_cache_clear = true;
    emit_changed();
}

void PonSVGResource::override_shader(const String &p_element_id, Ref<Shader> p_shader) {
    shader_overrides[p_element_id] = p_shader;
    // Invalidate cache
    needs_cache_clear = true;
    emit_changed();
}

void PonSVGResource::clear_fill_override(const String &p_element_id) {
    fill_overrides.erase(p_element_id);
    needs_cache_clear = true;
    emit_changed();
}

void PonSVGResource::clear_stroke_override(const String &p_element_id) {
    stroke_overrides.erase(p_element_id);
    needs_cache_clear = true;
    emit_changed();
}

void PonSVGResource::clear_shader_override(const String &p_element_id) {
    shader_overrides.erase(p_element_id);
    needs_cache_clear = true;
    emit_changed();
}

void PonSVGResource::clear_all_overrides() {
    fill_overrides.clear();
    stroke_overrides.clear();
    shader_overrides.clear();
    css_overrides.clear();
    needs_cache_clear = true;
    emit_changed();
}

// Class-based override implementations
void PonSVGResource::override_fill_by_class(const String &p_class_name, const Color &p_color) {
    String class_key = "." + p_class_name;
    fill_overrides[class_key] = p_color;
    needs_cache_clear = true;
    emit_changed();
}

void PonSVGResource::override_stroke_by_class(const String &p_class_name, const Color &p_color) {
    String class_key = "." + p_class_name;
    stroke_overrides[class_key] = p_color;
    needs_cache_clear = true;
    emit_changed();
}

void PonSVGResource::override_css_property(const String &p_element_id, const String &p_property, const String &p_value) {
    // Store CSS properties in a separate dictionary for more flexible styling
    String css_key = p_element_id + String("::") + p_property;
    if (!css_overrides.has(p_element_id)) {
        css_overrides[p_element_id] = Dictionary();
    }
    Dictionary element_css = css_overrides[p_element_id];
    element_css[p_property] = p_value;
    css_overrides[p_element_id] = element_css;
    
    needs_cache_clear = true;
    emit_changed();
}

void PonSVGResource::_clear_cache() const {
    cache_entries.clear();
    needs_cache_clear = false;
}

String PonSVGResource::_generate_cache_key(const String &p_content_id, const Vector2i &p_size) const {
    String key = p_content_id + String("_") + String::num_int64(p_size.x) + String("x") + String::num_int64(p_size.y);
      // Include override hashes in cache key
    if (fill_overrides.size() > 0 || stroke_overrides.size() > 0 || shader_overrides.size() > 0 || css_overrides.size() > 0) {        key += String("_overrides_") + String::num_int64(fill_overrides.hash()) + 
               String("_") + String::num_int64(stroke_overrides.hash()) +
               String("_") + String::num_int64(shader_overrides.hash()) +
               String("_") + String::num_int64(css_overrides.hash());
    }
    
    return key;
}

Ref<Image> PonSVGResource::_get_cached_image(const String &p_cache_key, const Vector2i &p_size) const {
    if (!cache_enabled) {
        return Ref<Image>();
    }
    
    if (needs_cache_clear) {
        _clear_cache();
    }
      if (cache_entries.has(p_cache_key)) {
        Dictionary entry = cache_entries[p_cache_key];
        bool is_dirty = entry.get("is_dirty", true);
        Vector2i size = entry.get("size", Vector2i());
        Ref<Image> image = entry.get("image", Ref<Image>());
        
        if (!is_dirty && size == p_size && image.is_valid()) {
            return image;
        }
    }
    
    return Ref<Image>();
}

void PonSVGResource::_store_cached_image(const String &p_cache_key, const Vector2i &p_size, const Ref<Image> &p_image) const {
    if (!cache_enabled) {
        return;
    }
      Dictionary entry;
    entry["image"] = p_image;
    entry["size"] = p_size;
    entry["cache_key"] = p_cache_key;
    entry["timestamp"] = Time::get_singleton()->get_ticks_msec();
    entry["is_dirty"] = false;
    
    cache_entries[p_cache_key] = entry;
}

void PonSVGResource::clear_cache() {
    _clear_cache();
    emit_changed();
}

int PonSVGResource::get_cache_size() const {
    return cache_entries.size();
}

void PonSVGResource::set_cache_enabled(bool p_enabled) {
    cache_enabled = p_enabled;
    if (!p_enabled) {
        _clear_cache();
    }
}

bool PonSVGResource::is_cache_enabled() const {
    return cache_enabled;
}

// Enhanced rasterization with caching and LOD support
Ref<Image> PonSVGResource::rasterize_full(const Vector2i &p_size) const {
    ERR_FAIL_COND_V_MSG(document == nullptr, Ref<Image>(), "SVG document not loaded");
    ERR_FAIL_COND_V_MSG(p_size.x <= 0 || p_size.y <= 0, Ref<Image>(), "Invalid size for rasterization");
    
    // Apply LOD if enabled
    Vector2i actual_size = calculate_lod_size(p_size);
    
    String cache_key = _generate_cache_key("full_svg", actual_size);
    Ref<Image> cached = _get_cached_image(cache_key, actual_size);
    if (cached.is_valid()) {
        // If LOD changed the size, scale the cached image to requested size
        if (actual_size != p_size && cached.is_valid()) {
            cached = cached->duplicate();
            cached->resize(p_size.x, p_size.y, Image::INTERPOLATE_LANCZOS);
        }
        return cached;
    }
    
    Ref<Image> result = LunaSVGIntegration::rasterize_document(document.get(), actual_size);
    if (result.is_valid()) {
        _store_cached_image(cache_key, actual_size, result);
        
        // Scale to requested size if needed
        if (actual_size != p_size) {
            result = result->duplicate();
            result->resize(p_size.x, p_size.y, Image::INTERPOLATE_LANCZOS);
        }
    }
    
    return result;
}

Ref<Image> PonSVGResource::rasterize_symbol(const String &p_symbol_id, const Vector2i &p_size) const {
    ERR_FAIL_COND_V_MSG(document == nullptr, Ref<Image>(), "SVG document not loaded");
    ERR_FAIL_COND_V_MSG(p_size.x <= 0 || p_size.y <= 0, Ref<Image>(), "Invalid size for rasterization");
    ERR_FAIL_COND_V_MSG(!has_symbol(p_symbol_id), Ref<Image>(), "Symbol not found: " + p_symbol_id);
    
    // Apply LOD if enabled
    Vector2i actual_size = calculate_lod_size(p_size);
    
    String cache_key = _generate_cache_key("symbol_" + p_symbol_id, actual_size);
    Ref<Image> cached = _get_cached_image(cache_key, actual_size);
    if (cached.is_valid()) {
        // If LOD changed the size, scale the cached image to requested size
        if (actual_size != p_size && cached.is_valid()) {
            cached = cached->duplicate();
            cached->resize(p_size.x, p_size.y, Image::INTERPOLATE_LANCZOS);
        }
        return cached;
    }
      lunasvg::Element element = LunaSVGIntegration::find_element_by_id(document.get(), p_symbol_id);
    if (element.isNull()) {
        ERR_PRINT("Could not find symbol element with ID: " + p_symbol_id);
        return Ref<Image>();
    }
    
    // Apply style overrides before rasterization
    _apply_overrides_to_element(element, p_symbol_id);
    
    Ref<Image> result = LunaSVGIntegration::rasterize_element(element, actual_size);
    if (result.is_valid()) {
        _store_cached_image(cache_key, actual_size, result);
        
        // Scale to requested size if needed
        if (actual_size != p_size) {
            result = result->duplicate();
            result->resize(p_size.x, p_size.y, Image::INTERPOLATE_LANCZOS);
        }
    }
    
    return result;
}

// Shader override implementation
Ref<Image> PonSVGResource::rasterize_element_with_shader(const String &p_element_id, const Vector2i &p_size, Ref<Shader> p_shader) const {
    ERR_FAIL_COND_V_MSG(document == nullptr, Ref<Image>(), "SVG document not loaded");
    ERR_FAIL_COND_V_MSG(p_size.x <= 0 || p_size.y <= 0, Ref<Image>(), "Invalid size for rasterization");
    ERR_FAIL_COND_V_MSG(p_shader.is_null(), Ref<Image>(), "Shader is null");
      // For now, this renders the element normally and then applies the shader as a post-process
    // A more advanced implementation would integrate with Godot's rendering pipeline
    lunasvg::Element element = LunaSVGIntegration::find_element_by_id(document.get(), p_element_id);
    if (element.isNull()) {
        ERR_PRINT("Could not find element with ID: " + p_element_id);
        return Ref<Image>();
    }
      // Apply style overrides before rasterization
    _apply_overrides_to_element(element, p_element_id);
    
    // First, render the element normally
    Ref<Image> base_image = LunaSVGIntegration::rasterize_element(element, p_size);
    if (base_image.is_null()) {
        return Ref<Image>();
    }
    
    // Apply shader processing if valid
    if (p_shader.is_valid() && _validate_shader(p_shader)) {
        Ref<Image> processed_image = _apply_shader_to_image(base_image, p_shader, p_size);
        if (processed_image.is_valid()) {
            return processed_image;
        } else {
            print_line("Warning: Shader processing failed, returning base image.");
        }
    } else {
        print_line("Warning: Invalid shader provided, returning base image.");
    }
    
    return base_image;
}

void PonSVGResource::_apply_stored_overrides() {
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

void PonSVGResource::_apply_overrides_to_element(lunasvg::Element& element, const String& element_id) const {
    if (element.isNull()) {
        return;
    }
    
    // Apply fill override if exists
    if (fill_overrides.has(element_id)) {
        Color color = fill_overrides[element_id];
        LunaSVGIntegration::apply_fill_color(element, color);
    }
    
    // Apply stroke override if exists  
    if (stroke_overrides.has(element_id)) {
        Color color = stroke_overrides[element_id];
        LunaSVGIntegration::apply_stroke_color(element, color);
    }
      // Apply CSS property overrides if they exist
    if (css_overrides.has(element_id)) {
        Dictionary element_css = css_overrides[element_id];
        Array css_keys = element_css.keys();
        for (int i = 0; i < css_keys.size(); i++) {
            String property = css_keys[i];
            String value = element_css[property];
            LunaSVGIntegration::apply_css_style(element, property, value);
        }
    }
    
    // Apply shader override if exists
    if (shader_overrides.has(element_id)) {
        // Shader overrides are handled at the texture level, not at the SVG level
        // This is noted for the calling code to handle appropriately
        print_line("Shader override detected for element: " + element_id + " (handled at texture level)");
    }
    
    // Apply overrides to child elements recursively (for comprehensive styling)
    _apply_overrides_to_children(element, element_id);
}

void PonSVGResource::_apply_overrides_to_children(lunasvg::Element& parent_element, const String& base_id) const {
    if (parent_element.isNull()) {
        return;
    }
      // Get all child elements and apply matching overrides
    auto children = parent_element.children();
    for (const auto& child : children) {
        if (child.isNull() || !child.isElement()) continue;
        
        // Convert Node to Element
        lunasvg::Element child_element = child.toElement();
        if (child_element.isNull()) continue;
        
        // Check if child has an ID that matches our overrides
        String child_id = LunaSVGIntegration::get_element_attribute(child_element, "id");
        if (!child_id.is_empty()) {
            // Apply overrides for this specific child ID
            if (fill_overrides.has(child_id)) {
                Color color = fill_overrides[child_id];
                LunaSVGIntegration::apply_fill_color(child_element, color);
            }
            if (stroke_overrides.has(child_id)) {
                Color color = stroke_overrides[child_id];
                LunaSVGIntegration::apply_stroke_color(child_element, color);
            }        }
        
        // Also check for class-based or tag-based overrides
        String child_class = LunaSVGIntegration::get_element_attribute(child_element, "class");
        if (!child_class.is_empty()) {
            String class_override_key = "." + child_class;
            if (fill_overrides.has(class_override_key)) {
                Color color = fill_overrides[class_override_key];
                LunaSVGIntegration::apply_fill_color(child_element, color);
            }
            if (stroke_overrides.has(class_override_key)) {
                Color color = stroke_overrides[class_override_key];
                LunaSVGIntegration::apply_stroke_color(child_element, color);
            }
        }
        
        // Recursively apply to grandchildren
        _apply_overrides_to_children(child_element, base_id);
    }
}

// LOD (Level of Detail) System Implementation
void PonSVGResource::set_lod_enabled(bool p_enabled) {
    if (lod_enabled != p_enabled) {
        lod_enabled = p_enabled;
        if (lod_enabled) {
            // Clear cache when enabling LOD to recalculate sizes
            needs_cache_clear = true;
        }
        emit_changed();
    }
}

bool PonSVGResource::is_lod_enabled() const {
    return lod_enabled;
}

void PonSVGResource::set_lod_bias(float p_bias) {
    p_bias = CLAMP(p_bias, 0.1f, 4.0f);
    if (lod_bias != p_bias) {
        lod_bias = p_bias;
        if (lod_enabled) {
            needs_cache_clear = true;
        }
        emit_changed();
    }
}

float PonSVGResource::get_lod_bias() const {
    return lod_bias;
}

Vector2i PonSVGResource::calculate_lod_size(const Vector2i &p_requested_size) const {
    if (!lod_enabled) {
        return p_requested_size;
    }
    
    // Calculate LOD level based on size and bias
    // Smaller sizes get lower detail, larger sizes get higher detail
    Vector2i max_size = Vector2i(4096, 4096); // Maximum detail size
    Vector2i min_size = Vector2i(32, 32);     // Minimum detail size
    
    float scale_factor = lod_bias;
    
    // Scale down for very small sizes to save memory
    if (p_requested_size.x < 128 || p_requested_size.y < 128) {
        scale_factor *= 0.75f;
    }
    // Scale up for larger sizes but cap it
    else if (p_requested_size.x > 512 || p_requested_size.y > 512) {
        scale_factor *= 1.25f;
    }
    
    Vector2i lod_size = Vector2i(
        int(p_requested_size.x * scale_factor),
        int(p_requested_size.y * scale_factor)
    );
    
    // Clamp to reasonable bounds
    lod_size.x = CLAMP(lod_size.x, min_size.x, max_size.x);
    lod_size.y = CLAMP(lod_size.y, min_size.y, max_size.y);
    
    return lod_size;
}

// Shader processing implementation
Ref<Image> PonSVGResource::_apply_shader_to_image(const Ref<Image> &p_base_image, Ref<Shader> p_shader, const Vector2i &p_size) const {
    if (p_base_image.is_null() || p_shader.is_null()) {
        return Ref<Image>();
    }
    
    // Create temporary SubViewport for shader processing
    SubViewport *viewport = memnew(SubViewport);
    viewport->set_size(p_size);
    viewport->set_render_target_update_mode(SubViewport::UPDATE_ONCE);
    
    // Create TextureRect to hold the base image
    TextureRect *texture_rect = memnew(TextureRect);
    texture_rect->set_size(Vector2(p_size.x, p_size.y));
    texture_rect->set_stretch_mode(TextureRect::STRETCH_KEEP_ASPECT_COVERED);
    
    // Create ImageTexture from base image
    Ref<ImageTexture> image_texture;
    image_texture.instantiate();
    image_texture->set_image(p_base_image);
    texture_rect->set_texture(image_texture);
    
    // Create and apply shader material
    Ref<ShaderMaterial> shader_material;
    shader_material.instantiate();
    shader_material->set_shader(p_shader);
    texture_rect->set_material(shader_material);
    
    // Add to viewport and process
    viewport->add_child(texture_rect);
    
    // Force render update
    viewport->set_render_target_update_mode(SubViewport::UPDATE_ONCE);
    
    // Get the processed texture
    Ref<ViewportTexture> viewport_texture = viewport->get_texture();
    if (viewport_texture.is_null()) {
        // Cleanup and return null
        viewport->queue_free();
        return Ref<Image>();
    }
    
    // Extract image from viewport texture
    Ref<Image> processed_image = viewport_texture->get_image();
    
    // Cleanup temporary resources
    viewport->queue_free();
    
    return processed_image;
}

bool PonSVGResource::_validate_shader(Ref<Shader> p_shader) const {
    if (p_shader.is_null()) {
        return false;
    }
    
    // Check if shader has valid code
    String shader_code = p_shader->get_code();
    if (shader_code.is_empty()) {
        return false;
    }
    
    // Basic validation - check for fragment shader
    if (!shader_code.contains("shader_type canvas_item")) {
        print_line("Warning: Shader must be of type 'canvas_item' for SVG processing.");
        return false;
    }
    
    return true;
}
