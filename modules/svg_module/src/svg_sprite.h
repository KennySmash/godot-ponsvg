#ifndef SVG_SPRITE_H
#define SVG_SPRITE_H

#include "scene/2d/node_2d.h"
#include "scene/resources/shader_material.h"
#include "svg_resource.h"

class SVGSprite2D : public Node2D {
    GDCLASS(SVGSprite2D, Node2D);

private:
    Ref<SVGResource> svg_resource;
    String symbol_id;
    Vector2 draw_size;
    bool centered;
    Color modulate_color;
    Ref<ShaderMaterial> material_override;
    
    Ref<Image> cached_image;
    RID texture_rid;
    bool needs_update;
    
    void _update_texture();
    void _draw_sprite();

protected:
    static void _bind_methods();
    virtual void _notification(int p_what);

public:
    SVGSprite2D();
    ~SVGSprite2D();

    // SVG-specific properties
    void set_svg_resource(const Ref<SVGResource> &p_resource);
    Ref<SVGResource> get_svg_resource() const;
    
    void set_symbol_id(const String &p_id);
    String get_symbol_id() const;
    
    void set_draw_size(const Vector2 &p_size);
    Vector2 get_draw_size() const;
    
    void set_centered(bool p_centered);
    bool is_centered() const;
    
    void set_modulate(const Color &p_color);
    Color get_modulate() const;
    
    void set_material_override(const Ref<ShaderMaterial> &p_material);
    Ref<ShaderMaterial> get_material_override() const;
    
    // Utility methods
    void force_update();
    Rect2 get_rect() const;
};

#endif // SVG_SPRITE_H
