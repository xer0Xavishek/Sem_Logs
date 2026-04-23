import numpy as np
import glfw
import glm
from OpenGL.GL import *


class Camera:

    def __init__(self, window_width, window_height, speed = 0.1, sensitivity = 0.1):
        self.speed = speed
        self.sensitivity = sensitivity
        self.aspect = window_width / window_height

        self.pos   = glm.vec3(0.0, 3.0, 10.0)
        self.front = glm.vec3(0.0,  0.0, 0.0)
        self.up    = glm.vec3(0.0,  1.0,  0.0)
        self.first_mouse = True
        self.yaw = -90.0
        self.pitch = 0.0
        self.projection_angle = 45.0
        self.last_x = window_width / 2.0
        self.last_y = window_height / 2.0

        self.update_handlers = []

    def __handle_key_event__(self, window, key, scancode, action, mods):
        if key == glfw.KEY_W and action != glfw.RELEASE:
            self.pos += self.speed * glm.normalize(glm.vec3(self.front.x, 0.0, self.front.z))
        elif key == glfw.KEY_S and action != glfw.RELEASE:
            self.pos -= self.speed * glm.normalize(glm.vec3(self.front.x, 0.0, self.front.z))
        elif key == glfw.KEY_A and action != glfw.RELEASE:
            self.pos -= self.speed * glm.normalize(glm.cross(self.front, self.up))
        elif key == glfw.KEY_D and action != glfw.RELEASE:
            self.pos += self.speed * glm.normalize(glm.cross(self.front, self.up))
        elif key == glfw.KEY_SPACE and action != glfw.RELEASE:
            self.pos += self.speed * self.up
        elif key == glfw.KEY_C and action != glfw.RELEASE:
            self.pos -= self.speed * self.up
        elif key == glfw.KEY_ESCAPE and action != glfw.RELEASE:
            glfw.set_window_should_close(window, True)
        
        self.__trigger_update_handlers__()

    def __handle_mouse_event__(self, window, xpos, ypos):
        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False

        xoffset = (xpos - self.last_x) * self.sensitivity
        yoffset = (self.last_y - ypos) * self.sensitivity

        self.last_x = xpos
        self.last_y = ypos

        self.yaw += xoffset;
        self.pitch += yoffset;


        if self.pitch >= 90.0: self.pitch = 90.0
        if self.pitch <= -90.0: self.pitch = -90.0

        front = glm.vec3()
        front.x = np.cos(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        front.y = np.sin(glm.radians(self.pitch))
        front.z = np.sin(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))

        self.front = glm.normalize(front)

    def __trigger_update_handlers__(self):
        for handler in self.update_handlers:
            handler(self)

    def start(self, window):
        glfw.set_key_callback(window, self.__handle_key_event__)
        glfw.set_cursor_pos_callback(window, self.__handle_mouse_event__)
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def get_view_matrix(self):
        return glm.lookAt(self.pos, self.pos + self.front, self.up);
    
    def get_projection_matrix(self):
        return glm.perspective(glm.radians(self.projection_angle), self.aspect, 0.1, 1000.0)

    def get_position(self):
        return self.pos

    def add_update_handler(self, handler):
        self.update_handlers.append(handler)
