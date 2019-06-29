from OpenGL import GL
from OpenGL.GL import shaders
import pyrr
import numpy as np
import glfw
import pathlib
import struct
import ctypes
from PIL import Image

WIDTH = 1280
HEIGHT = 760

###############################
### Animation
###############################

class AnimationState:
    def __init__(self,
        start_frame,
        end_frame,
        fps,
        curr_time,
        old_time,
        interpol,
        anim_type,
        curr_frame,
        next_frame):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.fps = fps

        self.curr_time = curr_time
        self.old_time = old_time
        self.interpol = interpol

        self.type = anim_type
        
        self.curr_frame = curr_frame
        self.next_frame = next_frame

class Animation:
    def __init__(self, first_frame, last_frame, fps):
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.fps = fps

###############################
### MD2 importing
###############################

class MD2Object:
    def __init__(self, filename, texture_file, shader):
        self.shader = shader
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
                self.tex_coords.append(int.from_bytes(f.read(2), byteorder='little')/self.skinwidth)
                self.tex_coords.append(int.from_bytes(f.read(2), byteorder='little')/self.skinheight)

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
                    scale.append(struct.unpack('f', buffer[offset:offset + 4])[0])
                    offset += 4
                for j in range(3):
                    translate.append(struct.unpack('f', buffer[offset:offset + 4])[0])
                    offset += 4
                self.frame_names.append(buffer[offset:offset + 16].decode())
                offset += 16
                for j in range(self.num_vertices):
                    for k in range(3):
                        self.vertices[i].append(int.from_bytes(buffer[offset:offset + 1], byteorder='little') * scale[k] + translate[k])
                        offset += 1
                    self.normal_indices[i].append(int.from_bytes(buffer[offset:offset + 1], byteorder='little'))
                    offset += 1

        # make vertex array and buffers
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        GL.glUseProgram(self.shader)

        self.vertex_bos = GL.glGenBuffers(self.num_frames)
        for i in range(self.num_frames):
            vertices_i = np.array(self.vertices[i], dtype=np.float32)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_bos[i])
            GL.glBufferData(GL.GL_ARRAY_BUFFER, len(self.vertices[i]) * 4, vertices_i, GL.GL_STATIC_DRAW)

        self.vertex_index_bo = GL.glGenBuffers(1)
        vertex_indices = np.array(self.vertex_indices, dtype=np.uint32)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.vertex_index_bo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(self.vertex_indices) * 4, vertex_indices, GL.GL_STATIC_DRAW)

        self.tex_coord_bo = GL.glGenBuffers(1)
        tex_coords = np.array(self.tex_coords, dtype=np.float32)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.tex_coord_bo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(self.tex_coords) * 4, tex_coords, GL.GL_STATIC_DRAW)

        self.tex_coord_index_bo = GL.glGenBuffers(1)
        tex_coord_indices = np.array(self.tex_coord_indices, dtype=np.uint32)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.tex_coord_index_bo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(self.tex_coord_indices) * 4, tex_coord_indices, GL.GL_STATIC_DRAW)

        # load texture and make buffer
        texture = Image.open(texture_file).convert('RGBA').transpose(Image.FLIP_TOP_BOTTOM)
        ix, iy, image = texture.size[0], texture.size[1], np.frombuffer(texture.tobytes('raw', 'RGBA'), dtype=np.uint8)
        self.texture_buffer = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_buffer)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT,1)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, ix, iy, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

        # to do: calculate and make normals buffer
    
    def render(self):
        # to do: animated rendering
        GL.glBindVertexArray(self.vao)
        
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_bos[0])
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 0, ctypes.c_void_p(0))

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.tex_coord_bo)
        GL.glEnableVertexAttribArray(2)
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, False, 0, ctypes.c_void_p(0))

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.vertex_index_bo)
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.vertex_indices), GL.GL_UNSIGNED_INT, None)
        GL.glBindVertexArray(0)

###############################
### Renderer
###############################

def render(shape):
    GL.glUseProgram(shape.shader)
    model_matrix = pyrr.Matrix44.from_scale((1/75, 1/75, 1/75)) * pyrr.Matrix44.from_x_rotation(90) * pyrr.Matrix44.from_z_rotation(90)
    view_matrix = pyrr.Matrix44.look_at((1, 1, 1), (0, 0, 0), (0, 1, 0))
    projection_matrix = pyrr.Matrix44.perspective_projection(45, WIDTH/HEIGHT, 0.001, 1000)
    mvp_matrix = projection_matrix * view_matrix * model_matrix
    mvp_loc = GL.glGetUniformLocation(shape.shader, 'mvp')
    GL.glUniformMatrix4fv(mvp_loc, 1, GL.GL_FALSE, mvp_matrix)

    shape.render()

###############################
### MAIN
###############################

def main():
    print('initializing glfw')
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    window = glfw.create_window(WIDTH, HEIGHT, 'Animation', None, None)
    if not window:
        print('Nao foi possivel criar janela')
        glfw.terminate()
        return
    glfw.make_context_current(window)

    print('reading shaders')
    vertex_shader = pathlib.Path('vertex_shader.glsl').read_text()
    fragment_shader = pathlib.Path('fragment_shader.glsl').read_text()

    print('compiling shaders')
    shader = shaders.compileProgram(shaders.compileShader(vertex_shader, GL.GL_VERTEX_SHADER), shaders.compileShader(fragment_shader, GL.GL_FRAGMENT_SHADER))

    print('reading object')
    shape = MD2Object('models/dragon.md2', 'models/dragon.png', shader)

    GL.glClearColor(0.2, 0.2, 0.2, 1.0)
    GL.glEnable(GL.GL_DEPTH_TEST)
    #GL.glCullFace(GL.GL_BACK)

    print('everything ready to render. rendering...')
    while not glfw.window_should_close(window):
        glfw.poll_events()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        render(shape)
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()