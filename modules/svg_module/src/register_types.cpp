#include "register_types.h"

#include "core/object/class_db.h"
#include "svg_resource.h"
#include "svg_texture.h"
#include "svg_sprite.h"

void initialize_svg_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
        return;
    }

    GDREGISTER_CLASS(SVGResource);
    GDREGISTER_CLASS(SVGTexture);
    GDREGISTER_CLASS(SVGSprite2D);
}

void uninitialize_svg_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
        return;
    }
}
