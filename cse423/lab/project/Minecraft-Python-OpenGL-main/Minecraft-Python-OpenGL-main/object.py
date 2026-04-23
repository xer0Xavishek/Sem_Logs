import numpy as np
from OpenGL.GL import *
from PIL import Image

vertex_data_dtype = np.dtype([
    ("position", np.float32, 3),
    ("texture", np.float32, 2)
])

class Object:
    def __init__(self):
        pass

    def __load_texture_file__(self, texture_file):
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        # Set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        image = Image.open(texture_file)
        image_width = image.size[0]
        image_height = image.size[1]
        image_data = image.tobytes("raw", "RGBA", 0, -1)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    def load(self):
        raise NotImplementedError("load() not implemented")

    def draw(self, camera):
        raise NotImplementedError("draw() not implemented")
    
    def camera_update_handler(self, camera):
        raise NotImplementedError("camera_update_handler() not implemented")
