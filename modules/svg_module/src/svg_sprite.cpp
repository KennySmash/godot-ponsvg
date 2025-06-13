#include "svg_sprite.h"
#include "servers/rendering_server.h"

SVGSprite2D::SVGSprite2D() {
    draw_size = Vector2(64, 64);
    centered = true;
    modulate_color = Color(1, 1, 1, 1);
    needs_update = true;
    texture_rid = RenderingServer::get_singleton()->texture_2d_create(Ref<Image>());
}

SVGSprite2D::~SVGSprite2D() {
    if (texture_rid.is_valid()) {
        RenderingServer::get_singleton()->free_rid(texture_rid);
    }
}

void SVGSprite2D::_bind_methods() {
    ClassDB::bind_method(D_METHOD("set_svg_resource", "resource"), &SVGSprite2D::set_svg_resource);
    ClassDB::bind_method(D_METHOD("get_svg_resource"), &SVGSprite2D::get_svg_resource);
    
    ClassDB::bind_method(D_METHOD("set_symbol_id", "id"), &SVGSprite2D::set_symbol_id);
    ClassDB::bind_method(D_METHOD("get_symbol_id"), &SVGSprite2D::get_symbol_id);
    
    ClassDB::bind_method(D_METHOD("set_draw_size", "size"), &SVGSprite2D::set_draw_size);
    ClassDB::bind_method(D_METHOD("get_draw_size"), &SVGSprite2D::get_draw_size);
    
    ClassDB::bind_method(D_METHOD("set_centered", "centered"), &SVGSprite2D::set_centered);
    ClassDB::bind_method(D_METHOD("is_centered"), &SVGSprite2D::is_centered);
    
    ClassDB::bind_method(D_METHOD("set_modulate", "color"), &SVGSprite2D::set_modulate);
    ClassDB::bind_method(D_METHOD("get_modulate"), &SVGSprite2D::get_modulate);
    
    ClassDB::bind_method(D_METHOD("set_material_override", "material"), &SVGSprite2D::set_material_override);
    ClassDB::bind_method(D_METHOD("get_material_override"), &SVGSprite2D::get_material_override);
    
    ClassDB::bind_method(D_METHOD("force_update"), &SVGSprite2D::force_update);
    ClassDB::bind_method(D_METHOD("get_rect"), &SVGSprite2D::get_rect);
    
    ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "svg_resource", PROPERTY_HINT_RESOURCE_TYPE, "SVGResource"), "set_svg_resource", "get_svg_resource");
    ADD_PROPERTY(PropertyInfo(Variant::STRING, "symbol_id"), "set_symbol_id", "get_symbol_id");
    ADD_PROPERTY(PropertyInfo(Variant::VECTOR2, "draw_size"), "set_draw_size", "get_draw_size");
    ADD_PROPERTY(PropertyInfo(Variant::BOOL, "centered"), "set_centered", "is_centered");
    ADD_PROPERTY(PropertyInfo(Variant::COLOR, "modulate"), "set_modulate", "get_modulate");
    ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "material_override", PROPERTY_HINT_RESOURCE_TYPE, "ShaderMaterial"), "set_material_override", "get_material_override");
}

void SVGSprite2D::_notification(int p_what) {
    switch (p_what) {
        case NOTIFICATION_DRAW: {
            _draw_sprite();
        } break;
    }
}

void SVGSprite2D::_update_texture() {
    if (!needs_update || svg_resource.is_null()) {
        return;
    }
    
    Vector2i size = Vector2i(int(draw_size.x), int(draw_size.y));
    
    if (symbol_id.is_empty()) {
        // Render full SVG
        cached_image = svg_resource->rasterize_full(size);
    } else {
        // Render specific symbol
        cached_image = svg_resource->rasterize_symbol(symbol_id, size);
    }
    
    if (cached_image.is_valid()) {
        RenderingServer::get_singleton()->texture_2d_update(texture_rid, cached_image);
    }
    
    needs_update = false;
}

void SVGSprite2D::_draw_sprite() {
    if (svg_resource.is_null()) {
        return;
    }
    
    _update_texture();
    
    if (!texture_rid.is_valid()) {
        return;
    }
    
    Vector2 pos = Vector2();
    if (centered) {
        pos = -draw_size / 2.0;
    }
    
    Rect2 src_rect = Rect2(Vector2(), draw_size);
    Rect2 dst_rect = Rect2(pos, draw_size);
      if (material_override.is_valid()) {
        // Use custom material if available
        RenderingServer::get_singleton()->canvas_item_add_texture_rect_region(get_canvas_item(), dst_rect, texture_rid, src_rect, modulate_color, false, material_override->get_rid());
    } else {
        // Standard texture draw
        RenderingServer::get_singleton()->canvas_item_add_texture_rect_region(get_canvas_item(), dst_rect, texture_rid, src_rect, modulate_color);
    }
}

void SVGSprite2D::set_svg_resource(const Ref<SVGResource> &p_resource) {
    if (svg_resource == p_resource) {
        return;
    }
    
    if (svg_resource.is_valid()) {
        svg_resource->disconnect("changed", callable_mp(this, &SVGSprite2D::force_update));
    }
    
    svg_resource = p_resource;
    
    if (svg_resource.is_valid()) {
        svg_resource->connect("changed", callable_mp(this, &SVGSprite2D::force_update));
    }
    
    needs_update = true;
    queue_redraw();
}

Ref<SVGResource> SVGSprite2D::get_svg_resource() const {
    return svg_resource;
}

void SVGSprite2D::set_symbol_id(const String &p_id) {
    if (symbol_id == p_id) {
        return;
    }
    
    symbol_id = p_id;
    needs_update = true;
    queue_redraw();
}

String SVGSprite2D::get_symbol_id() const {
    return symbol_id;
}

void SVGSprite2D::set_draw_size(const Vector2 &p_size) {
    if (draw_size == p_size) {
        return;
    }
    
    draw_size = p_size;
    needs_update = true;
    queue_redraw();
}

Vector2 SVGSprite2D::get_draw_size() const {
    return draw_size;
}

void SVGSprite2D::set_centered(bool p_centered) {
    if (centered == p_centered) {
        return;
    }
    
    centered = p_centered;
    queue_redraw();
}

bool SVGSprite2D::is_centered() const {
    return centered;
}

void SVGSprite2D::set_modulate(const Color &p_color) {
    if (modulate_color == p_color) {
        return;
    }
    
    modulate_color = p_color;
    queue_redraw();
}

Color SVGSprite2D::get_modulate() const {
    return modulate_color;
}

void SVGSprite2D::set_material_override(const Ref<ShaderMaterial> &p_material) {
    if (material_override == p_material) {
        return;
    }
    
    material_override = p_material;
    queue_redraw();
}

Ref<ShaderMaterial> SVGSprite2D::get_material_override() const {
    return material_override;
}

void SVGSprite2D::force_update() {
    needs_update = true;
    queue_redraw();
}

Rect2 SVGSprite2D::get_rect() const {
    if (centered) {
        return Rect2(-draw_size / 2.0, draw_size);
    } else {
        return Rect2(Vector2(), draw_size);
    }
}
