#include "svg_texture.h"
#include "servers/rendering_server.h"

SVGTexture::SVGTexture() {
    render_size = Vector2i(256, 256);
    needs_update = true;
    texture_rid = RenderingServer::get_singleton()->texture_2d_create(Ref<Image>());
}

SVGTexture::~SVGTexture() {
    if (texture_rid.is_valid()) {
        RenderingServer::get_singleton()->free_rid(texture_rid);
    }
}

void SVGTexture::_bind_methods() {
    ClassDB::bind_method(D_METHOD("set_svg_resource", "resource"), &SVGTexture::set_svg_resource);
    ClassDB::bind_method(D_METHOD("get_svg_resource"), &SVGTexture::get_svg_resource);
    
    ClassDB::bind_method(D_METHOD("set_render_size", "size"), &SVGTexture::set_render_size);
    ClassDB::bind_method(D_METHOD("get_render_size"), &SVGTexture::get_render_size);
    
    ClassDB::bind_method(D_METHOD("force_update"), &SVGTexture::force_update);
    
    ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "svg_resource", PROPERTY_HINT_RESOURCE_TYPE, "SVGResource"), "set_svg_resource", "get_svg_resource");
    ADD_PROPERTY(PropertyInfo(Variant::VECTOR2I, "render_size"), "set_render_size", "get_render_size");
}

void SVGTexture::_update_image() {
    if (!needs_update || svg_resource.is_null()) {
        return;
    }
    
    cached_image = svg_resource->rasterize_full(render_size);
    
    if (cached_image.is_valid()) {
        RenderingServer::get_singleton()->texture_2d_update(texture_rid, cached_image);
    }
    
    needs_update = false;
}

int SVGTexture::get_width() const {
    return render_size.x;
}

int SVGTexture::get_height() const {
    return render_size.y;
}

RID SVGTexture::get_rid() const {
    const_cast<SVGTexture*>(this)->_update_image();
    return texture_rid;
}

bool SVGTexture::has_alpha() const {
    return true; // SVGs typically have alpha
}

Ref<Image> SVGTexture::get_image() const {
    const_cast<SVGTexture*>(this)->_update_image();
    return cached_image;
}

void SVGTexture::set_svg_resource(const Ref<SVGResource> &p_resource) {
    if (svg_resource == p_resource) {
        return;
    }
    
    if (svg_resource.is_valid()) {
        svg_resource->disconnect("changed", callable_mp(this, &SVGTexture::force_update));
    }
    
    svg_resource = p_resource;
    
    if (svg_resource.is_valid()) {
        svg_resource->connect("changed", callable_mp(this, &SVGTexture::force_update));
    }
    
    needs_update = true;
    emit_changed();
}

Ref<SVGResource> SVGTexture::get_svg_resource() const {
    return svg_resource;
}

void SVGTexture::set_render_size(const Vector2i &p_size) {
    if (render_size == p_size) {
        return;
    }
    
    render_size = p_size;
    needs_update = true;
    emit_changed();
}

Vector2i SVGTexture::get_render_size() const {
    return render_size;
}

void SVGTexture::force_update() {
    needs_update = true;
    emit_changed();
}
