
# Task 1 — Rainy house scene
from OpenGL.GL import*
from OpenGL.GLUT import*
from OpenGL.GLU import*
import random
IDLE=-1
BRIGHTENING=1
DARKENING=0
class House_with_rain:
    def __init__(self,w=500,h=500):
        self.width=w 
        self.height=h 
        self.rain_drops=[]
        self.wind_angle=0.0        
        self.brightness=0.0        
        self.transition_mode=IDLE       
        self.fade_speed=0.004 
    def draw_triangle(self,x_p,y_p,w_p,h_p): 
        glBegin(GL_TRIANGLES)
        glVertex2d(x_p,y_p)
        glVertex2d(x_p+w_p,y_p)
        glVertex2d(x_p+(w_p/2),y_p+h_p)
        glEnd()
    def draw_background(self):
        r=self.brightness*0.40
        g=self.brightness*0.60
        b=self.brightness*0.90
        glColor3f(r,g,b)
        glBegin(GL_TRIANGLES)
        glVertex2d(0,0)
        glVertex2d(self.width,0)
        glVertex2d(self.width,self.height)
        glVertex2d(0,0)
        glVertex2d(0,self.height)
        glVertex2d(self.width,self.height)
        glEnd()
    def draw_ground(self):
        r=0.10+self.brightness*0.20
        g=0.25+self.brightness*0.35
        b=0.05+self.brightness*0.05
        glColor3f(r,g,b)
        ground_top=208
        ground_bottom=0
        left_edge=0
        right_edge=self.width
        glBegin(GL_TRIANGLES)
        glVertex2d(left_edge,ground_bottom)
        glVertex2d(right_edge,ground_bottom)
        glVertex2d(right_edge,ground_top)
        glVertex2d(left_edge,ground_bottom)
        glVertex2d(left_edge,ground_top)
        glVertex2d(right_edge,ground_top)
        glEnd()
    def draw_house(self):
        wall_left=130
        wall_right=370
        wall_bottom=100
        wall_top=300
        r=0.30+self.brightness*0.50
        g=0.22+self.brightness*0.48
        b=0.10+self.brightness*0.30
        glColor3f(r,g,b)
        glBegin(GL_TRIANGLES)
        glVertex2d(wall_left,wall_bottom)
        glVertex2d(wall_left,wall_top)
        glVertex2d(wall_right,wall_top)
        glVertex2d(wall_left,wall_bottom)
        glVertex2d(wall_right,wall_bottom)
        glVertex2d(wall_right,wall_top)
        glEnd()
        r=0.25+self.brightness*0.30
        g=0.10+self.brightness*0.17
        b=0.04+self.brightness*0.03
        glColor3f(r,g,b)
        self.draw_triangle(wall_left,wall_top,wall_right-wall_left,120)
        chimney_left=wall_right-90
        chimney_right=chimney_left+40
        chimney_bottom=wall_top+50
        chimney_top=chimney_bottom+80
        r=0.22+self.brightness*0.28
        g=0.08+self.brightness*0.12
        b=0.04
        glColor3f(r,g,b)
        glBegin(GL_TRIANGLES)
        glVertex2d(chimney_left,chimney_bottom)
        glVertex2d(chimney_right,chimney_bottom)
        glVertex2d(chimney_right,chimney_top)
        glVertex2d(chimney_left,chimney_bottom)
        glVertex2d(chimney_left,chimney_top)
        glVertex2d(chimney_right,chimney_top)
        glEnd()
        door_width=60
        door_height=100
        door_left=wall_left+(wall_right-wall_left-door_width)/2
        door_right=door_left+door_width
        door_bottom=wall_bottom
        door_top=door_bottom+door_height
        r=0.25+self.brightness*0.25
        g=0.12+self.brightness*0.13
        b=0.0
        glColor3f(r,g,b)
        glBegin(GL_TRIANGLES)
        glVertex2d(door_left,door_bottom)
        glVertex2d(door_left,door_top)
        glVertex2d(door_right,door_top)
        glVertex2d(door_left,door_bottom)
        glVertex2d(door_right,door_bottom)
        glVertex2d(door_right,door_top)
        glEnd()
        lw_left=wall_left+20 
        lw_right=lw_left+55
        lw_bottom=wall_top-95
        lw_top=lw_bottom+55
        r=0.60-self.brightness*0.20
        g=0.55-self.brightness*0.10
        b=0.10+self.brightness*0.80
        glColor3f(r,g,b)
        glBegin(GL_TRIANGLES)
        glVertex2d(lw_left,lw_bottom)
        glVertex2d(lw_right,lw_bottom)
        glVertex2d(lw_right,lw_top)
        glVertex2d(lw_left,lw_bottom)
        glVertex2d(lw_left,lw_top)
        glVertex2d(lw_right,lw_top)
        glEnd()
        glColor3f(0.0,0.0,0.0)
        glLineWidth(2.0)
        glBegin(GL_LINES) 
        glVertex2d(lw_left,lw_bottom);               glVertex2d(lw_right,lw_bottom)
        glVertex2d(lw_right,lw_bottom);               glVertex2d(lw_right,lw_top)
        glVertex2d(lw_right,lw_top);                  glVertex2d(lw_left,lw_top)
        glVertex2d(lw_left,lw_top);                  glVertex2d(lw_left,lw_bottom)
        glVertex2d((lw_left+lw_right)/2,lw_bottom);   glVertex2d((lw_left+lw_right)/2,lw_top)
        glVertex2d(lw_left,(lw_bottom+lw_top)/2);     glVertex2d(lw_right,(lw_bottom+lw_top)/2)
        glEnd()
        rw_right=wall_right-20
        rw_left=rw_right-55
        rw_bottom=wall_top-95
        rw_top=rw_bottom+55
        r=0.60-self.brightness*0.20
        g=0.55-self.brightness*0.10
        b=0.10+self.brightness*0.80
        glColor3f(r,g,b)
        glBegin(GL_TRIANGLES)
        glVertex2d(rw_left,rw_bottom)
        glVertex2d(rw_right,rw_bottom)
        glVertex2d(rw_right,rw_top)
        glVertex2d(rw_left,rw_bottom)
        glVertex2d(rw_left,rw_top)
        glVertex2d(rw_right,rw_top)
        glEnd()
        glColor3f(0.0,0.0,0.0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2d(rw_left,rw_bottom);               glVertex2d(rw_right,rw_bottom)
        glVertex2d(rw_right,rw_bottom);               glVertex2d(rw_right,rw_top)
        glVertex2d(rw_right,rw_top);                  glVertex2d(rw_left,rw_top)
        glVertex2d(rw_left,rw_top);                  glVertex2d(rw_left,rw_bottom)
        glVertex2d((rw_left+rw_right)/2,rw_bottom);   glVertex2d((rw_left+rw_right)/2,rw_top)
        glVertex2d(rw_left,(rw_bottom+rw_top)/2);     glVertex2d(rw_right,(rw_bottom+rw_top)/2)
        glEnd()
        glColor3f(0.9,0.75,0.1)
        glPointSize(6)
        glBegin(GL_POINTS)
        glVertex2d(door_left+48,(door_bottom+door_top)/2)
        glEnd()
    def setup_projection(self):
        glViewport(0,0,self.width,self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0,self.width,0.0,self.height,0.0,1.0)
        glMatrixMode(GL_MODELVIEW)
    def update_rain(self):
        for i in range(2):
            x=random.uniform(0,self.width)
            self.rain_drops.append([x,self.height])
        for drop in self.rain_drops:
            drop[0] +=self.wind_angle*0.3   
            drop[1]-=6                       
            if drop[0]< 0:
                drop[0] +=self.width
            elif drop[0]> self.width:
                drop[0]-=self.width
        self.rain_drops=[drop for drop in self.rain_drops if drop[1]> 0]
    def draw_rain(self):
        r=1
        g=1
        b=1
        glColor3f(r,g,b)
        glLineWidth(1.5)
        glBegin(GL_LINES)
        for x,y in self.rain_drops:
            glVertex2f(x,y)
            glVertex2f(x-self.wind_angle*2,y-12) #
        glEnd()
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.draw_background()   
        self.draw_ground()
        self.draw_house()
        self.draw_rain()
        glutSwapBuffers()
    def animate(self,value=0):
        if self.transition_mode==BRIGHTENING:
            self.brightness +=self.fade_speed
        elif self.transition_mode==DARKENING:
            self.brightness-=self.fade_speed
        self.brightness=max(0.0,min(1.0,self.brightness))
        self.update_rain()
        self.display()
    def special_key_listener(self,key,x,y):
        if key==GLUT_KEY_RIGHT:
            self.wind_angle-=0.3  
        elif key==GLUT_KEY_LEFT:
            self.wind_angle +=0.3  
    def keyboard_listener(self,key,x,y):
        if key in (b'd',b'D'):
            self.transition_mode=BRIGHTENING
        elif key in (b'n',b'N'):
            self.transition_mode=DARKENING
    def main(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
        glutInitWindowSize(self.width,self.height)
        glutInitWindowPosition(200,200)
        glutCreateWindow(b"House with raining")
        self.setup_projection()
        glutDisplayFunc(self.display)
        glutSpecialFunc(self.special_key_listener)
        glutKeyboardFunc(self.keyboard_listener)
        glutIdleFunc(self.animate)
        glutMainLoop()
if __name__=="__main__":
    scene=House_with_rain()
    scene.main()


# Task 2: Amazing Box
from OpenGL.GL import*
from OpenGL.GLUT import*
import random
class MovingPoint:
    def __init__(self,x,y,box_width_half,box_height_half):
        self.x=x
        self.y=y
        self.dir_x=random.choice([-1,1])
        self.dir_y=random.choice([-1,1])
        self.color=(random.random(),random.random(),random.random())
        self.width_half=box_width_half
        self.height_half=box_height_half
    def move(self,speed):
        self.x +=self.dir_x*speed
        self.y +=self.dir_y*speed
        if self.x>=self.width_half or self.x<=-self.width_half:
            self.dir_x*=-1
        if self.y>=self.height_half or self.y<=-self.height_half:
            self.dir_y*=-1
class AmazingBox:
    def __init__(self):
        self.width=1280
        self.height=720
        self.width_half=self.width/2
        self.height_half=self.height/2
        self.points=[]       
        self.speed=1      
        self.blink_enabled=False
        self.points_visible=True
        self.frame_count=0
        self.blink_interval=55    
        self.is_frozen=False
        glutInit()
        glutInitDisplayMode(GLUT_RGBA)
        glutInitWindowSize(self.width,self.height)
        glutCreateWindow(b"Amazing Box")
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-self.width_half,self.width_half,-self.height_half,self.height_half,-1,1)
        glMatrixMode(GL_MODELVIEW)
        glutDisplayFunc(self.display)
        glutIdleFunc(self.animate)
        glutKeyboardFunc(self.keyboard_listener)
        glutSpecialFunc(self.special_key_listener)
        glutMouseFunc(self.mouse_listener)
    def convert_coordinate(self,mouse_x,mouse_y):
        gl_x=mouse_x-self.width_half
        gl_y=self.height_half-mouse_y
        return gl_x,gl_y
    def draw_points(self):
        glPointSize(9)
        for point in self.points:
            if self.blink_enabled and not self.points_visible:
                continue
            glColor3f(*point.color)
            glBegin(GL_POINTS)
            glVertex2f(point.x,point.y)
            glEnd()
    def draw_border(self):
        glColor3f(0.7,0.7,0.7)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(-self.width_half,-self.height_half)
        glVertex2f( self.width_half,-self.height_half)
        glVertex2f( self.width_half,-self.height_half)
        glVertex2f( self.width_half,self.height_half)
        glVertex2f( self.width_half,self.height_half)
        glVertex2f(-self.width_half,self.height_half)
        glVertex2f(-self.width_half,self.height_half)
        glVertex2f(-self.width_half,-self.height_half)
        glEnd()
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.draw_border()
        self.draw_points()
        glutSwapBuffers()
    def animate(self):
        if not self.is_frozen:
            for point in self.points:
                point.move(self.speed)
            if self.blink_enabled:
                self.frame_count +=1
                if self.frame_count % self.blink_interval==0:
                    self.points_visible=not self.points_visible
        glutPostRedisplay()

    def mouse_listener(self,button,state,x,y):
        if state!=GLUT_DOWN:
            return
        if button==GLUT_RIGHT_BUTTON:
            world_x,world_y=self.convert_coordinate(x,y)
            self.points.append(MovingPoint(world_x,world_y,self.width_half,self.height_half))
        elif button==GLUT_LEFT_BUTTON:
            self.blink_enabled=not self.blink_enabled
            if not self.blink_enabled:
                self.points_visible=True
                self.frame_count=0
    def special_key_listener(self,key,x,y):
        if key==GLUT_KEY_UP:
            self.speed*=1.1
        elif key==GLUT_KEY_DOWN:
            self.speed/=1.1
            if self.speed< 0.2:
                self.speed=0.2
    def keyboard_listener(self,key,x,y):
        if key==b' ':
            self.is_frozen=not self.is_frozen
    def main(self):
        glutMainLoop()


if __name__=="__main__":
    AmazingBox().main()