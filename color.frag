#version 330 core

uniform vec4 mode;
//uniform sampler2D diffuse_map;
// receiving interpolated color for fragment shader
in vec3 fragment_color;
//in vec2 frag_tex_coord;
// output fragment color for OpenGL
out vec4 out_color;

void main() {
    //vec4 tex_color = texture(diffuse_map, frag_tex_coord);
    out_color = vec4(fragment_color, 1) -mode;
    //out_color = tex_color;
}
