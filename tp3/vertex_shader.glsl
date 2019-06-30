#version 330

uniform mat4 mvp;
uniform float interpolator;

layout (location=0) in vec3 position;
layout (location=1) in vec3 position1;
layout (location=2) in vec2 tex_coord;

out vec3 pixel_position;
out vec2 tex_coord_interpolated;

void main()
{
    vec3 real_position = mix(position, position1, interpolator);
    gl_Position = mvp * vec4(real_position, 1.0);
    pixel_position = gl_Position.xyz;
    tex_coord_interpolated = tex_coord;
}