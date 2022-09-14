#version 330 core
out vec4 Color;

in vec3 TexCoords;

uniform samplerCube skybox;
uniform vec4 mode;

void main()
{    
    Color = texture(skybox, TexCoords) - mode;
}