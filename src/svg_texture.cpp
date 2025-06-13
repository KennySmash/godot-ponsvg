#include "svg_texture.h"
#include "servers/rendering_server.h"

PonSVGTexture::PonSVGTexture() {
    render_size = Vector2i(256, 256);
    needs_update = true;
    texture_rid = RenderingServer::get_singleton()->texture_2d_create(Ref<Image>());
}

PonSVGTexture::~PonSVGTexture() {
    if (texture_rid.is_valid()) {
        RenderingServer::get_singleton()->free_rid(texture_rid);
    }
}

void PonSVGTexture::_bind_methods() {
    ClassDB::bind_method(D_METHOD("set_svg_resource", "resource"), &PonSVGTexture::set_svg_resource);
    ClassDB::bind_method(D_METHOD("get_svg_resource"), &PonSVGTexture::get_svg_resource);
    
    ClassDB::bind_method(D_METHOD("set_render_size", "size"), &PonSVGTexture::set_render_size);
    ClassDB::bind_method(D_METHOD("get_render_size"), &PonSVGTexture::get_render_size);
    
    ClassDB::bind_method(D_METHOD("force_update"), &PonSVGTexture::force_update);
    
    ADD_PROPERTY(PropertyInfo(Variant::OBJECT, "ponsvg_resource", PROPERTY_HINT_RESOURCE_TYPE, "PonSVGResource"), "set_ponsvg_resource", "get_ponsvg_resource");
    ADD_PROPERTY(PropertyInfo(Variant::VECTOR2I, "render_size"), "set_render_size", "get_render_size");
}

void PonSVGTexture::_update_image() {
    if (!needs_update || svg_resource.is_null()) {
        return;
    }
    
    cached_image = svg_resource->rasterize_full(render_size);
    
    if (cached_image.is_valid()) {
        RenderingServer::get_singleton()->texture_2d_update(texture_rid, cached_image);
    }
    
    needs_update = false;
}

int PonSVGTexture::get_width() const {
    return render_size.x;
}

int PonSVGTexture::get_height() const {
    return render_size.y;
}

RID PonSVGTexture::get_rid() const {
    const_cast<PonSVGTexture*>(this)->_update_image();
    return texture_rid;
}

bool PonSVGTexture::has_alpha() const {
    return true; // SVGs typically have alpha
}

Ref<Image> PonSVGTexture::get_image() const {
    const_cast<PonSVGTexture*>(this)->_update_image();
    return cached_image;
}

void PonSVGTexture::set_ponsvg_resource(const Ref<PonSVGResource> &p_resource) {
    if (svg_resource == p_resource) {
        return;
    }
    
    if (svg_resource.is_valid()) {
        svg_resource->disconnect("changed", callable_mp(this, &PonSVGTexture::force_update));
    }
    
    svg_resource = p_resource;
    
    if (svg_resource.is_valid()) {
        svg_resource->connect("changed", callable_mp(this, &PonSVGTexture::force_update));
    }
    
    needs_update = true;
    emit_changed();
}

Ref<PonSVGResource> PonSVGTexture::get_ponsvg_resource() const {
    return svg_resource;
}

void PonSVGTexture::set_render_size(const Vector2i &p_size) {
    if (render_size == p_size) {
        return;
    }
    
    render_size = p_size;
    needs_update = true;
    emit_changed();
}

Vector2i PonSVGTexture::get_render_size() const {
    return render_size;
}

void PonSVGTexture::force_update() {
    needs_update = true;
    emit_changed();
}

