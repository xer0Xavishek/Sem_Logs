"""
Reusable 3D primitives using ONLY allowed OpenGL functions
"""
import math
from OpenGL.GL import *

def draw_cube(size=1.0):
    """Draw a cube using glBegin/glEnd - ALLOWED"""
    s = size / 2
    glBegin(GL_QUADS)
    # Front
    glNormal3f(0, 0, 1)
    glVertex3f(-s, -s, s)
    glVertex3f(s, -s, s)
    glVertex3f(s, s, s)
    glVertex3f(-s, s, s)
    # Back
    glNormal3f(0, 0, -1)
    glVertex3f(-s, -s, -s)
    glVertex3f(-s, s, -s)
    glVertex3f(s, s, -s)
    glVertex3f(s, -s, -s)
    # Top
    glNormal3f(0, 1, 0)
    glVertex3f(-s, s, -s)
    glVertex3f(-s, s, s)
    glVertex3f(s, s, s)
    glVertex3f(s, s, -s)
    # Bottom
    glNormal3f(0, -1, 0)
    glVertex3f(-s, -s, -s)
    glVertex3f(s, -s, -s)
    glVertex3f(s, -s, s)
    glVertex3f(-s, -s, s)
    # Right
    glNormal3f(1, 0, 0)
    glVertex3f(s, -s, -s)
    glVertex3f(s, s, -s)
    glVertex3f(s, s, s)
    glVertex3f(s, -s, s)
    # Left
    glNormal3f(-1, 0, 0)
    glVertex3f(-s, -s, -s)
    glVertex3f(-s, -s, s)
    glVertex3f(-s, s, s)
    glVertex3f(-s, s, -s)
    glEnd()

def draw_pyramid(size=1.0):
    """Draw a pyramid using glBegin/glEnd - ALLOWED"""
    glBegin(GL_TRIANGLES)
    for i in range(4):
        angle1 = i * 90
        angle2 = (i + 1) * 90
        x1 = math.cos(math.radians(angle1)) * size
        y1 = math.sin(math.radians(angle1)) * size
        x2 = math.cos(math.radians(angle2)) * size
        y2 = math.sin(math.radians(angle2)) * size
        
        glNormal3f(0, 0, 1)
        glVertex3f(0, 0, size * 1.5)
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
    glEnd()

def draw_ground(size=500):
    """Draw ground plane - ALLOWED"""
    glBegin(GL_QUADS)
    glNormal3f(0, 0, 1)
    glVertex3f(-size, -size, 0)
    glVertex3f(size, -size, 0)
    glVertex3f(size, size, 0)
    glVertex3f(-size, size, 0)
    glEnd()

def draw_character(scale=1.0):
    """Draw simple character using cubes - ALLOWED"""
    # Body
    glPushMatrix()
    glScalef(0.4 * scale, 0.3 * scale, 0.8 * scale)
    draw_cube(1.0)
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glTranslatef(0, 0, 0.6 * scale)
    glScalef(0.3 * scale, 0.3 * scale, 0.3 * scale)
    draw_cube(1.0)
    glPopMatrix()
    
    # Arms
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(side * 0.25 * scale, 0, 0.2 * scale)
        glScalef(0.1 * scale, 0.1 * scale, 0.5 * scale)
        draw_cube(1.0)
        glPopMatrix()
    
    # Legs
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(side * 0.1 * scale, 0, -0.5 * scale)
        glScalef(0.12 * scale, 0.12 * scale, 0.6 * scale)
        draw_cube(1.0)
        glPopMatrix()

def draw_crystal(size=1.0):
    """Draw crystal using triangles - ALLOWED"""
    glBegin(GL_TRIANGLES)
    # Top pyramid
    for i in range(4):
        angle1 = i * 90
        angle2 = (i + 1) * 90
        x1 = math.cos(math.radians(angle1)) * size
        y1 = math.sin(math.radians(angle1)) * size
        x2 = math.cos(math.radians(angle2)) * size
        y2 = math.sin(math.radians(angle2)) * size
        
        glVertex3f(0, 0, size * 1.5)
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
    
    # Bottom pyramid
    for i in range(4):
        angle1 = i * 90
        angle2 = (i + 1) * 90
        x1 = math.cos(math.radians(angle1)) * size
        y1 = math.sin(math.radians(angle1)) * size
        x2 = math.cos(math.radians(angle2)) * size
        y2 = math.sin(math.radians(angle2)) * size
        
        glVertex3f(0, 0, -size * 1.5)
        glVertex3f(x2, y2, 0)
        glVertex3f(x1, y1, 0)
    glEnd()
