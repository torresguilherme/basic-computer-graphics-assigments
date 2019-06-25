from OpenGL import GL
from OpenGL.GL import shaders
import pyrr
import numpy as np
import glfw
import pathlib

###############################
### Animation
###############################

class Animation:
    def __init__(self):
        pass

###############################
### MD2 importing
###############################

class MD2Object:
    def __init__(self, filename):
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
    vertex_shader = pathlib.Path('vertex_shader.glsl').read_text()
    fragment_shader = pathlib.Path('fragment_shader.glsl').read_text()

    if not glfw.init():
        return
    window = glfw.create_window(1280, 760, 'Animation', None, None)
    if not window:
        print('Nao foi possivel criar janela')
        glfw.terminate()
        return
    glfw.make_context_current(window)

    GL.glClearColor(0.0, 0.0, 0.0, 1.0)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glCullFace(GL.GL_BACK)

    shader = shaders.compileProgram(shaders.compileShader(vertex_shader, GL.GL_VERTEX_SHADER), shaders.compileShader(fragment_shader, GL.GL_FRAGMENT_SHADER))

    while not glfw.window_should_close(window):
        glfw.poll_events()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        render(window, shader, None)
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()