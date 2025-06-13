def can_build(env, platform):
    """
    Check if the SVG module can be built on the current platform.
    """
    return True

def configure(env):
    """
    Configure build environment for the PonSVG module.
    """
    # Add LunaSVG include directories
    env.Append(CPPPATH=["#modules/ponsvg/src/lunasvg/include"])
    env.Append(CPPPATH=["#modules/ponsvg/src/lunasvg/source"])
    env.Append(CPPPATH=["#modules/ponsvg/src/lunasvg/plutovg/include"])
    env.Append(CPPPATH=["#modules/ponsvg/src/lunasvg/plutovg/source"])    # Add necessary compilation flags
    env.Append(CCFLAGS=["-DLUNASVG_BUILD_STATIC"])
    env.Append(CCFLAGS=["-DPLUTOVG_BUILD_STATIC"])
    env.Append(CCFLAGS=["-DLUNASVG_BUILD"])
    env.Append(CCFLAGS=["-DPLUTOVG_BUILD"])
    
    if env["platform"] == "windows":
        env.Append(CCFLAGS=["-DLUNASVG_STATIC"])
        env.Append(CCFLAGS=["-DPLUTOVG_STATIC"])

    # Handle special compiler flags
    if env["target"] == "debug":
        env.Append(CCFLAGS=["-DSVG_MODULE_DEBUG"])
      # Add LunaSVG source files to build
    lunasvg_sources = [
        "#modules/ponsvg/src/lunasvg/source/lunasvg.cpp",
        "#modules/ponsvg/src/lunasvg/source/svgelement.cpp", 
        "#modules/ponsvg/src/lunasvg/source/svggeometryelement.cpp",
        "#modules/ponsvg/src/lunasvg/source/svglayoutstate.cpp",
        "#modules/ponsvg/src/lunasvg/source/svgpaintelement.cpp",
        "#modules/ponsvg/src/lunasvg/source/svgparser.cpp",
        "#modules/ponsvg/src/lunasvg/source/svgproperty.cpp",
        "#modules/ponsvg/src/lunasvg/source/svgrenderstate.cpp",
        "#modules/ponsvg/src/lunasvg/source/svgtextelement.cpp",
        "#modules/ponsvg/src/lunasvg/source/graphics.cpp",
    ]
      # Add PlutoVG source files
    plutovg_sources = [
        "#modules/ponsvg/src/lunasvg/plutovg/source/plutovg-blend.c",
        "#modules/ponsvg/src/lunasvg/plutovg/source/plutovg-canvas.c",
        "#modules/ponsvg/src/lunasvg/plutovg/source/plutovg-font.c",
        "#modules/ponsvg/src/lunasvg/plutovg/source/plutovg-ft-math.c",
        "#modules/ponsvg/src/lunasvg/plutovg/source/plutovg-ft-raster.c",
        "#modules/ponsvg/src/lunasvg/plutovg/source/plutovg-ft-stroker.c",
        "#modules/ponsvg/src/lunasvg/plutovg/source/plutovg-matrix.c",
        "#modules/ponsvg/src/lunasvg/plutovg/source/plutovg-paint.c",
        "#modules/ponsvg/src/lunasvg/plutovg/source/plutovg-path.c",
        "#modules/ponsvg/src/lunasvg/plutovg/source/plutovg-rasterize.c",
        "#modules/ponsvg/src/lunasvg/plutovg/source/plutovg-surface.c",
    ]
    
    env.add_source_files(env.modules_sources, lunasvg_sources)
    env.add_source_files(env.modules_sources, plutovg_sources)
def get_doc_classes():
    """
    Return a list of documentation classes for this module.
    """
    return [
        "PonSVGResource",
        "PonSVGTexture",
        "PonSVGSprite2D",
    ]

def get_doc_path():
    """
    Return the path to the documentation for this module.
    """
    return "doc_classes"

