from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
camera_pos = [0, 500, 500]
camera_angle = 0
camera_first_person = False
fovY = 60
GRID_LENGTH = 600
player_pos = [0, 0, 30]
gun_angle = 0
player_alive = True
life = 5
score = 0
bullets_missed = 0
game_over = False
cheat_mode = False
cheat_vision = False
cheat_fire_cooldown = 0
bullets = []
enemies = []
enemy_size_phase = 0
enemy_hit_cooldown = []
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1)):
    glColor3f(color[0], color[1], color[2])
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
def initialize_enemies():
    global enemies, enemy_hit_cooldown
    enemies = []
    enemy_hit_cooldown = []
    for _ in range(5):
        while True:
            x = random.uniform(-GRID_LENGTH + 150, GRID_LENGTH - 150)
            y = random.uniform(-GRID_LENGTH + 150, GRID_LENGTH - 150)
            if math.sqrt(x**2 + y**2) > 300:
                break
        enemies.append([x, y, 40])
        enemy_hit_cooldown.append(0)
def draw_player():
    global player_pos, gun_angle, player_alive, camera_first_person
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    if not player_alive:
        glRotatef(90, 1, 0, 0)
    glRotatef(-gun_angle, 0, 0, 1)
    if not camera_first_person:
        glPushMatrix()
        glTranslatef(-10, 0, -35)
        glColor3f(0.0, 0.0, 1.0)
        gluCylinder(gluNewQuadric(), 8, 8, 30, 10, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(10, 0, -35)
        glColor3f(0.0, 0.0, 1.0)
        gluCylinder(gluNewQuadric(), 8, 8, 30, 10, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glColor3f(0.2, 0.5, 0.2)
        glScalef(1.5, 1, 2)
        glutSolidCube(20)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(-15, 0, 5)
        glRotatef(90, 0, 1, 0)
        glColor3f(0.7, 0.7, 0.6)
        gluCylinder(gluNewQuadric(), 6, 6, 25, 10, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(15, 0, 5)
        glRotatef(-90, 0, 1, 0)
        glColor3f(0.7, 0.7, 0.6)
        gluCylinder(gluNewQuadric(), 6, 6, 25, 10, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0, 30)
        glColor3f(0.0, 1.0, 1.0)
        gluSphere(gluNewQuadric(), 12, 20, 20)
        glPopMatrix()
    glPopMatrix()
    angle_rad = math.radians(gun_angle)
    gun_dir_x = -math.sin(angle_rad)
    gun_dir_y = -math.cos(angle_rad)
    gun_start_x = player_pos[0]
    gun_start_y = player_pos[1]
    gun_start_z = player_pos[2] + 10
    gun_end_x = player_pos[0] + 50 * gun_dir_x
    gun_end_y = player_pos[1] + 50 * gun_dir_y
    gun_end_z = player_pos[2] + 10
    glColor3f(0.5, 0.5, 0.5)
    glLineWidth(8)
    glBegin(GL_LINES)
    glVertex3f(gun_start_x, gun_start_y, gun_start_z)
    glVertex3f(gun_end_x, gun_end_y, gun_end_z)
    glEnd()
    glLineWidth(1)
def draw_first_person_gun():
    global gun_angle
    glPushMatrix()
    glTranslatef(30, 40, -20)
    glColor3f(0.5, 0.5, 0.5)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 40, 10, 10)
    glPopMatrix()
def draw_enemy(x, y, z, size):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.2, 0.2)
    gluSphere(gluNewQuadric(), size, 20, 20)
    glTranslatef(0, 0, size * 1.5)
    glColor3f(0.8, 0.1, 0.1)
    gluSphere(gluNewQuadric(), size * 0.6, 20, 20)
    glPopMatrix()
def draw_enemies():
    global enemy_size_phase
    base_size = 30
    size_variation = 5 * math.sin(enemy_size_phase)
    enemy_size = base_size + size_variation
    for enemy in enemies:
        draw_enemy(enemy[0], enemy[1], enemy[2], enemy_size)
def draw_bullet(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.0, 0.0)
    glutSolidCube(10)
    glPopMatrix()
def draw_bullets():
    for bullet in bullets:
        draw_bullet(bullet[0], bullet[1], bullet[2])
def draw_checkered_floor():
    tile_size = 75
    num_tiles = int(GRID_LENGTH * 2 / tile_size)
    glBegin(GL_QUADS)
    for i in range(num_tiles):
        for j in range(num_tiles):
            x = -GRID_LENGTH + i * tile_size
            y = -GRID_LENGTH + j * tile_size
            if (i + j) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.7, 0.5, 0.95)
            glVertex3f(x, y, 0)
            glVertex3f(x + tile_size, y, 0)
            glVertex3f(x + tile_size, y + tile_size, 0)
            glVertex3f(x, y + tile_size, 0)
    glEnd()
