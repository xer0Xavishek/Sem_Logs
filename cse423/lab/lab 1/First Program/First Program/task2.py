# Task 2: Amazing Box

from OpenGL.GL import *
from OpenGL.GLUT import *
import random


class MovingPoint:
    def __init__(self, x, y, box_width_half, box_height_half):
        self.x = x
        self.y = y
        # Random diagonal direction: either -1 or +1 for both axes
        self.dir_x = random.choice([-1, 1])
        self.dir_y = random.choice([-1, 1])
        # Random colour for this point
        self.color = (random.random(), random.random(), random.random())
        # Store boundary limits so the point knows when to bounce
        self.width_half  = box_width_half
        self.height_half = box_height_half

    def move(self, speed):
        # Move point by speed in its current direction
        self.x += self.dir_x * speed
        self.y += self.dir_y * speed
        # Bounce off left/right walls by flipping horizontal direction
        if self.x >= self.width_half or self.x <= -self.width_half:
            self.dir_x *= -1
        # Bounce off top/bottom walls by flipping vertical direction
        if self.y >= self.height_half or self.y <= -self.height_half:
            self.dir_y *= -1


class AmazingBox:
    def __init__(self):
        self.width       = 850
        self.height      = 850
        self.width_half  = self.width  / 2
        self.height_half = self.height / 2

        self.points      = []       # list of all active MovingPoint objects
        self.speed       = 1.5      # movement speed applied to every point each frame

        # --- Blink state ---
        # blink_enabled  : True = blinking is ON,  False = blinking is OFF
        # points_visible : True = points are shown, False = points are hidden (during blink)
        # frame_count    : counts frames to time the blink toggle (~every 50 frames)
        self.blink_enabled  = False
        self.points_visible = True
        self.frame_count    = 0

        # --- Freeze state ---
        # is_frozen : True = animation paused,  False = animation running
        self.is_frozen = False

        # --- GLUT initialisation ---
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(self.width, self.height)
        glutCreateWindow(b"Amazing Box")

        # Set up orthographic projection centred at (0, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-self.width_half,  self.width_half,
                -self.height_half, self.height_half, -1, 1)
        glMatrixMode(GL_MODELVIEW)

        # Register GLUT callbacks
        glutDisplayFunc(self.output_back)
        glutIdleFunc(self.anima_part_view)
        glutKeyboardFunc(self.t2_key)
        glutSpecialFunc(self.t1_key)
        glutMouseFunc(self.m1)

    # ------------------------------------------------------------------
    # Convert GLUT mouse coords (top-left origin) to OpenGL world coords
    # ------------------------------------------------------------------
    def to_coord(self, mouse_x, mouse_y):
        gl_x = mouse_x - self.width_half
        gl_y = self.height_half - mouse_y
        return gl_x, gl_y

    # ------------------------------------------------------------------
    # Draw all points, respecting the current blink visibility state
    # ------------------------------------------------------------------
    def draw_points(self):
        glPointSize(9)
        for point in self.points:
            # During a blink cycle, skip drawing when points should be hidden
            if self.blink_enabled and not self.points_visible:
                continue
            glColor3f(*point.color)
            glBegin(GL_POINTS)
            glVertex2f(point.x, point.y)
            glEnd()

    # ------------------------------------------------------------------
    # Draw the rectangular boundary box using GL_LINES
    # ------------------------------------------------------------------
    def draw_border(self):
        glColor3f(0.7, 0.7, 0.7)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        # Bottom edge
        glVertex2f(-self.width_half, -self.height_half)
        glVertex2f( self.width_half, -self.height_half)
        # Right edge
        glVertex2f( self.width_half, -self.height_half)
        glVertex2f( self.width_half,  self.height_half)
        # Top edge
        glVertex2f( self.width_half,  self.height_half)
        glVertex2f(-self.width_half,  self.height_half)
        # Left edge
        glVertex2f(-self.width_half,  self.height_half)
        glVertex2f(-self.width_half, -self.height_half)
        glEnd()

    # ------------------------------------------------------------------
    # Main display callback — clears the screen and redraws everything
    # ------------------------------------------------------------------
    def output_back(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.draw_border()
        self.draw_points()
        glutSwapBuffers()

    # ------------------------------------------------------------------
    # Idle / animation callback — runs every frame
    # ------------------------------------------------------------------
    def anima_part_view(self):
        # Do nothing while the animation is frozen
        if not self.is_frozen:
            # Advance every point by the current speed
            for point in self.points:
                point.move(self.speed)

            # Advance the blink timer when blinking is active
            if self.blink_enabled:
                self.frame_count += 1
                # Toggle visibility every 50 frames (~once per second at 50 fps)
                if self.frame_count % 50 == 0:
                    self.points_visible = not self.points_visible

        glutPostRedisplay()

    # ------------------------------------------------------------------
    # Mouse callback
    # Right click → spawn a new point at the clicked location
    # Left  click → toggle blinking on / off
    # ------------------------------------------------------------------
    def m1(self, button, state, x, y):
        # Only act on button press, not on release
        if state != GLUT_DOWN:
            return

        if button == GLUT_RIGHT_BUTTON:
            # Convert click position to OpenGL coords and spawn a new point
            world_x, world_y = self.to_coord(x, y)
            self.points.append(
                MovingPoint(world_x, world_y, self.width_half, self.height_half)
            )

        elif button == GLUT_LEFT_BUTTON:
            # Toggle blinking on or off with each left click
            self.blink_enabled = not self.blink_enabled
            # Reset visibility to shown whenever blinking is turned off
            if not self.blink_enabled:
                self.points_visible = True
                self.frame_count    = 0

    # ------------------------------------------------------------------
    # Special key callback (arrow keys)
    # UP arrow   → increase speed by 20 %
    # DOWN arrow → decrease speed by 20 % (minimum 0.2)
    # ------------------------------------------------------------------
    def t1_key(self, key, x, y):
        if key == GLUT_KEY_UP:
            self.speed *= 1.2
        elif key == GLUT_KEY_DOWN:
            self.speed /= 1.2
            # Prevent speed from reaching zero
            if self.speed < 0.2:
                self.speed = 0.2

    # ------------------------------------------------------------------
    # Normal key callback
    # Spacebar → toggle freeze (pause / resume animation)
    # ------------------------------------------------------------------
    def t2_key(self, key, x, y):
        if key == b' ':
            self.is_frozen = not self.is_frozen

    def run(self):
        glutMainLoop()


if __name__ == "__main__":
    AmazingBox().run()