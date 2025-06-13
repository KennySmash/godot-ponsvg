#ifndef SVG_RESOURCE_H
#define SVG_RESOURCE_H

#include "core/io/resource.h"
#include "core/variant/dictionary.h"
#include "scene/resources/shader.h"
#include "scene/resources/shader_material.h"
#include "lunasvg_integration.h"
#include <memory>

namespace lunasvg {
    class Document;
}

// Cache entry for rendered SVG content
struct SVGCacheEntry {
    Ref<Image> image;
    Vector2i size;
    String cache_key;
    uint64_t timestamp;
    bool is_dirty;
    
    SVGCacheEntry() : timestamp(0), is_dirty(true) {}
};

class SVGResource : public Resource {
    GDCLASS(SVGResource, Resource);

private:
    String svg_data;
    std::unique_ptr<lunasvg::Document> document;
    Dictionary symbols;
    Dictionary fill_overrides;
    Dictionary stroke_overrides;
    Dictionary shader_overrides;
      // Performance optimization - caching system
    mutable Dictionary cache_entries; // String -> SVGCacheEntry
    mutable uint64_t last_modification_time;
    mutable bool needs_cache_clear;
    mutable bool cache_enabled;
    
    // LOD system
    bool lod_enabled;
    float lod_bias;
    
    void _parse_svg();
    void _extract_symbols();
    void _apply_stored_overrides();
    void _clear_cache() const;
    String _generate_cache_key(const String &p_content_id, const Vector2i &p_size) const;
    Ref<Image> _get_cached_image(const String &p_cache_key, const Vector2i &p_size) const;
    void _store_cached_image(const String &p_cache_key, const Vector2i &p_size, const Ref<Image> &p_image) const;

protected:
    static void _bind_methods();

public:
    SVGResource();
    ~SVGResource();

    // Core loading functionality
    Error load_from_file(const String &p_path);
    Error load_from_string(const String &p_svg_string);
    
    // Symbol management
    PackedStringArray get_symbol_ids() const;
    bool has_symbol(const String &p_id) const;
    Dictionary get_symbol_data(const String &p_id) const;
    
    // Style overrides
    void override_fill(const String &p_element_id, const Color &p_color);
    void override_stroke(const String &p_element_id, const Color &p_color);
    void override_shader(const String &p_element_id, Ref<Shader> p_shader);
    
    void clear_fill_override(const String &p_element_id);
    void clear_stroke_override(const String &p_element_id);
    void clear_shader_override(const String &p_element_id);
    void clear_all_overrides();
    
    // Getters
    String get_svg_data() const { return svg_data; }
    Dictionary get_symbols() const { return symbols; }
    Dictionary get_fill_overrides() const { return fill_overrides; }
    Dictionary get_stroke_overrides() const { return stroke_overrides; }
    Dictionary get_shader_overrides() const { return shader_overrides; }
    
    // Document access for internal use
    lunasvg::Document* get_document() const { return document.get(); }
      // Rasterization support
    Ref<Image> rasterize_full(const Vector2i &p_size) const;
    Ref<Image> rasterize_symbol(const String &p_symbol_id, const Vector2i &p_size) const;
    Ref<Image> rasterize_element_with_shader(const String &p_element_id, const Vector2i &p_size, Ref<Shader> p_shader) const;
      // Performance and caching
    void clear_cache();
    int get_cache_size() const;
    void set_cache_enabled(bool p_enabled);
    bool is_cache_enabled() const;
    
    // LOD (Level of Detail) system
    void set_lod_enabled(bool p_enabled);
    bool is_lod_enabled() const;
    void set_lod_bias(float p_bias);
    float get_lod_bias() const;
    Vector2i calculate_lod_size(const Vector2i &p_requested_size) const;
};

#endif // SVG_RESOURCE_H
