#ifndef PONSVG_TEXTURE_H
#define PONSVG_TEXTURE_H

#include <godot_cpp/classes/texture2d.hpp>

using namespace godot;
#include "svg_resource.h"

class PonSVGTexture : public Texture2D {
    GDCLASS(PonSVGTexture, Texture2D);

private:
    Ref<PonSVGResource> svg_resource;
    Vector2i render_size;
    Ref<Image> cached_image;
    bool needs_update;
    
    void _update_image();

protected:
    static void _bind_methods();

public:
    PonSVGTexture();
    ~PonSVGTexture();    // Texture2D interface
    virtual int32_t _get_width() const override;
    virtual int32_t _get_height() const override;
    virtual bool _has_alpha() const override;// PonSVG-specific methods
    void set_ponsvg_resource(const Ref<PonSVGResource> &p_resource);
    Ref<PonSVGResource> get_ponsvg_resource() const;
    
    void set_render_size(const Vector2i &p_size);
    Vector2i get_render_size() const;
    
    void force_update();

private:
    RID texture_rid;
};

#endif // PONSVG_TEXTURE_H

