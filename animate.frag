#version 330 core

uniform sampler2D diffuse_map;
uniform vec4 mode;

in vec2 frag_tex_coords;

out vec4 out_color;

void main() {
    vec4 tex_color = texture(diffuse_map, frag_tex_coords);
    out_color = tex_color - mode;
}