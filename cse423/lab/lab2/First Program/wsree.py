from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time, random, sys, math

WIN_W = 800
WIN_H = 600

catcher_x = WIN_W // 2
catcher_y = 60
CATCHER_W = 140
CATCHER_H = 24

diamond_x = random.randint(60, WIN_W - 60)
diamond_y = WIN_H - 80
DIAMOND_SIZE = 16

score = 0
game_running = True
game_playing = True
game_over = False

catcher_color = (1.0, 1.0, 1.0)
diamond_color = (1.0, 0.0, 1.0)
bg_color = (0.05, 0.07, 0.12)

last_time = time.time()
fall_speed = 120.0
speed_increase_per_catch = 8.0

BTN_W = 48
BTN_H = 36
btn_left_x = 80
btn_mid_x = WIN_W // 2
btn_right_x = WIN_W - 80
btn_y = WIN_H - 40

cheat_mode = False
catcher_speed = 400.0
auto_move_speed = 320.0

def clamp(v, a, b):
    return max(a, min(b, v))

def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    adx = abs(dx)
    ady = abs(dy)
    if adx >= ady:
        if dx >= 0 and dy >= 0:
            return 0
        if dx >= 0 and dy < 0:
            return 7
        if dx < 0 and dy >= 0:
            return 3
        return 4
    else:
        if dx >= 0 and dy >= 0:
            return 1
        if dx < 0 and dy >= 0:
            return 2
        if dx < 0 and dy < 0:
            return 5
        return 6

def to_zone0(zone, x, y):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y
    else:
        return x, y

def from_zone0(zone, u, v):
    if zone == 0:
        return u, v
    elif zone == 1:
        return v, u
    elif zone == 2:
        return -v, u
    elif zone == 3:
        return -u, v
    elif zone == 4:
        return -u, -v
    elif zone == 5:
        return -v, -u
    elif zone == 6:
        return v, -u
    elif zone == 7:
        return u, -v
    else:
        return u, v

def draw_midpoint_line(x1, y1, x2, y2, color=(1,1,1)):
    zone = find_zone(x1, y1, x2, y2)
    u1, v1 = to_zone0(zone, x1, y1)
    u2, v2 = to_zone0(zone, x2, y2)

    if u1 > u2:
        u1, u2 = u2, u1
        v1, v2 = v2, v1

    dx = u2 - u1
    dy = v2 - v1
    d = 2*dy - dx
    incE = 2*dy
    incNE = 2*(dy - dx)
    u = u1
    v = v1

    glColor3f(*color)
    glBegin(GL_POINTS)
    while u <= u2:
        px, py = from_zone0(zone, u, v)
        glVertex2i(int(px), int(py))
        if d > 0:
            d += incNE
            v += 1
        else:
            d += incE
        u += 1
    glEnd()

def draw_polyline(points, color=(1,1,1)):
    for i in range(len(points)):
        x1,y1 = points[i]
        x2,y2 = points[(i+1) % len(points)]
        draw_midpoint_line(int(x1), int(y1), int(x2), int(y2), color)

def draw_diamond(cx, cy, size, color):
    top = (cx, cy + size)
    right = (cx + size, cy)
    bottom = (cx, cy - size)
    left = (cx - size, cy)
    draw_midpoint_line(*top, *right, color)
    draw_midpoint_line(*right, *bottom, color)
    draw_midpoint_line(*bottom, *left, color)
    draw_midpoint_line(*left, *top, color)

