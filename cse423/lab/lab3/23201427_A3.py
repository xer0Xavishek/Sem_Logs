from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math, time, random

PROJ_VEL=9999
CHASE_VEL= 42
THROB_RATE= 0.08
MOB_LO=16
MOB_HI=23
MOB_CAP =6
MISS_CAP=10
INIT_HP =5
SCR_W=1200
SCR_H=960

g_over=False
g_frenzy=False
rounds=[]
actv_mobs= []
hp=5
misses=0
score=0
clk =time.perf_counter()

orbit_r =500
orbit_z =500
orbit_deg= 0
view_mode= "3rd"
fov =100
lock_deg=0

hx, hy, hz= 0, 0, 0
facing=0 
step_d=18 
step_r=9 

swept=[]  
vcam=False 



def draw_text(x, y, msg, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, SCR_W, 0, SCR_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in msg:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_player():
    glPushMatrix()
    glTranslatef(hx, hy, hz)
    glScalef(0.65, 0.65, 0.65)

    if g_over:
        glRotatef(90, 1, 0, 0)
    else:
        glRotatef(facing, 0, 0, 1)

    # torso 
    glPushMatrix()
    glColor3f(85/255, 107/255, 46/255)
    glScalef(2, 1, 2)
    glTranslatef(0, 0, 25)
    glutSolidCube(33)
    glPopMatrix()

    # legs 
    glColor3f(0.0, 0.0, 1.0)
    for side in (-20, 20):
        glPushMatrix()
        glTranslatef(side, 0, -30)
        gluCylinder(gluNewQuadric(), 5, 15, 50, 10, 10)
        glPopMatrix()

    # head
    glPushMatrix()
    glColor3f(0, 0, 0)
    glTranslatef(0, 0, 99)
    gluSphere(gluNewQuadric(), 22, 12, 12)
    glPopMatrix()

    # arms
    glColor3f(255/255, 224/255, 189/255)
    for side in (-30, 30):
        glPushMatrix()
        glTranslatef(side, 0, 66)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 10, 5, 50, 15, 10)
        glPopMatrix()

    # gun barrel
    glPushMatrix()
    glColor3f(192/255, 192/255, 192/255)
    glTranslatef(0, 0, 66)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 5, 75, 15, 10)
    glPopMatrix()

    glPopMatrix()

def draw_grid():
    n =20
    tsz= SCR_W / n
    orig= -SCR_W / 2

    for r in range(n):
        for c in range(n):
            glColor3f(1.0, 1.0, 1.0) if (r + c) % 2 == 0 else glColor3f(0.7, 0.5, 0.95)
            x0 = orig + c * tsz;  x1 = x0 + tsz
            y0 = orig + r * tsz;  y1 = y0 + tsz
            glBegin(GL_QUADS)
            glVertex3f(x0, y0, 0); glVertex3f(x1, y0, 0)
            glVertex3f(x1, y1, 0); glVertex3f(x0, y1, 0)
            glEnd()


def draw_boundary():
    e = SCR_W // 2 
    h = 99
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.0, 1.0) 
    glVertex3f(-e,-e,0); glVertex3f(-e, e,0)
    glVertex3f(-e, e,h); glVertex3f(-e,-e,h)

    glColor3f(0.0, 1.0, 0.0)
    glVertex3f( e, e,0); glVertex3f( e,-e,0)
    glVertex3f( e,-e,h); glVertex3f( e, e,h)

    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(-e, e,0); glVertex3f( e, e,0)
    glVertex3f( e, e,h); glVertex3f(-e, e,h)

    glColor3f(0.10, 0.60, 0.70)
    glVertex3f( e,-e,0); glVertex3f(-e,-e,0)
    glVertex3f(-e,-e,h); glVertex3f( e,-e,h)
    glEnd()


def draw_bullets():
    glColor3f(1.0, 0.0, 0.0)
    for r in rounds:
        glPushMatrix()
        glTranslatef(*r["xyz"])
        glutSolidCube(22) 
        glPopMatrix()


