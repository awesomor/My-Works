import pygame
from random import *
from pygame import Vector2, Vector3
from math import *

class PhysicalRect:
    def __init__(self, x, y, theta, vx, vy, vw, inverseweight, width, height):
        self.position = Vector2(x,y)
        self.theta = theta
        self.velocity = Vector2(vx, vy)
        self.angularvelocity = vw
        self.width = width
        self.height = height
        self.inverseweight = inverseweight

    def update(self):
        self.p1 = self.position + self.d1
        self.p2 = self.position + self.d2
        self.p3 = self.position + self.d3
        self.p4 = self.position + self.d4

    def move(self):
        self.position += self.velocity * dt * scale

    def rotate(self):
        self.theta += self.angularvelocity * dt * angularscale
        self.d1 = Vector2(self.width/2, self.height/2).rotate_rad(self.theta)
        self.d2 = Vector2(-self.width/2, self.height/2).rotate_rad(self.theta)
        self.d3 = Vector2(-self.width/2, -self.height/2).rotate_rad(self.theta)
        self.d4 = Vector2(self.width/2, -self.height/2).rotate_rad(self.theta)
        self.t1 = Vector2(1,0).rotate_rad(self.theta)
        self.t2 = Vector2(0,1).rotate_rad(self.theta)
        self.t3 = Vector2(-1,0).rotate_rad(self.theta)
        self.t4 = Vector2(0,-1).rotate_rad(self.theta)

    def friction(self):
        if self.velocity.x > 0:
            if self.velocity.x > LinearFriction:
                self.velocity.x -= LinearFriction
            else : self.velocity.x = 0
        elif self.velocity.x < 0:
            if self.velocity.x < -LinearFriction:
                self.velocity.x -= -LinearFriction
            else : self.velocity.x = 0

        if self.angularvelocity > 0:
            if self.angularvelocity > AngularFriction:
               self.angularvelocity -= AngularFriction
            # else : self.angularvelocity = 0
        elif self.angularvelocity < 0:
            if self.angularvelocity < -AngularFriction:
                self.angularvelocity -= -AngularFriction
            # else : self.angularvelocity = 0

    def SpeedLimitate(self):
        if self.velocity.x > LinearMaxSpeed:
            self.velocity.x = LinearMaxSpeed
        if self.velocity.x < -LinearMaxSpeed:
            self.velocity.x = -LinearMaxSpeed
        if self.velocity.y > LinearMaxSpeed:
            self.velocity.y = LinearMaxSpeed
        if self.velocity.y < -LinearMaxSpeed:
            self.velocity.y = -LinearMaxSpeed

        if self.angularvelocity > AngularMaxSpeed:
            self.angularvelocity = AngularMaxSpeed
        if self.angularvelocity < -AngularMaxSpeed:
            self.angularvelocity = -AngularMaxSpeed



    def draw(self, screen):
        pygame.draw.lines(screen, color=RectColor, closed=True, points=(self.p1,self.p2,self.p3,self.p4), width=RectWidth)

def CollideDetect(obj1, obj2):
    distance = (obj1.position - obj2.position).length()
    dia1, dia2 = (obj1.width**2 + obj1.height**2)**.5, (obj2.width**2 + obj2.height**2)**.5
    if dia1 + dia2 < distance*2:
        pass
    else:
        for o1d, o1t in [(obj1.d1, obj1.t1), (obj1.d2, obj1.t2), (obj1.d3, obj1.t3), (obj1.d4, obj1.t4)]:
            collide = True
            inner = -10000, Vector2(1,0), Vector2(1,0)
            for o2d, o2t in [(obj2.d1, obj2.t1), (obj2.d2, obj2.t2), (obj2.d3, obj2.t3), (obj2.d4, obj2.t4)]:
                v1 = (obj1.position + o1d) - (obj2.position + o2d)
                v2 = o2t
                if inner[0] < v1.dot(v2): inner = v1.dot(v2), o2t, v1
                if v1.dot(v2) > 0: collide = False
            if collide:
                obj1.cd = inner[1]
                obj1.distance = -inner[1].dot(inner[2])
                obj1.r1 = o1d + inner[1] * -inner[1].dot(inner[2])
                obj2.r2 = (obj1.position + obj1.r1) - obj2.position
                return True

