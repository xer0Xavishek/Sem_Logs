
# Task 1 — Rainy house scene with day/night transition
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# Day/night transition state constants
IDLE        = -1   # no transition is happening
BRIGHTENING =  1   # scene is getting lighter (night -> day)
DARKENING   =  0   # scene is getting darker  (day  -> night)


class House_with_rain:
    """
    Draws a house in the rain with a smooth day/night cycle.
      L / l  — gradually brighten (night -> day)
      D / d  — gradually darken  (day  -> night)
      Left/Right arrows — tilt the rain (wind direction)
    """

    def __init__(self, w=500, h=500):
        self.width  = w
        self.height = h

        self.rain_drops      = []         # list of [x, y] for every raindrop
        self.wind_angle      = 0.0        # positive = rain leans left, negative = right
        self.brightness      = 0.0        # 0.0 = full night, 1.0 = full day
        self.transition_mode = IDLE       # current state of the day/night transition
        self.fade_speed      = 0.004      # brightness change per frame

    def trianstruct(self, x_p, y_p, w_p, h_p):
        """Draw a single upward-pointing filled triangle from its base."""
        glBegin(GL_TRIANGLES)
        glVertex2d(x_p, y_p)
        glVertex2d(x_p + w_p, y_p)
        glVertex2d(x_p + (w_p / 2), y_p + h_p)
        glEnd()

    def draw_background(self):
        """Sky colour shifts from black (night) to deep blue (day)."""
        r = self.brightness * 0.40
        g = self.brightness * 0.60
        b = self.brightness * 0.90
        glColor3f(r, g, b)
        glBegin(GL_TRIANGLES)
        glVertex2d(0, 0)
        glVertex2d(self.width, 0)
        glVertex2d(self.width, self.height)
        glVertex2d(0, 0)
        glVertex2d(0, self.height)
        glVertex2d(self.width, self.height)
        glEnd()

    def draw_ground(self):
        """Ground shifts from very dark green (night) to grass green (day)."""
        r = 0.10 + self.brightness * 0.20
        g = 0.25 + self.brightness * 0.35
        b = 0.05 + self.brightness * 0.05
        glColor3f(r, g, b)
        ground_top    = 208
        ground_bottom = 0
        left_edge     = 0
        right_edge    = self.width
        glBegin(GL_TRIANGLES)
        glVertex2d(left_edge,  ground_bottom)
        glVertex2d(right_edge, ground_bottom)
        glVertex2d(right_edge, ground_top)
        glVertex2d(left_edge,  ground_bottom)
        glVertex2d(left_edge,  ground_top)
        glVertex2d(right_edge, ground_top)
        glEnd()

    def draw_house(self):
        # House boundary coordinates
        wall_left   = 130
        wall_right  = 370
        wall_bottom = 100
        wall_top    = 300

        # ---------- Main walls ----------
        r = 0.30 + self.brightness * 0.50
        g = 0.22 + self.brightness * 0.48
        b = 0.10 + self.brightness * 0.30
        glColor3f(r, g, b)
        glBegin(GL_TRIANGLES)
        glVertex2d(wall_left,  wall_bottom)
        glVertex2d(wall_left,  wall_top)
        glVertex2d(wall_right, wall_top)
        glVertex2d(wall_left,  wall_bottom)
        glVertex2d(wall_right, wall_bottom)
        glVertex2d(wall_right, wall_top)
        glEnd()

        # ---------- Roof (triangle above the walls) ----------
        r = 0.25 + self.brightness * 0.30
        g = 0.10 + self.brightness * 0.17
        b = 0.04 + self.brightness * 0.03
        glColor3f(r, g, b)
        self.trianstruct(wall_left, wall_top, wall_right - wall_left, 120)

        # ---------- Chimney ----------
        chimney_left   = wall_right - 90
        chimney_right  = chimney_left + 40
        chimney_bottom = wall_top + 50
        chimney_top    = chimney_bottom + 80
        r = 0.22 + self.brightness * 0.28
        g = 0.08 + self.brightness * 0.12
        b = 0.04
        glColor3f(r, g, b)
        glBegin(GL_TRIANGLES)
        glVertex2d(chimney_left,  chimney_bottom)
        glVertex2d(chimney_right, chimney_bottom)
        glVertex2d(chimney_right, chimney_top)
        glVertex2d(chimney_left,  chimney_bottom)
        glVertex2d(chimney_left,  chimney_top)
        glVertex2d(chimney_right, chimney_top)
        glEnd()

        # ---------- Door (centred on the front wall) ----------
        door_width  = 60
        door_height = 100
        door_left   = wall_left + (wall_right - wall_left - door_width) / 2
        door_right  = door_left + door_width
        door_bottom = wall_bottom
        door_top    = door_bottom + door_height
        r = 0.25 + self.brightness * 0.25
        g = 0.12 + self.brightness * 0.13
        b = 0.0
        glColor3f(r, g, b)
        glBegin(GL_TRIANGLES)
        glVertex2d(door_left,  door_bottom)
        glVertex2d(door_left,  door_top)
        glVertex2d(door_right, door_top)
        glVertex2d(door_left,  door_bottom)
        glVertex2d(door_right, door_bottom)
        glVertex2d(door_right, door_top)
        glEnd()

        # ---------- Left window ----------
        lw_left   = wall_left + 20
        lw_right  = lw_left + 55
        lw_bottom = wall_top - 95
        lw_top    = lw_bottom + 55
        r = 0.60 - self.brightness * 0.20
        g = 0.55 - self.brightness * 0.10
        b = 0.10 + self.brightness * 0.80
        glColor3f(r, g, b)
        glBegin(GL_TRIANGLES)
        glVertex2d(lw_left,  lw_bottom)
        glVertex2d(lw_right, lw_bottom)
        glVertex2d(lw_right, lw_top)
        glVertex2d(lw_left,  lw_bottom)
        glVertex2d(lw_left,  lw_top)
        glVertex2d(lw_right, lw_top)
        glEnd()
        # Window frame + cross dividers
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2d(lw_left,  lw_bottom);               glVertex2d(lw_right, lw_bottom)
        glVertex2d(lw_right, lw_bottom);               glVertex2d(lw_right, lw_top)
        glVertex2d(lw_right, lw_top);                  glVertex2d(lw_left,  lw_top)
        glVertex2d(lw_left,  lw_top);                  glVertex2d(lw_left,  lw_bottom)
        glVertex2d((lw_left+lw_right)/2, lw_bottom);   glVertex2d((lw_left+lw_right)/2, lw_top)
        glVertex2d(lw_left, (lw_bottom+lw_top)/2);     glVertex2d(lw_right, (lw_bottom+lw_top)/2)
        glEnd()

        # ---------- Right window ----------
        rw_right  = wall_right - 20
        rw_left   = rw_right - 55
        rw_bottom = wall_top - 95
        rw_top    = rw_bottom + 55
        r = 0.60 - self.brightness * 0.20
        g = 0.55 - self.brightness * 0.10
        b = 0.10 + self.brightness * 0.80
        glColor3f(r, g, b)
        glBegin(GL_TRIANGLES)
        glVertex2d(rw_left,  rw_bottom)
        glVertex2d(rw_right, rw_bottom)
        glVertex2d(rw_right, rw_top)
        glVertex2d(rw_left,  rw_bottom)
        glVertex2d(rw_left,  rw_top)
        glVertex2d(rw_right, rw_top)
        glEnd()
        # Window frame + cross dividers
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2d(rw_left,  rw_bottom);               glVertex2d(rw_right, rw_bottom)
        glVertex2d(rw_right, rw_bottom);               glVertex2d(rw_right, rw_top)
        glVertex2d(rw_right, rw_top);                  glVertex2d(rw_left,  rw_top)
        glVertex2d(rw_left,  rw_top);                  glVertex2d(rw_left,  rw_bottom)
        glVertex2d((rw_left+rw_right)/2, rw_bottom);   glVertex2d((rw_left+rw_right)/2, rw_top)
        glVertex2d(rw_left, (rw_bottom+rw_top)/2);     glVertex2d(rw_right, (rw_bottom+rw_top)/2)
        glEnd()

        # ---------- Door knob ----------
        glColor3f(0.9, 0.75, 0.1)
        glPointSize(6)
        glBegin(GL_POINTS)
        glVertex2d(door_left + 48, (door_bottom + door_top) / 2)
        glEnd()

    def setup_projection(self):
        """Set up a simple 2-D orthographic projection matching the window size."""
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, self.width, 0.0, self.height, 0.0, 1.0)
        glMatrixMode(GL_MODELVIEW)

    def rainfall_overscene(self):
        """Spawn new raindrops at the top and advance all drops downward."""
        # Add two new drops per frame
        for _ in range(2):
            x = random.uniform(0, self.width)
            self.rain_drops.append([x, self.height])

        # Move every drop down and sideways with the wind
        for drop in self.rain_drops:
            drop[0] += self.wind_angle * 0.3   # horizontal drift
            drop[1] -= 6                        # fall speed

            # Wrap horizontally so drops don't disappear off the sides
            if drop[0] < 0:
                drop[0] += self.width
            elif drop[0] > self.width:
                drop[0] -= self.width

        # Remove drops that have hit the ground
        self.rain_drops = [drop for drop in self.rain_drops if drop[1] > 0]

    def draw_rain(self):
        """Draw each raindrop as a short angled line streak."""
        # Drops appear slightly brighter at night (more visible against dark sky)
        r = 1
        g = 1
        b = 1
        glColor3f(r, g, b)
        glLineWidth(1.5)
        glBegin(GL_LINES)
        for x, y in self.rain_drops:
            glVertex2f(x, y)
            glVertex2f(x - self.wind_angle * 2,  y - 12)
        glEnd()

    def output_back(self):
        """Main display callback — clear and redraw the full scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.draw_background()   # drawn as geometry, replaces glClearColor
        self.draw_ground()
        self.draw_house()
        self.draw_rain()
        glutSwapBuffers()

    def change_DN(self, value=0):
        """Idle callback — advance the brightness transition and rain each frame."""
        if self.transition_mode == BRIGHTENING:
            self.brightness += self.fade_speed
        elif self.transition_mode == DARKENING:
            self.brightness -= self.fade_speed

        # Keep brightness clamped to [0.0, 1.0]
        self.brightness = max(0.0, min(1.0, self.brightness))

        self.rainfall_overscene()
        self.output_back()

    def key_inputboard(self, key, x, y):
        """Left/Right arrow keys change the wind angle (rain tilt)."""
        if key == GLUT_KEY_RIGHT:
            self.wind_angle -= 0.3   # tilt rain to the right
        elif key == GLUT_KEY_LEFT:
            self.wind_angle += 0.3   # tilt rain to the left

    def normal_key_inputboard(self, key, x, y):
        """L = start brightening (night -> day), D = start darkening (day -> night)."""
        if key in (b'l', b'L'):
            self.transition_mode = BRIGHTENING
        elif key in (b'd', b'D'):
            self.transition_mode = DARKENING

    def checkrun(self):
        """Initialise GLUT and start the main loop."""
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(200, 200)
        glutCreateWindow(b"House with raining")
        self.setup_projection()
        glutDisplayFunc(self.output_back)
        glutSpecialFunc(self.key_inputboard)
        glutKeyboardFunc(self.normal_key_inputboard)
        glutIdleFunc(self.change_DN)
        glutMainLoop()


if __name__ == "__main__":
    scene = House_with_rain()
    scene.checkrun()