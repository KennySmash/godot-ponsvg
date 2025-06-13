def can_build(env, platform):
    """
    Check if the SVG module can be built on the current platform.
    """
    return True

def configure(env):
    """
    Configure build environment for the SVG module.
    """
    # Add LunaSVG include directories
    env.Append(CPPPATH=["#modules/svg_module/src/lunasvg/include"])
    env.Append(CPPPATH=["#modules/svg_module/src/lunasvg/source"])
    env.Append(CPPPATH=["#modules/svg_module/src/lunasvg/plutovg/include"])
    env.Append(CPPPATH=["#modules/svg_module/src/lunasvg/plutovg/source"])

    # Add necessary compilation flags
    env.Append(CCFLAGS=["-DLUNASVG_BUILD_STATIC"])
    
    if env["platform"] == "windows":
        env.Append(CCFLAGS=["-DLUNASVG_STATIC"])

    # Handle special compiler flags
    if env["target"] == "debug":
        env.Append(CCFLAGS=["-DSVG_MODULE_DEBUG"])
    
    # Add LunaSVG source files to build
    lunasvg_sources = [
        "#modules/svg_module/src/lunasvg/source/lunasvg.cpp",
        "#modules/svg_module/src/lunasvg/source/svgelement.cpp", 
        "#modules/svg_module/src/lunasvg/source/svggeometryelement.cpp",
        "#modules/svg_module/src/lunasvg/source/svglayoutstate.cpp",
        "#modules/svg_module/src/lunasvg/source/svgpaintelement.cpp",
        "#modules/svg_module/src/lunasvg/source/svgparser.cpp",
        "#modules/svg_module/src/lunasvg/source/svgproperty.cpp",
        "#modules/svg_module/src/lunasvg/source/svgrenderstate.cpp",
        "#modules/svg_module/src/lunasvg/source/svgtextelement.cpp",
        "#modules/svg_module/src/lunasvg/source/graphics.cpp",
    ]
      # Add PlutoVG source files
    plutovg_sources = [
        "#modules/svg_module/src/lunasvg/plutovg/source/plutovg-blend.c",
        "#modules/svg_module/src/lunasvg/plutovg/source/plutovg-canvas.c",
        "#modules/svg_module/src/lunasvg/plutovg/source/plutovg-font.c",
        "#modules/svg_module/src/lunasvg/plutovg/source/plutovg-ft-math.c",
        "#modules/svg_module/src/lunasvg/plutovg/source/plutovg-ft-raster.c",
        "#modules/svg_module/src/lunasvg/plutovg/source/plutovg-ft-stroker.c",
        "#modules/svg_module/src/lunasvg/plutovg/source/plutovg-matrix.c",
        "#modules/svg_module/src/lunasvg/plutovg/source/plutovg-paint.c",
        "#modules/svg_module/src/lunasvg/plutovg/source/plutovg-path.c",
        "#modules/svg_module/src/lunasvg/plutovg/source/plutovg-rasterize.c",
        "#modules/svg_module/src/lunasvg/plutovg/source/plutovg-surface.c",
    ]
    
    env.add_source_files(env.modules_sources, lunasvg_sources)
    env.add_source_files(env.modules_sources, plutovg_sources)
def get_doc_classes():
    """
    Return a list of documentation classes for this module.
    """
    return [
        "SVGResource",
        "SVGTexture",
        "SVGSprite2D",
    ]

def get_doc_path():
    """
    Return the path to the documentation for this module.
    """
    return "doc_classes"

