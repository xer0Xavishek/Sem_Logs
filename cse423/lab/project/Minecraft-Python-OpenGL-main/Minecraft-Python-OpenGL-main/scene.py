import glfw
from OpenGL.GL import *
import glm
import numpy as np
import ctypes
from object import vertex_data_dtype
from camera import Camera
import time

class Scene:
    def __init__ (self, width, height, window_title):
        self.width = width
        self.height = height
        self.window_title = window_title

        self.__create_camera__()

        self.shaders = []
        self.objects = []
        self.uniform_locations = {}
    
    def __init_window__(self):
        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

        window = glfw.create_window(self.width, self.height, self.window_title, None, None)
        if not window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")

        glfw.make_context_current(window)

        return window

    def __init_program__(self):
        program = glCreateProgram()

        return program

    def __setup_shader__(self, program, shader_code, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, shader_code)
        glCompileShader(shader)

        if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(shader))

        glAttachShader(program, shader)

        return shader        

    def __build_program__(self, program):
        glLinkProgram(program)

        if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
            raise RuntimeError(glGetProgramInfoLog(program))

    def __start_program__(self, program):
        glUseProgram(program)

    def __set_background_color__ (self, window, rgb_color):
        r, g, b = rgb_color
        
        a = 1.0

        glClearColor(r/255, g/255, b/255, a)

    def __load_objects__(self, program):
        for obj in self.objects:
            obj.load(program)

    def __create_camera__(self):
        self.camera = Camera(self.width, self.height)

    def __get_uniform_location__(self, uniform_name):
        if uniform_name not in self.uniform_locations:
            self.uniform_locations[uniform_name] = glGetUniformLocation(self.program, uniform_name)
        
        return self.uniform_locations[uniform_name]

    def __start_camera__(self, window):
        self.camera.start(self.window)

        for object in self.objects:
            self.camera.add_update_handler(object.camera_update_handler)

    def add_shader(self, shader_code, shader_type):
        self.shaders.append(
            {
                "shader": None,
                "shader_code": shader_code,
                "shader_type": shader_type
            }
        )

    def add_object(self, object):
        self.objects.append(object)

    def start(self):
        glfw.init()

        self.window = self.__init_window__()

        self.program = self.__init_program__()

        for shader in self.shaders:
            shader["shader"] = self.__setup_shader__(self.program, shader["shader_code"], shader["shader_type"])

        self.__build_program__(self.program)

        self.__start_program__(self.program)

        self.__load_objects__(self.program)

        self.__start_camera__(self.window)

        self.__set_background_color__(self.window, (173, 216, 230))

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        glEnable(GL_DEPTH_TEST)

        glfw.show_window(self.window)

    def run(self):
        
        transform_array = np.array(glm.mat4(1.0))
        glUniformMatrix4fv(self.__get_uniform_location__("uTransform"), 1, GL_TRUE, transform_array)

        # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            view_array = np.array(self.camera.get_view_matrix())
            glUniformMatrix4fv(self.__get_uniform_location__("uView"), 1, GL_TRUE, view_array)

            projection_array = np.array(self.camera.get_projection_matrix())
            glUniformMatrix4fv(self.__get_uniform_location__("uProjection"), 1, GL_TRUE, projection_array)

            for obj in self.objects:
                obj.draw()

            glfw.swap_buffers(self.window)

        glfw.terminate()