from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

camera_pos = (0, 500, 500)
fovY = 120
GRID_LENGTH = 600
rand_var = 423

player_x, player_y = 0, 0
player_angle = 90
player_life = 5
score = 0
missed = 0
game_over = False

bullets = []
enemies = []
cam_angle = 90
cam_height = 500
cam_radius = 500

fp_mode = False
cheat_mode = False
auto_cam = False
cooldown = 0

def init_enemies():
    global enemies
    enemies = []
    for _ in range(5):
        spawn_enemy()

def spawn_enemy(e=None):
    ex = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
    ey = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
    if e is None:
        enemies.append({'x': ex, 'y': ey, 'scale': 1.0, 'scale_dir': 0.02})
    else:
        e['x'] = ex
        e['y'] = ey

init_enemies()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_shapes():
    global player_x, player_y, player_angle, game_over
    global enemies, bullets

    for b in bullets:
        glPushMatrix()
        glTranslatef(b['x'], b['y'], 10)
        glColor3f(1, 1, 0)
        glutSolidCube(10)
        glPopMatrix()

    for e in enemies:
        glPushMatrix()
        glTranslatef(e['x'], e['y'], 20)
        glScalef(e['scale'], e['scale'], e['scale'])
        
        glColor3f(1, 0, 0) 
        gluSphere(gluNewQuadric(), 20, 16, 16)
        
        glTranslatef(0, 0, 22)
        glColor3f(0, 0, 0) 
        gluSphere(gluNewQuadric(), 12, 16, 16)
        glPopMatrix()

    glPushMatrix()
    glTranslatef(player_x, player_y, 0)
    
    if game_over:
        glRotatef(90, 1, 0, 0) 
        glTranslatef(0, 0, 20)

    glRotatef(player_angle - 90, 0, 0, 1)

    glColor3f(0, 0, 1)
    glPushMatrix()
    glTranslatef(-10, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 6, 25, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(10, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 6, 25, 10, 10)
    glPopMatrix()

    glTranslatef(0, 0, 35)
    glColor3f(0.4, 0.5, 0.2)
    glPushMatrix()
    glScalef(1.2, 0.6, 1.2)
    glutSolidCube(25)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, 20)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 12, 16, 16)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 15, -5)
    glColor3f(0.7, 0.7, 0.7)
    glRotatef(90, -1, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 3, 35, 10, 10)
    glPopMatrix()

    glPopMatrix()

def keyboardListener(key, x, y):
    global player_x, player_y, player_angle, cheat_mode, auto_cam, game_over
    global player_life, score, missed, bullets

    if key == b'r':
        player_life = 5
        score = 0
        missed = 0
        game_over = False
        player_x, player_y = 0, 0
        player_angle = 90
        bullets = []
        cheat_mode = False
        init_enemies()
        return

    if game_over:
        return

    speed = 10

    if key == b'w':  
        new_x = player_x + math.cos(math.radians(player_angle)) * speed
        new_y = player_y + math.sin(math.radians(player_angle)) * speed
        if abs(new_x) < GRID_LENGTH - 20 and abs(new_y) < GRID_LENGTH - 20:
            player_x, player_y = new_x, new_y

    if key == b's':
        new_x = player_x - math.cos(math.radians(player_angle)) * speed
        new_y = player_y - math.sin(math.radians(player_angle)) * speed
        if abs(new_x) < GRID_LENGTH - 20 and abs(new_y) < GRID_LENGTH - 20:
            player_x, player_y = new_x, new_y

    if key == b'a':
        player_angle += 5

    if key == b'd':
        player_angle -= 5

    if key == b'c':
        cheat_mode = not cheat_mode

    if key == b'v':
        auto_cam = not auto_cam


def specialKeyListener(key, x, y):
    global cam_angle, cam_height

    if key == GLUT_KEY_UP:
        cam_height += 15

    if key == GLUT_KEY_DOWN:
        cam_height -= 15

    if key == GLUT_KEY_LEFT:
        cam_angle += 5 

    if key == GLUT_KEY_RIGHT:
        cam_angle -= 5 

