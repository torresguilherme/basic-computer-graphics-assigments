#version 330

uniform sampler2D texture0;

in vec3 pixel_position;
in vec2 tex_coord_interpolated;

out vec4 frag_color;

void main()
{
    vec4 albedo = vec4(0.2, 1.0, 1.0, 1.0);
    //vec4 albedo = texture(texture0, tex_coord_interpolated);
    vec3 light_source = vec3(0.0, 1.0, 1.0);

    // flat shading
    vec3 x_tangent = dFdx(pixel_position);
    vec3 y_tangent = dFdy(pixel_position);
    vec3 face_normal = normalize(cross(x_tangent, y_tangent));
    
    float red_diffuse = albedo.r / 3.14 * dot(face_normal, light_source);
    float green_diffuse = albedo.g / 3.14 * dot(face_normal, light_source);
    float blue_diffuse = albedo.b / 3.14 * dot(face_normal, light_source);
    
    red_diffuse = max(0.0, red_diffuse);
    green_diffuse = max(0.0, green_diffuse);
    blue_diffuse = max(0.0, blue_diffuse);
    
    frag_color = vec4(red_diffuse, green_diffuse, blue_diffuse , 1.0);
}