
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time


class MPL_caller:
    # Determines which of the 8 zones the line from (x1,y1) to (x2,y2) belongs to
    def find_zone(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) >= abs(dy):
            if dx >= 0 and dy >= 0:
                return 0
            elif dx < 0 and dy >= 0:
                return 3
            elif dx < 0 and dy < 0:
                return 4
            else:
                return 7
        else:
            if dx >= 0 and dy > 0:
                return 1
            elif dx < 0 and dy > 0:
                return 2
            elif dx < 0 and dy < 0:
                return 5
            else:
                return 6

    # Convert a point from its original zone to Zone 0
    def convert_to_zone0(self, x, y, zone):
        zone_map = [
            ( x,  y),   # Zone 0: no change
            ( y,  x),   # Zone 1: swap x, y
            ( y, -x),   # Zone 2: swap, negate original x
            (-x,  y),   # Zone 3: negate x
            (-x, -y),   # Zone 4: negate both
            (-y, -x),   # Zone 5: swap, negate both
            (-y,  x),   # Zone 6: swap, negate original y
            ( x, -y),   # Zone 7: negate y
        ]
        return zone_map[zone]

    # Convert a point from Zone 0 back to its original zone
    def convert_from_zone0(self, x, y, zone):
        zone_map = [
            ( x,  y),   # Zone 0
            ( y,  x),   # Zone 1
            (-y,  x),   # Zone 2
            (-x,  y),   # Zone 3
            (-x, -y),   # Zone 4
            (-y, -x),   # Zone 5
            ( y, -x),   # Zone 6
            ( x, -y),   # Zone 7
        ]
        return zone_map[zone]

    # Midpoint line drawing algorithm - only handles Zone 0
    def midpoint_zone0(self, x1, y1, x2, y2):
        x1 = int(round(x1))
        y1 = int(round(y1))
        x2 = int(round(x2))
        y2 = int(round(y2))

        dx = x2 - x1
        dy = y2 - y1

        d     = 2 * dy - dx
        incE  = 2 * dy
        incNE = 2 * (dy - dx)

        y = y1
        points = []
        for x in range(x1, x2 + 1):
            points.append((x, y))
            if d > 0:
                d += incNE
                y += 1
            else:
                d += incE
        return points

    # Public draw_line: handles any zone by converting to/from zone 0
    def draw_line(self, x1, y1, x2, y2):
        zone = self.find_zone(x1, y1, x2, y2)

        zx1, zy1 = self.convert_to_zone0(x1, y1, zone)
        zx2, zy2 = self.convert_to_zone0(x2, y2, zone)

        zone0_pts = self.midpoint_zone0(zx1, zy1, zx2, zy2)

        original_pts = []
        for a, b in zone0_pts:
            original_pts.append(self.convert_from_zone0(a, b, zone))
        return original_pts


class Diamond:
    BASE_SIZE = 25

    def __init__(self, x, y, size=BASE_SIZE):
        self.x = x
        self.y = y
        self.sz = size
        # Make sure random colors are bright enough to stand out on black bg
        r = random.uniform(0.4, 1.0)
        g = random.uniform(0.4, 1.0)
        b = random.uniform(0.4, 1.0)
        self.col = (r, g, b)

    def fall(self, dy):
        self.y -= dy

    def get_bounds(self):
        # Returns (center_x, center_y, size, size) for bounding box use
        return (self.x, self.y, self.sz, self.sz)


