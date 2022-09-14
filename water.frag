#version 330 core

uniform sampler2D diffuse_map;
uniform vec4 mode;
// receiving interpolated color for fragment shader
in vec3 fragment_color;
in vec2 frag_tex_coord;
// output fragment color for OpenGL
out vec4 out_color;

void main() {
    vec3 tex_color = vec3(texture(diffuse_map, frag_tex_coord));
    // out_color = vec4(fragment_color, 0.5);
    out_color = vec4(tex_color, 0.7) - mode;
}
