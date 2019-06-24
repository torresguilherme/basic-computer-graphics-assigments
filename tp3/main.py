import OpenGL.GL
import OpenGL.GL.shaders
import pyrr
import numpy as np
import glfw
import pathlib

###############################
### MD2 importing
###############################

class MD2Object:
    def __init__(self, filename):
        pass

###############################
### Animation
###############################

class Animation:
    def __init__(self):
        pass

###############################
### Renderer
###############################

def render(window, shader, object):
    pass

###############################
### MAIN
###############################

def main():
    vertex_shader_source = pathlib.Path('vertex_shader.glsl').read_text()
    fragment_shader_source = pathlib.Path('fragment_shader.glsl').read_text()

if __name__ == "__main__":
    main()