def CollideResolve(obj1, obj2):
    if obj1.inverseweight == 0 and obj2.inverseweight == 0: return
    CollisionDirection = obj1.cd
    RelativeVelocity = obj1.velocity - obj2.velocity
    if obj1.inverseweight == 0: inversei1 = 0
    else: inversei1 = 1 / (1 / obj1.inverseweight * ((obj1.width/scale)**2+(obj1.height/scale)**2)/12)
    if obj2.inverseweight == 0: inversei2 = 0
    else: inversei2 = 1 / (1 / obj2.inverseweight * ((obj2.width/scale)**2+(obj2.height/scale)**2)/12)
    r1nr1 = (Vector3(obj1.r1.x, obj1.r1.y, 0).cross(Vector3(CollisionDirection.x, CollisionDirection.y, 0))).cross(Vector3(obj1.r1.x, obj1.r1.y, 0))
    r1nr1 = Vector2(r1nr1.x, r1nr1.y)
    r2nr2 = (Vector3(obj2.r2.x, obj2.r2.y, 0).cross(Vector3(CollisionDirection.x, CollisionDirection.y, 0))).cross(Vector3(obj2.r2.x, obj2.r2.y, 0))
    r2nr2 = Vector2(r2nr2.x, r2nr2.y)
    Jacobian = -(1 + e) * RelativeVelocity.dot(CollisionDirection)
    Jacobian /= obj1.inverseweight + obj2.inverseweight + (inversei1 * r1nr1 + inversei2 * r2nr2).dot(CollisionDirection)
    obj1.angularvelocity += inversei1 * obj1.r1.cross(Jacobian * CollisionDirection)
    obj2.angularvelocity += -inversei2 * obj2.r2.cross(Jacobian * CollisionDirection)
    obj1.velocity += obj1.inverseweight * Jacobian * CollisionDirection
    obj2.velocity += - obj2.inverseweight * Jacobian * CollisionDirection
    obj1.position += CollisionDirection * (obj1.distance + 1) * (obj1.distance > 0) * (obj1.inverseweight != 0)









pygame.init()
screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
screen = pygame.display.set_mode((screen_width, screen_height), flags=pygame.FULLSCREEN)

dt = 1/60
clock = pygame.time.Clock()

g = 9.8
scale = 1/10
angularscale = 1
e = .7
LinearFriction = 1
AngularFriction = pi/2000
LinearMaxSpeed = 5000
AngularMaxSpeed = 2 * pi

RectColor = "Black"
RectWidth = 5
rects = []
rect_number = 10
for i in range(rect_number):
    x = randint(100, screen_width-300)
    y = randint(100, screen_height-300)
    theta = randint(0, 360)/180*pi
    vx = randint(-30, 30) * 10
    vy = randint(-30, 30)
    vw = randint(-30, 30) / 20
    width = randint(50, 200)
    height = randint(50, 200)
    inverseweight = 1 / (width * height / 100)
    rect = PhysicalRect(x=x, y=y, theta=theta, vx=vx, vy=vy, vw=vw, width=width, height=height, inverseweight=inverseweight)
    rects.append(rect)
rects.append(PhysicalRect(x= screen_width / 2,     y=screen_height * 5/4, theta=0, vx=0, vy=0, vw=0, width=screen_width,       height=screen_height * 1/2, inverseweight=0))
rects.append(PhysicalRect(x= -screen_width / 8,    y=screen_height * 1/2, theta=0, vx=0, vy=0, vw=0, width=screen_width * 1/4, height=screen_height,       inverseweight=0))
rects.append(PhysicalRect(x= screen_width * 9/8, y=screen_height * 1/2, theta=0, vx=0, vy=0, vw=0, width=screen_width * 1/4, height=screen_height,       inverseweight=0))

running = True
while running :
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    for rect in rects:
        rect.velocity.y += g * (rect.inverseweight != 0)
        rect.friction()
        rect.SpeedLimitate()

        rect.rotate()
        rect.move()
        rect.update()

        # rm, rM, rh = min(rect.p1.x, rect.p2.x, rect.p3.x, rect.p4.x), max(rect.p1.x, rect.p2.x, rect.p3.x, rect.p4.x), max(rect.p1.y, rect.p2.y, rect.p3.y, rect.p4.y)
        # if screen_height < rh:
        #     rect.velocity.y *= -1
        # if screen_width < rM:
        #     rect.velocity.x *= -1
        # if rm < 0:
        #     rect.velocity.x *= -1

    for i in range(len(rects)):
        for j in range(len(rects)):
            obj1, obj2 = rects[i], rects[j]
            if obj1 == obj2: continue
            if CollideDetect(obj1, obj2):
                CollideResolve(obj1, obj2)

    screen.fill("white")

    for rect in rects:
        rect.draw(screen)

    pygame.display.flip()

pygame.quit()



