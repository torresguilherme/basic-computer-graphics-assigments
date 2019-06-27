from OpenGL import GL
from OpenGL.GL import shaders
import pyrr
import numpy as np
import glfw
import pathlib
import struct

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
    def __init__(self, filename, texture):
        with open(filename, 'rb') as f:
            ### READING HEADER
            ident = f.read(4)
            if ident != 'IDP2'.encode('ascii'):
                print("Nao é um arquivo MD2, numero mágico é: " + ident.decode())
                return
            self.version = int.from_bytes(f.read(4), byteorder='little') # 8
            if self.version != 8:
                print("Versao do arquivo nao bate: " + self.version)
                return

            self.skinwidth = int.from_bytes(f.read(4), byteorder='little') # width of texture
            self.skinheight = int.from_bytes(f.read(4), byteorder='little') # height of texture
            self.framesize = int.from_bytes(f.read(4), byteorder='little') # size of one frame in bytes

            self.num_skins = int.from_bytes(f.read(4), byteorder='little') # number of textures
            self.num_vertices = int.from_bytes(f.read(4), byteorder='little') # number of vertices
            self.num_tex_coords = int.from_bytes(f.read(4), byteorder='little') # number of texture coordinates
            self.num_tris = int.from_bytes(f.read(4), byteorder='little') # number of triangles
            self.num_commands = int.from_bytes(f.read(4), byteorder='little') # number of opengl commands
            self.num_frames = int.from_bytes(f.read(4), byteorder='little') # total number of frames

            self.ofs_skins = int.from_bytes(f.read(4), byteorder='little') # offset to skin names (64 bytes each)
            self.ofs_st = int.from_bytes(f.read(4), byteorder='little') # offset to s-t texture coordinates
            self.ofs_tris = int.from_bytes(f.read(4), byteorder='little') # offset to triangles
            self.ofs_frames = int.from_bytes(f.read(4), byteorder='little') # offset to frame data
            self.ofs_glcmds = int.from_bytes(f.read(4), byteorder='little') # offset to opengl commands
            self.ofs_end = int.from_bytes(f.read(4), byteorder='little') # offset to end of file

            # READING CONTENTS
            self.skin_names = []
            for i in range(self.num_skins):
                self.skin_names.append(f.read(64).decode())
            
            self.tex_coords = []
            for i in range(self.num_tex_coords):
                for j in range(2):
                    self.tex_coords.append(int.from_bytes(f.read(2), byteorder='little'))
            
            self.vertex_indices = []
            self.tex_coord_indices = []
            for i in range(self.num_tris):
                for k in range(3):
                    self.vertex_indices.append(int.from_bytes(f.read(2), byteorder='little'))
                for k in range(3):
                    self.tex_coord_indices.append(int.from_bytes(f.read(2), byteorder='little'))

            # frame data
            self.frame_names = []
            self.vertices = []
            self.normal_indices = []
            for i in range(self.num_frames):
                self.vertices.append([])
                self.normal_indices.append([])
                buffer = f.read(self.framesize)
                scale = []
                translate = []
                offset = 0
                for j in range(3):
                    scale.append(struct.unpack('f', buffer[offset:offset + 4]))
                    offset += 4
                for j in range(3):
                    translate.append(struct.unpack('f', buffer[offset:offset + 4]))
                    offset += 4
                self.frame_names.append(buffer[offset:offset + 16].decode())
                offset += 16
                for j in range(self.num_vertices):
                    for k in range(3):
                        self.vertices[i].append(int.from_bytes(buffer[offset:offset + 1], byteorder='little') * scale[k] + translate[k])
                        offset += 1
                    self.normal_indices[i].append(int.from_bytes(buffer[offset:offset + 1], byteorder='little'))
                    offset += 1

###############################
### Renderer
###############################

def render(window, shader, shape):
    pass

###############################
### MAIN
###############################

def main():
    vertex_shader = pathlib.Path('vertex_shader.glsl').read_text()
    fragment_shader = pathlib.Path('fragment_shader.glsl').read_text()

    shape = MD2Object('models/dragon.md2', 'models/dragon.png')

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
        render(window, shader, shape)
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()