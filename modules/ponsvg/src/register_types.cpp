#include "register_types.h"

#include "core/object/class_db.h"
#include "svg_resource.h"
#include "svg_texture.h"
#include "svg_sprite.h"

void initialize_ponsvg_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
        return;
    }

    GDREGISTER_CLASS(PonPonSVGResource);
    GDREGISTER_CLASS(PonPonSVGTexture);
    GDREGISTER_CLASS(PonPonSVGSprite2D);
}

void uninitialize_ponsvg_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
        return;
    }
}
