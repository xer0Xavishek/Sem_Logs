import numpy as np
from object import Object, vertex_data_dtype
from OpenGL.GL import *
from PIL import Image
from block_chunk import Chunk, CHUNK_X_SIZE, CHUNK_Z_SIZE

TEXTURE_ATLAS_PATH = 'assets/texture_atlas.png'

RENDER_DISTANCE = 2

class World(Object):

    def __init__(self):
        super().__init__()

        self.chunks = {}

        self.central_chunk = (0, 0)

        self.__create_chunks__(self.central_chunk, RENDER_DISTANCE)

    def __create_chunks__(self, central_chunk, render_distance):
        central_chunk_x, central_chunk_z = central_chunk
        for x in range(-render_distance, render_distance):
            for z in range(-render_distance, render_distance):
                if (central_chunk_x + x, central_chunk_z + z) not in self.chunks:
                    self.chunks[(central_chunk_x + x, central_chunk_z + z)] = Chunk((central_chunk_x + x, central_chunk_z + z))

    def __load_chunks__(self, program):
        for chunk in self.chunks.values():
            chunk.load(program)

    def __get_camera_coord__(self, camera):
        camera_coord = np.array(camera.get_position())
        
        camera_x, _, camera_z = camera_coord // CHUNK_X_SIZE

        return (camera_x, camera_z)

    def __unload_extra_chunks__(self, central_chunk, render_distance):
        central_chunk_x, central_chunk_z = central_chunk
        for chunk in list(self.chunks.keys()):
            chunk_x, chunk_z = chunk
            if (abs(chunk_x - central_chunk_x) > render_distance) or (abs(chunk_z - central_chunk_z) > render_distance):
                del self.chunks[chunk]

    def camera_update_handler(self, camera):
        camera_coord = self.__get_camera_coord__(camera)

        if camera_coord != self.central_chunk:
            self.central_chunk = camera_coord
            self.__unload_extra_chunks__(self.central_chunk, RENDER_DISTANCE)
            self.__create_chunks__(self.central_chunk, RENDER_DISTANCE)
            self.__load_chunks__(self.program)

    def load(self, program):
        self.__load_texture_file__(TEXTURE_ATLAS_PATH)

        self.program = program

        self.__load_chunks__(self.program)

    def draw(self):
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        for chunk in self.chunks.values():
            chunk.draw()

        glBindTexture(GL_TEXTURE_2D, 0)