#version 330 core

// global color variable
uniform vec3 global_color;
uniform sampler2D diffuse_map;
uniform vec4 mode;
uniform vec3 position_fairy;
uniform vec3 w_camera_position;




vec3 light_dir;

// material properties

// reflection
vec3 r ;



// ambient color constant
vec3 k_a = vec3(1,0,1);

//light color
// vec3 k_s = vec3(1,1,1);

//power of light
float s = 1;

//view



// receiving interpolated color for fragment shader
in vec3 fragment_color;
in vec2 frag_tex_coords;
in vec3 position_object;
in vec3 w_normal;

// output fragment color for OpenGL
out vec4 out_color;

void main() {
    vec3 v = normalize(w_camera_position - position_object);
    light_dir = normalize(position_fairy - position_object);
    float d = distance(position_object,position_fairy) ;
    // out_color = vec4((fragment_color + global_color + vec3(0.8, -0.4, 0.75) ), 1);
    //+ vec3(0.7, -0.12, 0.3)
    vec4 tex_color = texture(diffuse_map, frag_tex_coords) - mode;
    vec3 n = normalize(w_normal);
    r = reflect(light_dir,n);
    k_a = tex_color.xyz;
    vec3 k_d = vec3(0.08,0.08,0.08);
    vec3 k_s = vec3(0.01,0.01,0.01);
    if (mode == vec4(0,0,0,0)){
        out_color = tex_color;
    }
    else {
        out_color = vec4(k_a +  ( (1/(d*d))*(k_d*max(0,dot(n,light_dir)) + k_s*pow(max(0,dot(r,v)),s))),1);
    }
}
