from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

import math, sys, time, random


WIN_W, WIN_H = 1280, 800
ASPECT = WIN_W/float(WIN_H)
FOVY = 40
FOVY = 40
NEAR_Z, FAR_Z = 0.1, 5000.0

# camera follows player with smoothing
cam_pos = [ -300.0, -60.0, 260.0 ]
cam_tgt = [    0.0,   0.0, 120.0 ]
SMOOTH = 0.12 # camera lerp factor

  
class AABB3:
    def __init__(self, x, y, z, w, d, h):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.d = d
        self.h = h
    def minx(self): return self.x
    def miny(self): return self.y
    def minz(self): return self.z
    def maxx(self): return self.x + self.w
    def maxy(self): return self.y + self.d
    def maxz(self): return self.z + self.h

def aabb3_overlap(a: AABB3, b: AABB3) -> bool:
    return (a.minx() < b.maxx() and a.maxx() > b.minx() and
            a.miny() < b.maxy() and a.maxy() > b.miny() and
            a.minz() < b.maxz() and a.maxz() > b.minz())

#Z is up, player moves along X, Y

class MovingPlatform:
    def __init__(self, aabb, x_start, x_end, speed, dir):
        self.aabb = aabb
        self.x_start = x_start
        self.x_end = x_end
        self.speed = speed
        self.dir = dir

PLATFORMS = []     # list[AABB3]
MOVING_PLATFORMS = [] # list[AABB3]
SPIKES = []        # list[AABB3] hazard
GOAL = None        # AABB3
POWERUPS = []      # list of dicts: {'aabb': AABB3, 'type': str, 'active': bool}

CORRIDOR_Y = 240.0   # global depth
Y_MIN, Y_MAX = -CORRIDOR_Y/2.0, CORRIDOR_Y/2.0

def add_platform(x,y,z,w,d,h): PLATFORMS.append(AABB3(x,y,z,w,d,h))
def add_moving_platform(x,y,z,w,d,h, x_start, x_end, speed):
    dir = 1 if speed > 0 else -1
    _x_start, _x_end = min(x_start, x_end), max(x_start, x_end)
    MOVING_PLATFORMS.append(MovingPlatform(AABB3(x,y,z,w,d,h), _x_start, _x_end, abs(speed), dir))

def build_level():
    global GOAL, PLATFORMS, SPIKES, POWERUPS, MOVING_PLATFORMS
    PLATFORMS.clear(); SPIKES.clear(); POWERUPS.clear(); MOVING_PLATFORMS.clear()

    # Section 1: First Power-Up (Double Jump)
    add_platform(0, Y_MIN, 0, 200, CORRIDOR_Y, 22)           # Starting platform
    add_platform(250, Y_MIN+40, 40, 80, CORRIDOR_Y-80, 22)   
    add_platform(400, Y_MIN, 80, 150, CORRIDOR_Y, 22)        # power-up platform 
    POWERUPS.append({'aabb': AABB3(480, 0, 120, 24, 24, 24), 'type': 'double', 'active': True})

    # Section 2
    add_platform(600, Y_MIN+60, 120, 100, CORRIDOR_Y-120, 22) # Ascending platform
    add_platform(750, Y_MIN+20, 160, 100, CORRIDOR_Y-40, 22)  # Higher platform with enemy
    add_platform(950, Y_MIN, 120, 120, CORRIDOR_Y, 22)

    # Section 3: Dash Power-Up
    POWERUPS.append({'aabb': AABB3(1000, 0, 150, 24, 24, 24), 'type': 'dash', 'active': True})
    add_platform(1300, Y_MIN, 110, 150, CORRIDOR_Y, 22)      # Landing platform after big gap

    # Section 4
    add_platform(1500, Y_MIN, 20, 400, CORRIDOR_Y, 22) 
    SPIKES.append(AABB3(1550, Y_MIN, 23, 80, CORRIDOR_Y, 16))
    SPIKES.append(AABB3(1700, Y_MIN, 23, 80, CORRIDOR_Y, 16))
    add_platform(1950, Y_MIN+50, 60, 80, CORRIDOR_Y-100, 22) 

    # Section 5: Wall-Jump Tower
    add_platform(2100, Y_MIN, 0, 20, CORRIDOR_Y, 120)        # Left Wall
    add_platform(2180, Y_MIN, 0, 20, CORRIDOR_Y, 120)        # Right Wall
    add_platform(2250, Y_MIN+80, 200, 50, 50, 22)           # platfrm after tower
    add_platform(2100, Y_MIN, 120, 100, CORRIDOR_Y, 22)      # Top of the tower

    # Section 6: moving platforms
    add_moving_platform(2300, Y_MIN+80, 280, 80, 80, 22, 2300, 2450, 60)
    add_platform(2700, Y_MIN, 260, 150, CORRIDOR_Y, 22)      # Final landing 

    # decor platforms
    i=0
    while i<3000:
      
       add_moving_platform(i, Y_MIN-random.randint(150,300), random.randint(150,250), random.randint(60,150),random.randint(60,100),random.randint(16,40),i,i+70, random.randint(30,90))
     
       i+=300
       
    i=100
    while i<3000:
      
       add_moving_platform(i, Y_MIN-random.randint(200,350), random.randint(300,350), random.randint(60,150),random.randint(60,100),random.randint(16,40),i,i+70,random.randint(30,90))
      
       i+=200
       
    
    # FIN
    GOAL = AABB3(3000, -60, 282, 100, 120, 20)
    add_platform(GOAL.x, Y_MIN, GOAL.z-6, GOAL.w, CORRIDOR_Y, 6)

    # Spikes covering the entire floor
    SPIKES.clear() 
    floor_width = 2900
    for x in range(0, floor_width, 40):
        is_on_platform = False
        for p in PLATFORMS:
            if x + 40 > p.x and x < p.x + p.w:
                 if p.z <= 0:
                    is_on_platform = True
                    break
        if not is_on_platform:
            SPIKES.append(AABB3(x, Y_MIN, 0, 40, CORRIDOR_Y, 16))



