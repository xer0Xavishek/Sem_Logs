# Task 2: Amazing Box

from OpenGL.GL import *
from OpenGL.GLUT import *
import random


class MovingPoint:
    def __init__(self, x, y, box_width_half, box_height_half):
        self.x = x
        self.y = y
        self.dir_x = random.choice([-1, 1])
        self.dir_y = random.choice([-1, 1])
        self.color = (random.random(), random.random(), random.random())
        self.width_half  = box_width_half
        self.height_half = box_height_half

    def move(self, speed):
        self.x += self.dir_x * speed
        self.y += self.dir_y * speed
        if self.x >= self.width_half or self.x <= -self.width_half:
            self.dir_x *= -1
        if self.y >= self.height_half or self.y <= -self.height_half:
            self.dir_y *= -1


class AmazingBox:
    def __init__(self):
        self.width       = 550
        self.height      = 550
        self.width_half  = self.width  / 2
        self.height_half = self.height / 2

        self.points      = []       
        self.speed       = 1      
        
        self.blink_enabled  = False
        self.points_visible = True
        self.frame_count    = 0
        self.blink_interval = 55    

        self.is_frozen = False

        glutInit()
        glutInitDisplayMode(GLUT_RGBA)
        glutInitWindowSize(self.width, self.height)
        glutCreateWindow(b"Amazing Box")

        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-self.width_half,  self.width_half,
                -self.height_half, self.height_half, -1, 1)
        glMatrixMode(GL_MODELVIEW)

        glutDisplayFunc(self.output_back)
        glutIdleFunc(self.anima_part_view)
        glutKeyboardFunc(self.t2_key)
        glutSpecialFunc(self.t1_key)
        glutMouseFunc(self.m1)

    def to_coord(self, mouse_x, mouse_y):
        gl_x = mouse_x - self.width_half
        gl_y = self.height_half - mouse_y
        return gl_x, gl_y


    def draw_points(self):
        glPointSize(9)
        for point in self.points:
            if self.blink_enabled and not self.points_visible:
                continue
            glColor3f(*point.color)
            glBegin(GL_POINTS)
            glVertex2f(point.x, point.y)
            glEnd()


    def draw_border(self):
        glColor3f(0.7, 0.7, 0.7)
        glLineWidth(2.0)
        glBegin(GL_LINES)

        glVertex2f(-self.width_half, -self.height_half)
        glVertex2f( self.width_half, -self.height_half)

        glVertex2f( self.width_half, -self.height_half)
        glVertex2f( self.width_half,  self.height_half)

        glVertex2f( self.width_half,  self.height_half)
        glVertex2f(-self.width_half,  self.height_half)

        glVertex2f(-self.width_half,  self.height_half)
        glVertex2f(-self.width_half, -self.height_half)
        glEnd()

 
    def output_back(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.draw_border()
        self.draw_points()
        glutSwapBuffers()


    def anima_part_view(self):

        if not self.is_frozen:

            for point in self.points:
                point.move(self.speed)

            if self.blink_enabled:
                self.frame_count += 1

                if self.frame_count % self.blink_interval == 0:
                    self.points_visible = not self.points_visible

        glutPostRedisplay()


    def m1(self, button, state, x, y):

        if state != GLUT_DOWN:
            return

        if button == GLUT_RIGHT_BUTTON:

            world_x, world_y = self.to_coord(x, y)
            self.points.append(
                MovingPoint(world_x, world_y, self.width_half, self.height_half)
            )

        elif button == GLUT_LEFT_BUTTON:

            self.blink_enabled = not self.blink_enabled

            if not self.blink_enabled:
                self.points_visible = True
                self.frame_count    = 0

  
    def t1_key(self, key, x, y):
        if key == GLUT_KEY_UP:
            self.speed *= 1.2
        elif key == GLUT_KEY_DOWN:
            self.speed /= 1.2

            if self.speed < 0.2:
                self.speed = 0.2

  
    def t2_key(self, key, x, y):
        if key == b' ':
            self.is_frozen = not self.is_frozen

    def run(self):
        glutMainLoop()


if __name__ == "__main__":
    AmazingBox().run()