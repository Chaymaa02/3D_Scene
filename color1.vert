#version 330 core

// input attribute variable, given per vertex
in vec3 position;
in vec3 color;

// global matrix variables
uniform mat4 view;
uniform mat4 projection;
uniform mat4 model;

// interpolated color for fragment shader, intialized at vertices
out vec3 fragment_color;
out vec2 frag_tex_coords;
out vec3 position_object;
out vec3 w_normal ;

void main() {
    // initialize interpolated colors at vertices
    position_object = position;
    fragment_color = color;
    frag_tex_coords = position.xz;
    w_normal = color;

    // tell OpenGL how to transform the vertex to clip coordinates
    gl_Position = projection * view * model * vec4(position, 1);
}