player = AABB3(80, -20, 60, 34, 28, 60)
vx, vy, vz = 0.0, 0.0, 0.0
SPEED = 80
ACCEL = 100.0
FRICTION = 80.0
GRAV = -280.0
JUMP_V = 160.0
MAX_FALL = -300.0

# jump 
jump_buffer_time = 0.12  # seconds
coyote_time_max  = 0.12
jump_buffer = 0.0
coyote_time = 0.0
jump_count = 0           # for double jump

# dash
dash_time = 0.0
DASH_TIME = .2
DASH_SPEED = 400.0
dash_cd = 0.0
DASH_CD_MAX = 0.7
can_dash = False
can_double = False

# combat
SPELL_CHARGE_MAX = 9
spell_charge = 0
bullets = [] 

SLASH_TIME = 0.16
SLASH_CD_MAX = 0.5
slash_cd = 0.0
slashes = []  

# health + i-frames
hp = 5
hurt_timer = 0.0
HURT_IFRAMES = 0.6

# facing
facing = 1

# state machine
STATE_TITLE, STATE_RUN, STATE_PAUSE, STATE_END, STATE_OVER = 0,1,2,3,4
game_state = STATE_TITLE
camera_mode = 0 # 0 for default, 1 for angled view

# Player state
player = AABB3(80, -20, 60, 34, 28, 60)
vx, vy, vz = 0.0, 0.0, 0.0
SPEED = 80
ACCEL = 100.0
FRICTION = 80.0
GRAV = -280.0
JUMP_V = 160.0
MAX_FALL = -300.0


class Enemy:
    def __init__(self, x, y, z, w, d, h, dir, xmin, xmax, hp=2, move_axis='y'):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.d = d
        self.h = h
        self.dir = dir
        self.xmin = xmin
        self.xmax = xmax
        self.hp = hp
        self.move_axis = move_axis

enemies = []