def shoot_bullet():
    rad= math.radians(facing)
    nx=-math.sin(rad)
    ny= math.cos(rad)
    tip= 75

    rounds.append({
        "xyz": [hx + nx * tip, hy + ny * tip, 40],
        "spd": [nx * PROJ_VEL,  ny * PROJ_VEL,  0]
    })


def update_bullets(dt):
    global misses, score, g_over

    lim=SCR_W / 2
    remove = []
    hit=[]

    for r in rounds:
        vx, vy = r["spd"][0], r["spd"][1]
        steps= max(1, int(math.hypot(vx, vy) * dt / 50) + 1)
        sdx=vx * dt / steps
        sdy=vy * dt / steps

        oob = hit_flag = False

        for _ in range(steps):
            r["xyz"][0] += sdx
            r["xyz"][1] += sdy
            bx, by = r["xyz"][0], r["xyz"][1]

            if abs(bx) > lim or abs(by) > lim:
                oob = True;  break

            for m in actv_mobs:
                if math.hypot(bx - m["x"], by - m["y"]) < m["rad"] + 12:
                    hit_flag = True;  hit.append(m);  score += 1;  break

            if hit_flag:
                break

        if oob or hit_flag:
            remove.append(r)
            if oob:
                misses += 1
                if misses >= MISS_CAP:
                    g_over = True

    for r in remove:
        if r in rounds:
            rounds.remove(r)
    for m in hit:
        _respot(m)


def draw_enemies():
    q = gluNewQuadric()
    for m in actv_mobs:
        glPushMatrix()
        glTranslatef(m["x"], m["y"], m["rad"])
        sc = m["rad"] / 20.0
        glScalef(sc, sc, sc)
        glColor3f(1.0, 0.0, 0.0);  gluSphere(q, 40, 20, 20)   # body
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0, 0, 40);    gluSphere(q, 20, 20, 20)   # head
        glPopMatrix()


def _respot(m):
    while True:
        nx = random.randint(-450, 450)
        ny = random.randint(-450, 450)
        if math.hypot(hx - nx, hy - ny) > 222:
            m["x"] = nx;  m["y"] = ny
            m["rad"] = MOB_LO;  m["dir"] = 1
            return


def generate_enemies():
    actv_mobs.clear()
    for _ in range(MOB_CAP):
        while True:
            nx = random.randint(-450, 450)
            ny = random.randint(-450, 450)
            if math.hypot(nx - hx, ny - hy) > 222:
                actv_mobs.append({"x": nx, "y": ny, "rad": MOB_LO, "dir": 1})
                break

def update_enemies(dt):
    global hp, g_over

    if g_over:
        return

    for m in actv_mobs:
        dx= hx - m["x"];  dy = hy - m["y"]
        dist = math.hypot(dx, dy)

        if dist > 5:
            m["x"] += (dx / dist) * CHASE_VEL * dt
            m["y"] += (dy / dist) * CHASE_VEL * dt

        m["rad"] += m["dir"] * THROB_RATE * 120 * dt
        if   m["rad"] >= MOB_HI:  m["rad"] = MOB_HI;  m["dir"] = -1
        elif m["rad"] <= MOB_LO:  m["rad"] = MOB_LO;  m["dir"]=  1

        if dist < 70 + m["rad"]:
            hp -= 1
            if hp <= 0:
                g_over = True;  return
            _respot(m)


