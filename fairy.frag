#version 330 core




in vec3 w_position, w_normal;   // in world coodinates

// light dir, in world coordinates
uniform vec3 light_dir;

// material properties
uniform vec3 k_d = vec3(1,1,1);

// reflection
vec3 r ;



// ambient color constant
vec3 k_a = vec3(1,0,1);

//light color
vec3 k_s = vec3(1,1,1);

//power of light
float s = 10;

// world camera position
uniform vec3 w_camera_position;
uniform vec4 mode;
// view vector
vec3 v = w_camera_position;

uniform sampler2D diffuse_map;
// receiving interpolated color for fragment shader
//in vec3 fragment_color;
in vec2 frag_tex_coord;
// output fragment color for OpenGL
out vec4 out_color;

void main() {



    vec4 tex_color = texture(diffuse_map, frag_tex_coord) - mode;
    //out_color = vec4(fragment_color, 1);
    // out_color = tex_color ;

    vec3 n = normalize(w_normal);
    r = reflect(light_dir,n);
    k_a = tex_color.xyz;
    // out_color = vec4(k_d * max(0, dot(n, light_dir)), 1);
    out_color = vec4(k_a + k_d*max(0,dot(n,light_dir)) + k_s*pow(max(0,dot(r,v)),s),1);
}
