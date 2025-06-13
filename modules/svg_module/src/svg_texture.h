#ifndef SVG_TEXTURE_H
#define SVG_TEXTURE_H

#include "scene/resources/texture.h"
#include "svg_resource.h"

class SVGTexture : public Texture2D {
    GDCLASS(SVGTexture, Texture2D);

private:
    Ref<SVGResource> svg_resource;
    Vector2i render_size;
    Ref<Image> cached_image;
    bool needs_update;
    
    void _update_image();

protected:
    static void _bind_methods();

public:
    SVGTexture();
    ~SVGTexture();

    // Texture2D interface
    virtual int get_width() const override;
    virtual int get_height() const override;
    virtual RID get_rid() const override;
    virtual bool has_alpha() const override;
    virtual Ref<Image> get_image() const override;

    // SVG-specific methods
    void set_svg_resource(const Ref<SVGResource> &p_resource);
    Ref<SVGResource> get_svg_resource() const;
    
    void set_render_size(const Vector2i &p_size);
    Vector2i get_render_size() const;
    
    void force_update();

private:
    RID texture_rid;
};

#endif // SVG_TEXTURE_H
