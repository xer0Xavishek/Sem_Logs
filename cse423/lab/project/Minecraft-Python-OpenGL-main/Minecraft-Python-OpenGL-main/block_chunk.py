from block import Block
from OpenGL.GL import *
import numpy as np
from object import vertex_data_dtype

CHUNK_X_SIZE = 16
CHUNK_Y_SIZE = 1
CHUNK_Z_SIZE = 16

class Chunk:
    def __init__(self, coord):
        self.coord = coord
        
        self.blocks = {}

        self.__create_blocks__()

        self.loaded = False

    def __del__ (self):
        glDeleteVertexArrays(1, [self.obj_vao])
        glDeleteBuffers(1, [self.obj_vbo])

    def __create_blocks__(self):
        for x in range(CHUNK_X_SIZE):
            for z in range(CHUNK_Z_SIZE):
                for y in range(z + 1):
                    block_x = self.coord[0] * CHUNK_X_SIZE + x
                    block_y = y
                    block_z = self.coord[1] * CHUNK_Z_SIZE + z
        
                    self.blocks[(block_x, block_y, block_z)] = Block((block_x, block_y, block_z))

    def __stack_blocks_vertices__(self, blocks):
        vertices = None

        for block in blocks.values():
            if vertices is None:
                vertices = block.getVertices(blocks)
                continue
            
            vertices = np.concatenate((vertices, block.getVertices(blocks)))

        return vertices, vertices.shape[0]

    def load(self, program):
        if self.loaded:
            return
        
        self.obj_vao = glGenVertexArrays(1)
        glBindVertexArray(self.obj_vao)

        vertices, self.nvertices = self.__stack_blocks_vertices__(self.blocks)

        self.obj_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.obj_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        locationPositionAttrib = glGetAttribLocation(program, "aPosition")
        glVertexAttribPointer(locationPositionAttrib, 3, GL_FLOAT, GL_FALSE, vertex_data_dtype.itemsize, ctypes.c_void_p(vertex_data_dtype.fields['position'][1]))
        glEnableVertexAttribArray(0)

        locationTextureAttrib = glGetAttribLocation(program, "aTexCoord")
        glVertexAttribPointer(locationTextureAttrib, 2, GL_FLOAT, GL_FALSE, vertex_data_dtype.itemsize, ctypes.c_void_p(vertex_data_dtype.fields['texture'][1]))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)

        self.loaded = True

    def draw(self):
        if not self.loaded:
            return

        glBindVertexArray(self.obj_vao)
        glDrawArrays(GL_QUADS, 0, self.nvertices)
        glBindVertexArray(0)