def draw_boundaries():
    wall_height = 150
    wall_thickness = 30
    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 1.0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glEnd()
def keyboardListener(key, x, y):
    global player_pos, gun_angle, cheat_mode, cheat_vision, game_over, life, score, bullets_missed, player_alive, camera_first_person
    if game_over and key == b'r':
        player_pos = [0, 0, 30]
        gun_angle = 0
        life = 5
        score = 0
        bullets_missed = 0
        game_over = False
        player_alive = True
        bullets.clear()
        initialize_enemies()
        print("Game Reset!")
        return
    if game_over:
        return
    if key == b'w':
        rad = math.radians(gun_angle)
        move_speed = 50 if cheat_mode else 10
        player_pos[0] += move_speed * (-math.sin(rad))
        player_pos[1] += move_speed * (-math.cos(rad))
        player_pos[0] = max(-GRID_LENGTH + 50, min(GRID_LENGTH - 50, player_pos[0]))
        player_pos[1] = max(-GRID_LENGTH + 50, min(GRID_LENGTH - 50, player_pos[1]))
    if key == b's':
        rad = math.radians(gun_angle)
        move_speed = 50 if cheat_mode else 10
        player_pos[0] -= move_speed * (-math.sin(rad))
        player_pos[1] -= move_speed * (-math.cos(rad))
        player_pos[0] = max(-GRID_LENGTH + 50, min(GRID_LENGTH - 50, player_pos[0]))
        player_pos[1] = max(-GRID_LENGTH + 50, min(GRID_LENGTH - 50, player_pos[1]))
    if key == b'a':
        if not cheat_mode:
            gun_angle -= 5
    if key == b'd':
        if not cheat_mode:
            gun_angle += 5
    if key == b'c':
        cheat_mode = not cheat_mode
        print(f"Cheat Mode: {'ON' if cheat_mode else 'OFF'}")
    if key == b'v':
        if cheat_mode:
            camera_first_person = not camera_first_person
            print(f"Cheat Vision (First Person): {'ON' if camera_first_person else 'OFF'}")
def specialKeyListener(key, x, y):
    global camera_pos, camera_angle
    if key == GLUT_KEY_UP:
        camera_pos[2] += 20
    if key == GLUT_KEY_DOWN:
        camera_pos[2] = max(100, camera_pos[2] - 20)
    if key == GLUT_KEY_LEFT:
        camera_angle += 5
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 5
def mouseListener(button, state, x, y):
    global camera_first_person, bullets, game_over, cheat_mode
    if game_over:
        return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        fire_bullet()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if not cheat_mode:
            camera_first_person = not camera_first_person
            print(f"Camera Mode: {'First Person' if camera_first_person else 'Third Person'}")
def fire_bullet():
    global bullets, player_pos, gun_angle
    angle_rad = math.radians(gun_angle)
    dir_x = -math.sin(angle_rad)
    dir_y = -math.cos(angle_rad)
    spawn_x = player_pos[0] + 50 * dir_x
    spawn_y = player_pos[1] + 50 * dir_y
    spawn_z = player_pos[2] + 10
    bullets.append([spawn_x, spawn_y, spawn_z, dir_x, dir_y])
