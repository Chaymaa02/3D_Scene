#version 330 core
in vec3 position;

out vec3 TexCoords;

uniform mat4 projection;
uniform mat4 view;


void main()
{
    mat4 view_t = mat4(mat3(view)); //view without translation
    TexCoords = position;
    gl_Position = projection * view_t * vec4(position, 1.0);
}