def spawn_enemies():
    enemies.clear()
    # Section 1
    enemies.append(Enemy(450, Y_MIN, 102, 26, 32, 28, +1, Y_MIN, Y_MAX))
    # Section 2
    enemies.append(Enemy(760, Y_MIN+20, 182, 26, 32, 28, +1, Y_MIN+20, Y_MAX-20))
    enemies.append(Enemy(950, Y_MIN, 142, 26, 32, 28, -1, Y_MIN, Y_MAX))
    # Section 3
    enemies.append(Enemy(1320, Y_MIN, 132, 26, 32, 28, -1, Y_MIN, Y_MAX))
    # Section 4 
    enemies.append(Enemy(1550, Y_MIN+100, 42, 28, 36, 32, +1, 1520, 1880, move_axis='x'))
    enemies.append(Enemy(1800, Y_MIN, 42, 28, 36, 32, -1, Y_MIN, Y_MAX))
    # Section 5 
    enemies.append(Enemy(2120, Y_MIN+100, 142, 28, 36, 32, +1, 2100, 2180, move_axis='x'))
    # Section 6 
    enemies.append(Enemy(2710, Y_MIN, 282, 28, 36, 32, +1, Y_MIN, Y_MAX))
    enemies.append(Enemy(2750, Y_MIN+100, 282, 28, 36, 32, -1, 2700, 2850, move_axis='x'))


def draw_text_2d(x,y,msg,font=GLUT_BITMAP_HELVETICA_18):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(1,1,1)
    glRasterPos2f(x,y)
    for ch in msg: glutBitmapCharacter(font, ord(ch))
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_box(a: AABB3, color=(0.18,0.18,0.20)):
    glColor3f(*color)
    x,y,z,w,d,h = a.x,a.y,a.z,a.w,a.d,a.h
    glBegin(GL_QUADS)
    # bottom
    glVertex3f(x,y,z); glVertex3f(x+w,y,z); glVertex3f(x+w,y+d,z); glVertex3f(x,y+d,z)
    # top
    glVertex3f(x,y,z+h); glVertex3f(x+w,y,z+h); glVertex3f(x+w,y+d,z+h); glVertex3f(x,y+d,z+h)
    glEnd()
    glBegin(GL_QUADS)
    # front/back/left/right
    glVertex3f(x,y+d,z); glVertex3f(x+w,y+d,z); glVertex3f(x+w,y+d,z+h); glVertex3f(x,y+d,z+h)
    glVertex3f(x,y,z);   glVertex3f(x+w,y,z);   glVertex3f(x+w,y,z+h);   glVertex3f(x,y,z+h)
    glVertex3f(x,y,z);   glVertex3f(x,y+d,z);   glVertex3f(x,y+d,z+h);   glVertex3f(x,y,z+h)
    glVertex3f(x+w,y,z); glVertex3f(x+w,y+d,z); glVertex3f(x+w,y+d,z+h); glVertex3f(x+w,y,z+h)
    glEnd()

def draw_checker_floor():
    size_x, size_y = 5000, 600
    tile = 120.0
    x0, y0 = -200, -size_y/2
    nx, ny = int(size_x/tile), int(size_y/tile)
    glBegin(GL_QUADS)
    for i in range(nx):
        for j in range(ny):
            x = x0 + i*tile; y = y0 + j*tile
            glColor3f(176/255,191/255,26/255)
            glVertex3f(x,y,0); glVertex3f(x+tile,y,0); glVertex3f(x+tile,y+tile,0); glVertex3f(x,y+tile,0)
    glEnd()

