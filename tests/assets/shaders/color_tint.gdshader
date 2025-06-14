shader_type canvas_item;

uniform vec4 tint_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float tint_strength : hint_range(0.0, 1.0) = 0.5;

void fragment() {
    vec4 base_color = texture(TEXTURE, UV);
    COLOR = mix(base_color, tint_color * base_color.a, tint_strength);
}
