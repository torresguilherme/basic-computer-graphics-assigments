#version 330

uniform mat4 mvp;

in vec3 position;
in vec2 tex_coord;

out vec3 pixel_position;

void main()
{
    gl_Position = mvp * vec4(position, 1.0);
    pixel_position = gl_Position.xyz;
}