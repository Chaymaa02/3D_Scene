#version 330 core

// global color
uniform vec3 global_color;


// ---- skinning globals and attributes



// input attribute variable, given per vertex
in vec3 position;
in vec3 color;
in vec3 normal;

// global matrix variables
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;



//texture
// in vec2 tex_coord;

// interpolated color for fragment shader, intialized at vertices
out vec3 fragment_color;
out vec2 frag_tex_coord;


void main() {

    // initialize interpolated colors at vertices
    fragment_color = color + normal + global_color;
    frag_tex_coord = position.xz;

    // tell OpenGL how to transform the vertex to clip coordinates
    gl_Position = projection * view * model * vec4(position, 1);
}
