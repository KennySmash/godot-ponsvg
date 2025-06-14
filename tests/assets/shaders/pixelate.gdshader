shader_type canvas_item;

uniform float pixel_size : hint_range(1.0, 50.0) = 8.0;

void fragment() {
    vec2 pixelated_uv = floor(UV * pixel_size) / pixel_size;
    COLOR = texture(TEXTURE, pixelated_uv);
}