def setupCamera():
    glMatrixMode(GL_PROJECTION);  glLoadIdentity()
    gluPerspective(fov, SCR_W / SCR_H, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW);   glLoadIdentity()

    if view_mode == "3rd":
        ex = orbit_r * math.sin(math.radians(orbit_deg))
        ey = orbit_r * math.cos(math.radians(orbit_deg))
        gluLookAt(ex, ey, orbit_z,  0, 0, 0,  0, 0, 1)

    elif view_mode == "1st":
        ang = math.radians(lock_deg if (vcam and g_frenzy) else facing)
        lx= -math.sin(ang);  ly = math.cos(ang)
        gluLookAt(hx + lx*10,  hy + ly*10,  88,
                  hx + lx*250, hy + ly*250,  45,
                  0, 0, 1)


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, SCR_W, SCR_H)
    setupCamera()

    draw_grid()
    draw_boundary()
    draw_enemies()

    if not g_over:
        draw_bullets()
        draw_player()
        draw_text(10, 750, f"Player Life Remaining: {hp}")
        draw_text(10, 725, f"Game Score: {score}")
        draw_text(10, 700, f"Player Bullet Missed: {misses}")
    else:
        draw_player()
        draw_text(370, 730, f"Game Over!....... Score: {score}")
        draw_text(370, 700,  "Press  'R' to Restart the Game")

    glutSwapBuffers()


def keyboardListener(key, x, y):
    global clk, vcam, view_mode, hx, hy, hz, facing
    global g_over, score, misses, hp, orbit_deg, g_frenzy, lock_deg
    global rounds, actv_mobs

    k = key.decode("utf-8").lower()

    if not g_over:
        rad = math.radians(facing)
        if k == "w":
            hx += -math.sin(rad) * step_d
            hy +=  math.cos(rad) * step_d
        elif k == "s":
            hx -= -math.sin(rad) * step_d
            hy -=  math.cos(rad) * step_d
        elif k == "a":
            facing += step_r
        elif k == "d":
            facing -= step_r

        hx = max(-500, min(500, hx))
        hy = max(-500, min(500, hy))

    if k == "c":
        g_frenzy = not g_frenzy
        if not g_frenzy:
            vcam = False
            swept.clear()

    elif k == "v":
        if g_frenzy and view_mode == "1st":
            vcam = not vcam
            if vcam:
                lock_deg = facing

    elif k == "r" and g_over:
        rounds = [];  actv_mobs = []
        hp = INIT_HP;  misses = 0;  score = 0
        hx = 0;  hy = 0;  hz = 0;  facing = 0
        g_over = False;  g_frenzy = False;  vcam = False
        view_mode = "3rd";  clk = time.perf_counter()
        generate_enemies()

    glutPostRedisplay()


def specialKeyListener(key, x, y):
    global orbit_z, orbit_deg
    if key == GLUT_KEY_UP:    orbit_z   += 10
    if key == GLUT_KEY_DOWN:  orbit_z   -= 10
    if key == GLUT_KEY_LEFT:  orbit_deg += 1.1
    if key == GLUT_KEY_RIGHT: orbit_deg -= 1.1


def mouseListener(button, state, x, y):
    global view_mode
    if not g_over:
        if button == GLUT_LEFT_BUTTON  and state == GLUT_DOWN: shoot_bullet()
        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            view_mode = "1st" if view_mode == "3rd" else "3rd"


def idle():
    global clk, facing, g_frenzy, swept, vcam

    now= time.perf_counter()
    dt= now - clk
    clk= now

    if not g_over:
        update_bullets(dt)
        update_enemies(dt)

        if g_frenzy:
            facing += 769 * dt
            if facing >= 360:
                facing -= 360
                swept.clear()

            rad= math.radians(facing)
            dnx= -math.sin(rad)
            dny=  math.cos(rad)

            for m in actv_mobs:
                if m not in swept:
                    dx= m["x"] - hx;   dy = m["y"] - hy
                    dist = math.hypot(dx, dy)
                    if dist > 50:
                        px = hx + dist * dnx;  py = hy + dist * dny
                        if abs(m["x"] - px) < m["rad"] and abs(m["y"] - py) < m["rad"]:
                            swept.append(m);  shoot_bullet()

    glutPostRedisplay()



def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(SCR_W, SCR_H)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"23201427_Avishek Biswas_Bullet Frenzy Game")

    generate_enemies()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()
