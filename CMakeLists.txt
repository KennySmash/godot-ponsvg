cmake_minimum_required(VERSION 3.20)

project(ponsvg VERSION 1.0.0 LANGUAGES CXX C)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Platform detection
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(TARGET_PATH x86_64)
    set(TARGET_NAME libponsvg.linux.template_${CMAKE_BUILD_TYPE}.${TARGET_PATH}.so)
elseif(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(TARGET_PATH x86_64)
    else()
        set(TARGET_PATH x86_32)
    endif()
    set(TARGET_NAME libponsvg.windows.template_${CMAKE_BUILD_TYPE}.${TARGET_PATH}.dll)
elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    set(TARGET_PATH universal)
    set(TARGET_NAME libponsvg.macos.template_${CMAKE_BUILD_TYPE}.${TARGET_PATH}.dylib)
endif()

# Find godot-cpp
find_package(PkgConfig QUIET)
set(GODOT_CPP_SYSTEM_HEADERS ON CACHE BOOL "Treat godot-cpp headers as system headers (suppress warnings)")

# Try to find godot-cpp in common locations
set(GODOT_CPP_PATHS
    "${CMAKE_CURRENT_SOURCE_DIR}/godot-cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/libs/godot-cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/../godot-cpp"
)

foreach(path ${GODOT_CPP_PATHS})
    if(EXISTS "${path}/CMakeLists.txt")
        set(GODOT_CPP_PATH ${path})
        break()
    endif()
endforeach()

if(NOT GODOT_CPP_PATH)
    message(FATAL_ERROR "godot-cpp not found. Please run: git submodule update --init --recursive")
endif()

# Add godot-cpp
add_subdirectory(${GODOT_CPP_PATH} godot-cpp)

# Add our extension
add_library(${PROJECT_NAME} SHARED)

# Define source files
set(PONSVG_SOURCES
    src/register_types.cpp
    src/svg_resource.cpp
    src/svg_texture.cpp
    src/svg_sprite.cpp
    src/lunasvg_integration.cpp
)

# Add LunaSVG sources
set(LUNASVG_SOURCES
    modules/ponsvg/src/lunasvg/source/lunasvg.cpp
    modules/ponsvg/src/lunasvg/source/graphics.cpp
    modules/ponsvg/src/lunasvg/source/svgelement.cpp
    modules/ponsvg/src/lunasvg/source/svggeometryelement.cpp
    modules/ponsvg/src/lunasvg/source/svglayoutstate.cpp
    modules/ponsvg/src/lunasvg/source/svgpaintelement.cpp
    modules/ponsvg/src/lunasvg/source/svgparser.cpp
    modules/ponsvg/src/lunasvg/source/svgproperty.cpp
    modules/ponsvg/src/lunasvg/source/svgrenderstate.cpp
    modules/ponsvg/src/lunasvg/source/svgtextelement.cpp
)

# Add PlutoVG sources
set(PLUTOVG_SOURCES
    modules/ponsvg/src/lunasvg/plutovg/source/plutovg-blend.c
    modules/ponsvg/src/lunasvg/plutovg/source/plutovg-canvas.c
    modules/ponsvg/src/lunasvg/plutovg/source/plutovg-font.c
    modules/ponsvg/src/lunasvg/plutovg/source/plutovg-ft-math.c
    modules/ponsvg/src/lunasvg/plutovg/source/plutovg-ft-raster.c
    modules/ponsvg/src/lunasvg/plutovg/source/plutovg-ft-stroker.c
    modules/ponsvg/src/lunasvg/plutovg/source/plutovg-matrix.c
    modules/ponsvg/src/lunasvg/plutovg/source/plutovg-paint.c
    modules/ponsvg/src/lunasvg/plutovg/source/plutovg-path.c
    modules/ponsvg/src/lunasvg/plutovg/source/plutovg-rasterize.c
    modules/ponsvg/src/lunasvg/plutovg/source/plutovg-surface.c
)

# Set target sources
target_sources(${PROJECT_NAME} PRIVATE
    ${PONSVG_SOURCES}
    ${LUNASVG_SOURCES}
    ${PLUTOVG_SOURCES}
)

# Include directories
target_include_directories(${PROJECT_NAME} PRIVATE
    src/
    modules/ponsvg/src/
    modules/ponsvg/src/lunasvg/include/
    modules/ponsvg/src/lunasvg/source/
    modules/ponsvg/src/lunasvg/plutovg/include/
    modules/ponsvg/src/lunasvg/plutovg/source/
)

# Link godot-cpp
target_link_libraries(${PROJECT_NAME} PRIVATE godot::cpp)

# Compiler definitions
target_compile_definitions(${PROJECT_NAME} PRIVATE
    LUNASVG_BUILD_STATIC
    PLUTOVG_BUILD_STATIC
    LUNASVG_BUILD
    PLUTOVG_BUILD
)

# Platform-specific settings
if(WIN32)
    target_compile_definitions(${PROJECT_NAME} PRIVATE
        LUNASVG_STATIC
        PLUTOVG_STATIC
        WIN32_LEAN_AND_MEAN
        NOMINMAX
    )
    
    # Link math library on Windows if using MinGW
    if(MINGW)
        target_link_libraries(${PROJECT_NAME} PRIVATE m)
    endif()
    
elseif(UNIX AND NOT APPLE)
    target_link_libraries(${PROJECT_NAME} PRIVATE m)
    target_compile_options(${PROJECT_NAME} PRIVATE -fPIC)
    
elseif(APPLE)
    target_compile_options(${PROJECT_NAME} PRIVATE -fPIC)
    
    # Set macOS deployment target
    set_target_properties(${PROJECT_NAME} PROPERTIES
        MACOSX_DEPLOYMENT_TARGET "10.15"
    )
endif()

# Build type specific settings
if(CMAKE_BUILD_TYPE MATCHES Debug)
    target_compile_definitions(${PROJECT_NAME} PRIVATE
        DEBUG_ENABLED
        SVG_MODULE_DEBUG
    )
else()
    target_compile_definitions(${PROJECT_NAME} PRIVATE
        NDEBUG
    )
    
    # Optimization for release
    if(NOT WIN32)
        target_compile_options(${PROJECT_NAME} PRIVATE -O3)
    endif()
endif()

# Set output name and directory
set_target_properties(${PROJECT_NAME} PROPERTIES
    OUTPUT_NAME ${TARGET_NAME}
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin"
)

# Copy the extension file to output
configure_file(ponsvg.gdextension "${CMAKE_SOURCE_DIR}/bin/ponsvg.gdextension" COPYONLY)

# Post-build message
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E echo "✅ PonSVG GDExtension built: ${TARGET_NAME}"
    COMMAND ${CMAKE_COMMAND} -E echo "📁 Output directory: ${CMAKE_SOURCE_DIR}/bin"
)

# Install configuration
install(TARGETS ${PROJECT_NAME}
    LIBRARY DESTINATION bin
    RUNTIME DESTINATION bin
)

install(FILES ponsvg.gdextension
    DESTINATION .
)
