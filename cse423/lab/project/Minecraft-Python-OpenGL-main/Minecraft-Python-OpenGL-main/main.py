from scene import Scene
from OpenGL.GL import *
from world import World

VERTEX_SHADER_PATH = "shaders/vertex.glsl"
FRAGMENT_SHADER_PATH = "shaders/fragment.glsl"

def main():
    scene_width = 1270
    scene_height = 720
    scene = Scene(scene_width, scene_height, "Window")

    vertex_code = open(VERTEX_SHADER_PATH, 'r').read()
    scene.add_shader(vertex_code, GL_VERTEX_SHADER)

    fragment_code = open(FRAGMENT_SHADER_PATH, 'r').read()
    scene.add_shader(fragment_code, GL_FRAGMENT_SHADER)

    scene.add_object(World())

    scene.start()

    scene.run()

if __name__ == '__main__':
    main()