def draw_catcher(cx, cy, w, h, color):
    top_left = (cx - w//2, cy + h//2)
    top_right = (cx + w//2, cy + h//2)
    bottom_left = (cx - w//4, cy - h//2)
    bottom_right = (cx + w//4, cy - h//2)
    draw_midpoint_line(*top_left, *top_right, color)
    draw_midpoint_line(*top_left, *bottom_left, color)
    draw_midpoint_line(*top_right, *bottom_right, color)
    draw_midpoint_line(*bottom_left, *bottom_right, color)
    
def draw_left_arrow_button(x, y, w, h):
    ax = x - w//2
    ay = y
    pts = [(ax + w//2, ay + h//2), (ax, ay), (ax + w//2, ay - h//2), (ax + w//2 - 6, ay)]
    draw_polyline(pts, (0.0, 0.8, 0.8))

def draw_play_pause_button(x, y, w, h, playing):
    if playing:
        bx = x - w//6
        draw_midpoint_line(bx - 6, y + h//3, bx - 6, y - h//3, (1.0, 0.6, 0.0))
        draw_midpoint_line(bx + 6, y + h//3, bx + 6, y - h//3, (1.0, 0.6, 0.0))
    else:
        pts = [(x - 6, y + h//3), (x + w//4, y), (x - 6, y - h//3)]
        draw_polyline(pts, (1.0, 0.6, 0.0))

def draw_quit_button(x, y, w, h):
    draw_midpoint_line(x - 10, y - 10, x + 10, y + 10, (1.0, 0.2, 0.2))
    draw_midpoint_line(x - 10, y + 10, x + 10, y - 10, (1.0, 0.2, 0.2))

def has_collided(box1, box2):
    return (box1['x'] < box2['x'] + box2['w'] and box1['x'] + box1['w'] > box2['x'] and box1['y'] < box2['y'] + box2['h'] and box1['y'] + box1['h'] > box2['y'])

def spawn_diamond():
    global diamond_x, diamond_y, diamond_color
    diamond_x = random.randint(60, WIN_W - 60)
    diamond_y = WIN_H - 60
    diamond_color = (random.uniform(0.6,1.0), random.uniform(0.4,1.0), random.uniform(0.4,1.0))

def on_restart():
    global score, fall_speed, game_over, game_playing, catcher_color
    score = 0
    fall_speed = 120.0
    game_over = False
    game_playing = True
    catcher_color = (1.0, 1.0, 1.0)
    spawn_diamond()
    print("Starting Over")

def on_quit():
    global score
    print("Goodbye", score)
    glutLeaveMainLoop()

def on_game_over():
    global game_over, game_playing, catcher_color
    game_over = True
    game_playing = False
    catcher_color = (1.0, 0.0, 0.0)
    print("Game Over. Score:", score)

def display():
    glClearColor(*bg_color, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_left_arrow_button(btn_left_x, btn_y, BTN_W, BTN_H)
    draw_play_pause_button(btn_mid_x, btn_y, BTN_W, BTN_H, game_playing)
    draw_quit_button(btn_right_x, btn_y, BTN_W, BTN_H)

    if not game_over:
        draw_diamond(int(diamond_x), int(diamond_y), DIAMOND_SIZE//2, diamond_color)

    draw_catcher(int(catcher_x), int(catcher_y), CATCHER_W, CATCHER_H, catcher_color)

    glutSwapBuffers()

def idle():
    global last_time, diamond_y, fall_speed, score, game_playing, catcher_x, cheat_mode

    cur = time.time()
    dt = cur - last_time
    last_time = cur

    if game_playing and not game_over:
        diamond_y -= fall_speed * dt

        if cheat_mode:
            target_x = clamp(diamond_x, CATCHER_W//2, WIN_W - CATCHER_W//2)
            if abs(target_x - catcher_x) > 1:
                move = math.copysign(min(auto_move_speed*dt, abs(target_x - catcher_x)), target_x - catcher_x)
                catcher_x += move
            catcher_x = clamp(catcher_x, CATCHER_W//2, WIN_W - CATCHER_W//2)

        diamond_box = {'x': diamond_x - DIAMOND_SIZE//2, 'y': diamond_y - DIAMOND_SIZE//2, 'w': DIAMOND_SIZE, 'h': DIAMOND_SIZE}
        catcher_box = {'x': catcher_x - CATCHER_W//2, 'y': catcher_y - CATCHER_H//2, 'w': CATCHER_W, 'h': CATCHER_H}

        if has_collided(diamond_box, catcher_box):
            score += 1
            print("Score:", score)
            fall_speed += speed_increase_per_catch * 0.25
            spawn_diamond()
            fall_speed += 2.0
        elif diamond_y < 0:
            on_game_over()

    glutPostRedisplay()

left_pressed = False
right_pressed = False

def special_key(key, x, y):
    global catcher_x, left_pressed, right_pressed
    if not game_playing or game_over or cheat_mode:
        return
    if key == GLUT_KEY_LEFT:
        left_pressed = True
        catcher_x -= 18
    elif key == GLUT_KEY_RIGHT:
        right_pressed = True
        catcher_x += 18
    catcher_x = clamp(catcher_x, CATCHER_W//2, WIN_W - CATCHER_W//2)

def special_up(key, x, y):
    global left_pressed, right_pressed
    if key == GLUT_KEY_LEFT:
        left_pressed = False
    elif key == GLUT_KEY_RIGHT:
        right_pressed = False

def keyboard(key, x, y):
    global game_playing, cheat_mode, catcher_x
    if key == b'c' or key == b'C':
        cheat_mode = not cheat_mode
        print("Cheat mode", "ON" if cheat_mode else "OFF")
    elif key == b'r' or key == b'R':
        on_restart()
    elif key == b'q' or key == b'\x1b':
        on_quit()

def mouse_click(button, state, mx, my):
    wy = WIN_H - my
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if abs(mx - btn_left_x) <= BTN_W and abs(wy - btn_y) <= BTN_H:
            on_restart()
            return
        if abs(mx - btn_mid_x) <= BTN_W and abs(wy - btn_y) <= BTN_H:
            toggle_play_pause()
            return
        if abs(mx - btn_right_x) <= BTN_W and abs(wy - btn_y) <= BTN_H:
            on_quit()
            return

def toggle_play_pause():
    global game_playing
    game_playing = not game_playing
    print("Paused" if not game_playing else "Resumed")

def reshape(w, h):
    glViewport(0,0,w,h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def timer(fps=60):
    glutPostRedisplay()
    glutTimerFunc(int(1000/fps), lambda t=0: timer(fps), 0)

def main():
    global last_time
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIN_W, WIN_H)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Catch the Diamonds - Midpoint Lines")
    glPointSize(1.0)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutReshapeFunc(reshape)
    glutSpecialFunc(special_key)
    glutSpecialUpFunc(special_up)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse_click)
    spawn_diamond()
    last_time = time.time()
    timer(60)
    glutMainLoop()

if __name__ == "__main__":
    main()