class DiamondCatcherGame:
    def __init__(self):
        self.win_w  = 800
        self.win_h  = 800

        # Catcher properties
        self.cat_x    = self.win_w // 2
        self.cat_y    = 50
        self.cat_w    = 100
        self.cat_h    = 25
        self.cat_tilt = 12   # how much the trapezoid tilts inward on each side

        # Game state
        self.dia_speed  = 1.3
        self.score      = 0
        self.game_over  = False
        self.paused     = False
        self.cheat_on   = False

        self.diamond  = self.spawn_diamond()
        self.mpl      = MPL_caller()
        self.last_time = time.time()

        # Button areas: (x, y, w, h) in screen coords (y is from bottom after flip)
        self.btn_restart = (52,          self.win_h - 56, 35, 35)
        self.btn_pause   = (self.win_w // 2 - 17, self.win_h - 56, 35, 35)
        self.btn_quit    = (self.win_w - 90,  self.win_h - 56, 35, 35)

    # -------------------------------------------------------
    # Game Logic
    # -------------------------------------------------------

    def spawn_diamond(self):
        x = random.randint(30, self.win_w - 30)
        y = self.win_h - 65
        return Diamond(x, y)

    def move_catcher(self, dx):
        if self.game_over or self.paused:
            return
        self.cat_x += dx
        self.cat_x = max(0, min(self.win_w - self.cat_w, self.cat_x))

    def toggle_pause(self):
        self.paused = not self.paused
        if not self.paused:
            # Reset timer so we don't get a huge delta after unpausing
            self.last_time = time.time()

    def toggle_cheat(self):
        self.cheat_on = not self.cheat_on

    def reset_game(self):
        self.score      = 0
        self.game_over  = False
        self.paused     = False
        self.dia_speed  = 1.3
        self.cat_x      = self.win_w // 2
        self.diamond    = self.spawn_diamond()
        self.last_time  = time.time()
        print("Starting over!")

    def check_collision(self):
        dx, dy, ds, _ = self.diamond.get_bounds()
        half = ds / 2

        # Diamond bounding box
        d_left   = dx - half
        d_right  = dx + half
        d_top    = dy + half
        d_bottom = dy - half

        # Catcher bounding box
        c_left   = self.cat_x
        c_right  = self.cat_x + self.cat_w
        c_top    = self.cat_y + self.cat_h
        c_bottom = self.cat_y

        # AABB collision check
        return (d_left  < c_right  and
                d_right > c_left   and
                d_bottom < c_top   and
                d_top   > c_bottom)

    def update(self):
        if self.paused or self.game_over:
            return

        current_time = time.time()
        delta        = current_time - self.last_time
        self.last_time = current_time

        fall_amount = self.dia_speed * delta * 60

        # Cheat mode: smoothly slide the catcher toward the diamond
        if self.cheat_on:
            target_x = int(self.diamond.x - self.cat_w / 2)
            target_x = max(0, min(self.win_w - self.cat_w, target_x))
            diff     = target_x - self.cat_x
            step     = min(abs(diff), max(12, int(abs(diff) * 0.18)))
            if diff > 0:
                self.cat_x += step
            elif diff < 0:
                self.cat_x -= step

        self.diamond.fall(fall_amount)

        if self.check_collision():
            self.score     += 1
            print("Score:", self.score)
            self.dia_speed += 0.2
            self.diamond    = self.spawn_diamond()
        elif self.diamond.y <= 0:
            self.game_over = True
            print("Game Over! Final Score:", self.score)

    # -------------------------------------------------------
    # Drawing helpers (all use midpoint lines + GL_POINTS only)
    # -------------------------------------------------------

    def put_line(self, x1, y1, x2, y2, col=(1, 1, 1)):
        glColor3f(*col)
        pts = self.mpl.draw_line(x1, y1, x2, y2)
        for px, py in pts:
            glVertex2f(px, py)

    def draw_diamond(self, d):
        cx, cy, s = d.x, d.y, d.sz
        half = s // 2
        # Four midpoint lines forming the diamond shape
        self.put_line(cx,        cy + half, cx + half, cy,        d.col)
        self.put_line(cx + half, cy,        cx,        cy - half, d.col)
        self.put_line(cx,        cy - half, cx - half, cy,        d.col)
        self.put_line(cx - half, cy,        cx,        cy + half, d.col)

    def draw_catcher(self):
        col = (1, 0, 0) if self.game_over else (1, 1, 1)
        x   = self.cat_x
        y   = self.cat_y
        w   = self.cat_w
        h   = self.cat_h
        t   = self.cat_tilt

        # Trapezoid shape: wider at top, slightly indented at bottom
        # Bottom-left, bottom-right, top-right, top-left (closed)
        self.put_line(x + t,     y,     x + w - t, y,     col)   # bottom
        self.put_line(x + w - t, y,     x + w,     y + h, col)   # right diagonal
        self.put_line(x + w,     y + h, x,          y + h, col)  # top
        self.put_line(x,         y + h, x + t,      y,     col)  # left diagonal

    def draw_buttons(self):
        rx, ry, rw, rh = self.btn_restart
        px, py, pw, ph = self.btn_pause
        qx, qy, qw, qh = self.btn_quit

        teal  = (0.0, 0.85, 0.85)   # bright teal for restart
        amber = (1.0, 0.75, 0.0)    # amber for pause/play
        red   = (1.0, 0.0,  0.0)    # red for quit

        # --- Restart button: left arrow ---
        mid_y = (ry + ry + rh) // 2
        self.put_line(rx + rw, ry,      rx,      mid_y,       teal)
        self.put_line(rx,      mid_y,   rx + rw, ry + rh,     teal)
        self.put_line(rx + rw, ry,      rx + rw, ry + rh,     teal)

        # --- Pause / Play button ---
        if not self.paused:
            # Show pause icon (two vertical bars)
            bar_gap = pw // 3
            self.put_line(px,           py, px,           py + ph, amber)
            self.put_line(px + bar_gap, py, px + bar_gap, py + ph, amber)
        else:
            # Show play icon (right-pointing triangle)
            mid_right_y = (py + py + ph) // 2
            self.put_line(px,      py + ph, px + pw, mid_right_y, amber)
            self.put_line(px + pw, mid_right_y, px, py,           amber)
            self.put_line(px,      py,      px,      py + ph,     amber)

        # --- Quit button: X shape ---
        self.put_line(qx,      qy,      qx + qw, qy + qh, red)
        self.put_line(qx + qw, qy,      qx,      qy + qh, red)

    # -------------------------------------------------------
    # Main render
    # -------------------------------------------------------

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glBegin(GL_POINTS)
        self.draw_catcher()
        self.draw_diamond(self.diamond)
        self.draw_buttons()
        glEnd()
        glutSwapBuffers()

    # -------------------------------------------------------
    # Input callbacks
    # -------------------------------------------------------

    def key_pressed(self, key, x, y):
        if key == b'c':
            self.toggle_cheat()

    def special_pressed(self, key, x, y):
        if key == GLUT_KEY_LEFT:
            self.move_catcher(-12)
        elif key == GLUT_KEY_RIGHT:
            self.move_catcher(12)

    def mouse_click(self, button, state, mx, my):
        if state != GLUT_DOWN:
            return
        # Flip y since OpenGL origin is bottom-left
        my = self.win_h - my

        btn_actions = {
            "restart": (self.btn_restart, self.reset_game),
            "pause":   (self.btn_pause,   self.toggle_pause),
            "quit":    (self.btn_quit,    self.quit_game),
        }

        for name, (area, action) in btn_actions.items():
            bx, by, bw, bh = area
            if bx <= mx <= bx + bw and by <= my <= by + bh:
                action()
                break

    def quit_game(self):
        print(f"Goodbye! Final Score: {self.score}")
        glutLeaveMainLoop()


# -------------------------------------------------------
# GLUT callbacks (kept thin — actual logic is in the class)
# -------------------------------------------------------

game = DiamondCatcherGame()

def game_loop():
    game.update()
    game.render()

def keyboard_cb(key, x, y):
    game.key_pressed(key, x, y)

def special_cb(key, x, y):
    game.special_pressed(key, x, y)

def mouse_cb(button, state, x, y):
    game.mouse_click(button, state, x, y)


# -------------------------------------------------------
# Initialise GLUT and enter main loop
# -------------------------------------------------------

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
glutInitWindowSize(game.win_w, game.win_h)
glutCreateWindow(b"Catch the Diamonds!")

glutDisplayFunc(game_loop)
glutKeyboardFunc(keyboard_cb)
glutSpecialFunc(special_cb)
glutMouseFunc(mouse_cb)
glutIdleFunc(game_loop)

glClearColor(0.0, 0.0, 0.0, 1.0)   # black background
glOrtho(0, game.win_w, 0, game.win_h, 0, 1)

glutMainLoop()