def draw_spikes():
    for s in SPIKES:
        cols = max(1, int(s.w//26)); rows = max(1, int(s.d//26))
        for i in range(cols):
            for j in range(rows):
                cx = s.x + 13 + i*26
                cy = s.y + 13 + j*26
                glPushMatrix()
                glTranslatef(cx, cy, s.z)
                glColor3f(139/255,0,0)
                q = gluNewQuadric()
                gluCylinder(q, 7.0, 0.0, s.h, 10, 1) 
                glPopMatrix()

def draw_player():
    glPushMatrix()
    glTranslatef(player.x + player.w/2, player.y + player.d/2, player.z)
    ang = 0 if facing>0 else 180
    glRotatef(ang, 0,0,1)

    # legs
    glColor3f(0.10,0.10,0.10)
    glPushMatrix(); glTranslatef(0,-8,  12); glutSolidCube(22); glPopMatrix()
    glPushMatrix(); glTranslatef( 0, 8, 12); glutSolidCube(22); glPopMatrix()

    # torso
    glColor3f(0.49,0.39,0.50)
    glPushMatrix(); glTranslatef(0,0,36); glutSolidCube(30); glPopMatrix()

    # head
    glColor3f(0.05,0.05,0.05)
    glPushMatrix(); glTranslatef(0,0,62); gluSphere(gluNewQuadric(), 12, 16, 12); glPopMatrix()

    # sword
    glColor3f(0.85,0.85,0.95)
    glPushMatrix()
    glTranslatef(10,15,42)
    glRotatef(45, 0, -1, 0) 
    glScalef(42,4,4)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()

def draw_enemy(e: 'Enemy'):
    if e.hp <= 0: return
    glPushMatrix()
    glTranslatef(e.x + e.w/2, e.y + e.d/2, e.z + e.h/2)
    glColor3f(139/255,0,0)
    glutSolidCube(int(max(e.w, e.h)))
    glPopMatrix()

def draw_bullets():
    glColor3f(1.0,1.0,1.0)
    for b in bullets:
        glPushMatrix()
        glTranslatef(b['x'], b['y'], b['z'])
        glutSolidCube(28)
        glPopMatrix()

def draw_slashes():
    glColor3f(1.0,1.0,0.3)
    for s in slashes:
        a = s['aabb']
        glPushMatrix()
        glTranslatef(a.x + a.w/2, a.y + a.d/2, a.z + a.h/2)
        glScalef(a.w, a.d, a.h)
        glutSolidCube(1)
        glPopMatrix()

def draw_overlay(alpha):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, alpha)
    
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WIN_W, 0)
    glVertex2f(WIN_W, WIN_H)
    glVertex2f(0, WIN_H)
    glEnd()
    
    glDisable(GL_BLEND)
    
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def setup_camera():
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()

    if camera_mode == 0:
        # side view
        gluPerspective(FOVY, ASPECT, NEAR_Z, FAR_Z)
        target_eye = [ player.x, player.y + 500, player.z + 80 ] 
        target_tgt = [ player.x, player.y, player.z + 40 ]        # look at player
    else: # camera_mode == 1
        # angled view
        gluPerspective(25, ASPECT, NEAR_Z, FAR_Z)
        target_eye = [ player.x - 400, player.y + 400, player.z + 300 ]
        target_tgt = [ player.x, player.y, player.z + 40 ]

    for i in range(3):
        cam_pos[i] = cam_pos[i] + SMOOTH * (target_eye[i] - cam_pos[i])
        cam_tgt[i] = cam_tgt[i] + SMOOTH * (target_tgt[i] - cam_tgt[i])

    gluLookAt(cam_pos[0],cam_pos[1],cam_pos[2],
              cam_tgt[0],cam_tgt[1],cam_tgt[2],
              0,0,1)

def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    setup_camera()


    sun_dir = [cam_tgt[i] - cam_pos[i] for i in range(3)]
    sun_len = math.sqrt(sum(x*x for x in sun_dir))
    if sun_len == 0: sun_len = 1
    sun_dir = [x/sun_len for x in sun_dir]

    sun_pos = [
        cam_tgt[0] + sun_dir[0]*1200,
        cam_tgt[1] + sun_dir[1]*1200-450,
        cam_tgt[2] + sun_dir[2]*1200 +  450]
    
    glPushMatrix()
    glTranslatef(*sun_pos)
    glColor3f(1.0, 0.95, 0.3)
    glutSolidSphere(90, 32, 24)
    glPopMatrix()

    draw_checker_floor()
    for p in PLATFORMS: draw_box(p, (183/255,65/255,14/255)) 
    for mp in MOVING_PLATFORMS:

        if mp.aabb.y <= -200:
            draw_box(mp.aabb, (random.uniform(0.7,1.0),random.uniform(0.7,1.0),random.uniform(0.7,1.0))) 
        else:
            draw_box(mp.aabb, (183/255,65/255,14/255))  
            

    for pu in POWERUPS:
        if pu['active']:
            color = (0.2,0.9,0.2) if pu['type']=='dash' else (0.2,0.2,0.9)
            draw_box(pu['aabb'], color)
    draw_spikes()

    for e in enemies: draw_enemy(e)
    draw_bullets()
    draw_slashes()
    draw_player()

    draw_hud()
    glutSwapBuffers()