def setupCamera():
    global camera_pos, camera_angle, camera_first_person, cheat_vision, cheat_mode
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if camera_first_person:
        rad = math.radians(gun_angle)
        gun_dir_x = -math.sin(rad)
        gun_dir_y = -math.cos(rad)
        cam_x = player_pos[0]
        cam_y = player_pos[1]
        cam_z = player_pos[2] + 50
        look_x = player_pos[0] + 100 * gun_dir_x
        look_y = player_pos[1] + 100 * gun_dir_y
        look_z = player_pos[2]
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 0, 1)
    else:
        rad = math.radians(camera_angle)
        distance = 800
        cam_x = distance * math.sin(rad)
        cam_y = distance * math.cos(rad)
        cam_z = camera_pos[2]
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)
def update_bullets():
    global bullets, enemies, score, bullets_missed, cheat_mode
    bullets_to_remove = []
    for i, bullet in enumerate(bullets):
        bullet[0] += 15 * bullet[3]
        bullet[1] += 15 * bullet[4]
        if (abs(bullet[0]) > GRID_LENGTH or abs(bullet[1]) > GRID_LENGTH):
            bullets_to_remove.append(i)
            if not cheat_mode:
                bullets_missed += 1
            continue
        for j, enemy in enumerate(enemies):
            dist = math.sqrt((bullet[0] - enemy[0])**2 + (bullet[1] - enemy[1])**2)
            if dist < 50:
                bullets_to_remove.append(i)
                score += 1
                while True:
                    new_x = random.uniform(-GRID_LENGTH + 150, GRID_LENGTH - 150)
                    new_y = random.uniform(-GRID_LENGTH + 150, GRID_LENGTH - 150)
                    if math.sqrt((new_x - player_pos[0])**2 + (new_y - player_pos[1])**2) > 300:
                        enemy[0] = new_x
                        enemy[1] = new_y
                        break
                break
    for i in sorted(bullets_to_remove, reverse=True):
        if i < len(bullets):
            bullets.pop(i)
def update_enemies():
    global enemies, player_pos, life, game_over, player_alive, enemy_hit_cooldown, cheat_mode
    for i, enemy in enumerate(enemies):
        if enemy_hit_cooldown[i] > 0:
            enemy_hit_cooldown[i] -= 1
        dx = player_pos[0] - enemy[0]
        dy = player_pos[1] - enemy[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 50:
            enemy[0] += (dx / dist) * 0.1
            enemy[1] += (dy / dist) * 0.1
        if dist < 55 and enemy_hit_cooldown[i] == 0 and not cheat_mode:
            life -= 1
            enemy_hit_cooldown[i] = 120
            print(f"Hit! Life remaining: {life}")
            while True:
                new_x = random.uniform(-GRID_LENGTH + 150, GRID_LENGTH - 150)
                new_y = random.uniform(-GRID_LENGTH + 150, GRID_LENGTH - 150)
                if math.sqrt((new_x - player_pos[0])**2 + (new_y - player_pos[1])**2) > 300:
                    enemy[0] = new_x
                    enemy[1] = new_y
                    break
            if life <= 0:
                game_over = True
                player_alive = False
                print("Game Over!")
def update_cheat_mode():
    global gun_angle, cheat_mode, enemies, player_pos, cheat_fire_cooldown
    if cheat_mode:
        gun_angle += 0.5
        if cheat_fire_cooldown > 0:
            cheat_fire_cooldown -= 1
            return
        rad = math.radians(gun_angle)
        gun_dir_x = -math.sin(rad)
        gun_dir_y = -math.cos(rad)
        for enemy in enemies:
            to_enemy_x = enemy[0] - player_pos[0]
            to_enemy_y = enemy[1] - player_pos[1]
            distance = math.sqrt(to_enemy_x**2 + to_enemy_y**2)
            if distance > 50:
                to_enemy_x /= distance
                to_enemy_y /= distance
                dot_product = gun_dir_x * to_enemy_x + gun_dir_y * to_enemy_y
                if dot_product > 0.995:
                    fire_bullet()
                    cheat_fire_cooldown = 10
                    break
def idle():
    global enemy_size_phase, game_over, bullets_missed, cheat_mode, player_alive
    if not game_over:
        update_bullets()
        update_enemies()
        update_cheat_mode()
        enemy_size_phase += 0.1
        if bullets_missed >= 10 and not cheat_mode:
            game_over = True
            player_alive = False
            print("Game Over! Too many missed bullets!")
    glutPostRedisplay()
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    glEnable(GL_DEPTH_TEST)
    draw_checkered_floor()
    draw_boundaries()
    draw_player()
    draw_enemies()
    draw_bullets()
    if camera_first_person:
        draw_first_person_gun()
    draw_text(10, 770, f"Player Life Remaining: {life}")
    draw_text(10, 740, f"Game Score: {score}")
    draw_text(10, 710, f"Player Bullet Missed: {bullets_missed}")
    draw_text(10, 680, f"Cheat Mode: {'ON' if cheat_mode else 'OFF'} | Camera: {'First Person' if camera_first_person else 'Third Person'}")
    if game_over:
        draw_text(300, 400, "GAME OVER! Press R to Restart", GLUT_BITMAP_HELVETICA_18, (0, 0, 0))
    glutSwapBuffers()
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Bullet Frenzy - 3D Game")
    initialize_enemies()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()
if __name__ == "__main__":
    main()