def mouseListener(button, state, x, y):
    global fp_mode, bullets, game_over

    if game_over:
        return

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        bullets.append({
            'x': player_x + math.cos(math.radians(player_angle)) * 20, 
            'y': player_y + math.sin(math.radians(player_angle)) * 20, 
            'angle': player_angle
        })

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        fp_mode = not fp_mode


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    gluPerspective(fovY, 1.25, 0.1, 1500) 
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if fp_mode:
        cam_x = player_x
        cam_y = player_y
        cam_z = 60

        look_angle = player_angle
        if cheat_mode and not auto_cam:
            look_angle = 90

        look_x = player_x + math.cos(math.radians(look_angle)) * 100
        look_y = player_y + math.sin(math.radians(look_angle)) * 100
        look_z = 50

        gluLookAt(cam_x, cam_y, cam_z,  
                  look_x, look_y, look_z,  
                  0, 0, 1)  
    else:
        cx = cam_radius * math.cos(math.radians(cam_angle))
        cy = cam_radius * math.sin(math.radians(cam_angle))
        
        gluLookAt(cx, cy, cam_height,
                  0, 0, 0,
                  0, 0, 1)  


def idle():
    global player_life, score, missed, game_over, player_angle, cooldown
    global enemies, bullets

    if game_over:
        glutPostRedisplay()
        return

    for e in enemies:
        dx = player_x - e['x']
        dy = player_y - e['y']
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            e['x'] += (dx/dist) * 1.5
            e['y'] += (dy/dist) * 1.5

        e['scale'] += e['scale_dir']
        if e['scale'] > 1.3 or e['scale'] < 0.7:
            e['scale_dir'] *= -1

        if dist < 40: 
            player_life -= 1
            if player_life <= 0:
                game_over = True
            spawn_enemy(e)

    for b in bullets[:]:
        b['x'] += math.cos(math.radians(b['angle'])) * 20
        b['y'] += math.sin(math.radians(b['angle'])) * 20

        if abs(b['x']) > GRID_LENGTH or abs(b['y']) > GRID_LENGTH:
            missed += 1
            bullets.remove(b)
            if missed >= 10:
                game_over = True
            continue

        for e in enemies:
            if math.hypot(b['x'] - e['x'], b['y'] - e['y']) < 35:
                score += 10
                bullets.remove(b)
                spawn_enemy(e)
                break

    if cheat_mode:
        player_angle += 3
        cooldown -= 1

        if cooldown <= 0:
            for e in enemies:
                angle_to_enemy = math.degrees(math.atan2(e['y'] - player_y, e['x'] - player_x))
                
                diff = (player_angle - angle_to_enemy) % 360
                if diff > 180: diff -= 360
                
                if abs(diff) < 10: 
                    bullets.append({'x': player_x, 'y': player_y, 'angle': player_angle})
                    cooldown = 10
                    break

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    size = 60
    for i in range(-GRID_LENGTH, GRID_LENGTH, size):
        for j in range(-GRID_LENGTH, GRID_LENGTH, size):
            if ((i // size) + (j // size)) % 2 == 0:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0.7, 0.5, 0.95)
            
            glBegin(GL_QUADS)
            glVertex3f(i, j, 0)
            glVertex3f(i + size, j, 0)
            glVertex3f(i + size, j + size, 0)
            glVertex3f(i, j + size, 0)
            glEnd()

    wall_h = 50
    glColor3f(0, 1, 1)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_h)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_h)
    glEnd()

    glColor3f(0, 0, 1)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_h)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_h)
    glEnd()

    glColor3f(0, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_h)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_h)
    glEnd()

    glColor3f(0.8, 0.8, 0) 
    glBegin(GL_QUADS)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_h)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_h)
    glEnd()

    draw_shapes()

    draw_text(10, 770, f"Player Life Remaining: {player_life}")
    draw_text(10, 740, f"Game Score: {score}")
    draw_text(10, 710, f"Player Bullet Missed: {missed}")
    if game_over:
        draw_text(400, 400, "GAME OVER! Press 'R' to Restart.")

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Bullet Frenzy - 3D Game")

    glEnable(GL_DEPTH_TEST)
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()