def draw_hud():
    display_hp = '*' * hp
    draw_text_2d(10, WIN_H-26, f'Lives: {display_hp} | Spell: {spell_charge}/{SPELL_CHARGE_MAX} |  Dash: {"Yes" if can_dash else "No"} | DoubleJump: {"Yes" if can_double else "No"}')
    draw_text_2d(10, WIN_H-56, 'Green Cube: Dash (S) | Blue Cube: DoubleJump (W) | Sword: Slash (J) | Spell: (K)')
    if game_state == STATE_TITLE:
        draw_text_2d(WIN_W//2-180, WIN_H//2+30, '                              Blorp')
        draw_text_2d(WIN_W//2-320, WIN_H//2-10, 'W/Space=Jump/Double Jump  A/D=Move  L=Dash  K=Spell  J=Slash  P=Pause')
        draw_text_2d(WIN_W//2-160, WIN_H//2-50, '             Press SPACE to Start')
        draw_overlay(0.5)
    elif game_state == STATE_PAUSE:
        draw_text_2d(WIN_W//2-60, WIN_H//2, 'PAUSED (SPACE to Resume)')
        draw_overlay(0.5)
    elif game_state == STATE_END:
        draw_text_2d(WIN_W//2-110, WIN_H//2, 'YOU REACHED THE GOAL! (SPACE)')
        draw_overlay(0.5)
    elif game_state == STATE_OVER:
        draw_text_2d(WIN_W//2-80, WIN_H//2, 'GAME OVER (SPACE)')
        draw_overlay(0.5)

# Inputs

left_hold = right_hold = False
want_jump = False

def keyboard_down(key,x,y):
    global game_state, left_hold, right_hold, want_jump, facing, camera_mode
    if key == b' ':
        if game_state in (STATE_TITLE, STATE_END, STATE_OVER): reset_game(); set_state(STATE_RUN); return
        if game_state == STATE_PAUSE: set_state(STATE_RUN); return
    if key in (b'p', b'P'):
        if game_state == STATE_RUN: set_state(STATE_PAUSE)
        elif game_state == STATE_PAUSE: set_state(STATE_RUN)
        return
    if key in (b'c', b'C'):
        camera_mode = 1 - camera_mode # Toggle 0 1
        return
    if game_state != STATE_RUN: return

    if key in (b'a', b'A'): right_hold = True;  facing = +1
    if key in (b'd', b'D'): left_hold = True; facing = -1
    if key in (b'w', b'W', b' '): buffer_jump()

    if key in (b'l', b'L'): try_dash()
    if key in (b'k', b'K'): try_spell()
    if key in (b'j', b'J'): try_slash()

def keyboard_up(key,x,y):
    global left_hold, right_hold
    if key in (b'a', b'A'): right_hold = False
    if key in (b'd', b'D'): left_hold = False

def special_down(k,x,y):
    if k == GLUT_KEY_LEFT:  keyboard_down(b'a',x,y)
    if k == GLUT_KEY_RIGHT: keyboard_down(b'd',x,y)
    if k == GLUT_KEY_UP:    keyboard_down(b'w',x,y)
    if k == GLUT_KEY_DOWN:  keyboard_down(b's',x,y)

def special_up(k,x,y):
    if k == GLUT_KEY_LEFT:  keyboard_up(b'a',x,y)
    if k == GLUT_KEY_RIGHT: keyboard_up(b'd',x,y)

# Abilities

def set_state(s):
    global game_state
    game_state = s

def buffer_jump():
    global jump_buffer
    jump_buffer = jump_buffer_time

def do_jump():
    global vz, jump_count, coyote_time
    vz = JUMP_V
    jump_count += 1
    coyote_time = 0.0

def try_dash():
    global dash_time, dash_cd
    if can_dash and dash_cd <= 0.0 and dash_time <= 0.0:
        dash_time = DASH_TIME
        dash_cd = DASH_CD_MAX

def try_spell():
    global spell_charge
    if spell_charge >= 3:
        dirx = 1.0 if facing>0 else -1.0
        bullets.append({'x': player.x + player.w/2 + dirx*26,
                        'y': player.y + player.d/2,
                        'z': player.z + 28,
                        'vx': dirx*160.0, 'vy': 0.0, 'vz': 0.0, 'life': 2.5})
        spell_charge -= 3

def try_slash():
    global slash_cd
    if slash_cd <= 0.0:
        fw, fd, fh = 54.0, 32.0, 32.0
        ox = player.x + (player.w/2 + (40 if facing>0 else -40)) - fw/2
        oy = player.y + player.d/2 - fd/2
        oz = player.z + 18
        slashes.append({'aabb': AABB3(ox, oy, oz, fw, fd, fh), 't': SLASH_TIME})
        slash_cd = SLASH_CD_MAX


# Physics ( 60 FPS )

FIXED_DT = 1.0/60.0
accum = 0.0
last_t = time.perf_counter()

def move_and_collide_axis(box: AABB3, dx, dy, dz):
   
    nx, ny, nz = box.x + dx, box.y + dy, box.z + dz 
    res = AABB3(nx, ny, nz, box.w, box.d, box.h)
    hit_left = hit_right = hit_floor = hit_ceiling = False
    
    
    all_platforms = PLATFORMS + [mp.aabb for mp in MOVING_PLATFORMS] # same collition for both platforms

    for p in all_platforms:
        if not aabb3_overlap(res, p): continue
       
        if dx != 0:
            if dx > 0: 
                res.x = p.x - box.w
                hit_right = True
            else:       
                res.x = p.x + p.w
                hit_left = True
        elif dy != 0:
            if dy > 0:  res.y = p.y - box.d
            else:       res.y = p.y + p.d
        elif dz != 0:
            if dz > 0:
                res.z = p.z - box.h; hit_ceiling = True
            else:
                res.z = p.z + p.h;   hit_floor = True
    return res, hit_left, hit_right, hit_floor, hit_ceiling

def physics_step(dt):
    global vx, vy, vz, player, jump_buffer, coyote_time, jump_count, game_state
    global dash_time, dash_cd, spell_charge, slash_cd
    global hp, hurt_timer, facing, can_dash, can_double
    if game_state != STATE_RUN: return


    for mp in MOVING_PLATFORMS:
        mp.aabb.x += mp.dir * mp.speed * dt
        if mp.dir > 0 and mp.aabb.x > mp.x_end:
            mp.aabb.x = mp.x_end
            mp.dir = -1
        elif mp.dir < 0 and mp.aabb.x < mp.x_start:
            mp.aabb.x = mp.x_start
            mp.dir = 1

    # timers
    if jump_buffer>0: jump_buffer -= dt
    if coyote_time>0: coyote_time -= dt
    if dash_cd>0: dash_cd -= dt
    if slash_cd>0: slash_cd -= dt
    if hurt_timer>0: hurt_timer -= dt

    # horizontal input
    if dash_time > 0:
        target_vx = DASH_SPEED * (1 if facing>0 else -1)
        vx = target_vx
        dash_time -= dt
    else:
        target = 0.0
        if left_hold:  target -= SPEED
        if right_hold: target += SPEED
        
        # acceleration/friction logic
        factor = ACCEL if target != 0 else FRICTION
        vx += (target - vx) * min(1.0, factor * dt)
        if abs(vx) < 0.1: vx = 0.0

    # gravity
    vz += GRAV * dt
    if vz < MAX_FALL: vz = MAX_FALL

    # Move & collide X then Y then Z
    # X
    new_box, hitL, hitR, _, _ = move_and_collide_axis(player, vx*dt, 0, 0)
    player = new_box
    if hitL or hitR:
        vx = 0.0

    # clamp to Y
    ny = min(max(player.y + vy*dt, Y_MIN), Y_MAX - player.d)
    player = AABB3(player.x, ny, player.z, player.w, player.d, player.h)

    # Z
    prev_z = player.z
    new_box, _, _, hitF, hitC = move_and_collide_axis(player, 0, 0, vz*dt)
    player = new_box
    grounded = False
    
    # Carry player on moving platform
    platform_dx = 0.0
    if vz <= 0: # Only check for ground if moving down or still
        player_feet = AABB3(player.x, player.y, player.z - 0.1, player.w, player.d, 0.1)
        for mp in MOVING_PLATFORMS:
            if aabb3_overlap(player_feet, mp.aabb):
                platform_dx = mp.dir * mp.speed * dt
                player.x += platform_dx
                break

    if hitF and vz <= 0:
        grounded = True
        vz = 0.0
        coyote_time = coyote_time_max
        jump_count = 0
    
    if hitC and vz > 0:
        vz = 0.0



    if jump_buffer > 0:
        if grounded or coyote_time > 0:
            do_jump()
            jump_buffer = 0.0
        elif jump_count == 1 and can_double: 
            do_jump()
            jump_buffer = 0.0

    # power-ups
    for p in POWERUPS:
        if p['active'] and aabb3_overlap(player, p['aabb']):
            if p['type'] == 'dash':
                can_dash = True
            elif p['type'] == 'double':
                can_double = True
            p['active'] = False

    # spikes damage
    for s in SPIKES:
        if aabb3_overlap(player, s):
            set_state(STATE_OVER)
            break

    # bullets update
    for b in bullets[:]:
        b['x'] += b['vx'] * dt
        b['y'] += b['vy'] * dt
        b['z'] += b['vz'] * dt
        b['life'] -= dt
        if b['life'] <= 0:
            bullets.remove(b); continue
        # collide with enemies
        for e in enemies:
            if e.hp <= 0: continue
            if aabb3_overlap(AABB3(b['x']-14,b['y']-14,b['z']-14,28,28,28),
                             AABB3(e.x,e.y,e.z,e.w,e.d,e.h)):
                e.hp = 0 # Spell does 2 damage
                if b in bullets: bullets.remove(b)
                break

    # slashes
    for s in slashes[:]:
        s['t'] -= dt
        if s['t'] <= 0:
            slashes.remove(s); continue
        for e in enemies:
            if e.hp <= 0: continue
            if aabb3_overlap(s['aabb'], AABB3(e.x,e.y,e.z,e.w,e.d,e.h)):
                e.hp -= 1
                if spell_charge < SPELL_CHARGE_MAX:
                    spell_charge += 1
                if s in slashes: slashes.remove(s) # prevent multi-hit
                break

    # enemy patrol + contact (move along Y axis)
    for e in enemies:
        if e.hp <= 0: continue
        if e.move_axis == 'y':
            e.y += e.dir * 90.0 * dt
            if e.y < e.xmin: e.y = e.xmin; e.dir = +1
            if e.y + e.d > e.xmax: e.y = e.xmax - e.d; e.dir = -1
        else: # move_axis == 'x'
            e.x += e.dir * 90.0 * dt
            if e.x < e.xmin: e.x = e.xmin; e.dir = +1
            if e.x + e.w > e.xmax: e.x = e.xmax - e.w; e.dir = -1
        
        if aabb3_overlap(player, AABB3(e.x,e.y,e.z,e.w,e.d,e.h)) and hurt_timer <= 0.0:
            hp -= 1
            hurt_timer = HURT_IFRAMES

    # end / death
    if aabb3_overlap(player, GOAL):
        set_state(STATE_END)
    if hp <= 0 or player.z < -80:
        set_state(STATE_OVER)

def fixed_update():
    global accum, last_t
    t = time.perf_counter()
    dt = t - last_t
    last_t = t
    if dt > 0.1: dt = 0.1
    accum += dt
    while accum >= FIXED_DT:
        physics_step(FIXED_DT)
        accum -= FIXED_DT


def idle():
    fixed_update()
    draw_scene()
    glutPostRedisplay()

def init_gl():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.53, 0.81, 0.92, 1.0)

def reset_game():
    global player, vx, vy, vz, jump_buffer, coyote_time, jump_count, game_state
    global dash_time, dash_cd, spell_charge, slash_cd, hurt_timer, hp, facing, can_dash, can_double
    player = AABB3(80, -20, 60, 34, 28, 60)
    vx=vy=vz=0.0
    jump_buffer=0.0; coyote_time=0.0; jump_count=0
    dash_time=0.0; dash_cd=0.0
    spell_charge=0; slash_cd=0.0
    hurt_timer=0.0; hp=5
    facing = +1
    can_dash = False
    can_double = False
    build_level()
    spawn_enemies()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutCreateWindow(b'3D Platformer - Polished (Assignments-based)')
    init_gl()
    reset_game()
    glutDisplayFunc(draw_scene)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutMainLoop()

if __name__ == '__main__':
    main()