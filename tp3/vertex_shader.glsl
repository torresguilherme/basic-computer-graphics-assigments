#version 330

uniform mat4 mvp;

in vec3 position;
in vec2 tex_coord;

void main()
{
    gl_Position = mvp * vec4(position, 1.0);
}