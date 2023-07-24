import pygame
import pymunk
from random import *
from math import *
import numpy
from pymunk import Vec2d
from pymunk.pygame_util import *
from pygame.locals import *


pygame.init()

screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
screen_height -= 0
screen = pygame.display.set_mode((screen_width, screen_height), flags=pygame.FULLSCREEN)

clock = pygame.time.Clock()
space = pymunk.Space()
space.gravity = 0, 4000


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.position = Vec2d(width/2 - screen_width/2, height/2 - screen_height/2)

    def move(self, c, ratio):
        self.position += ((c.body.position - Vec2d(screen_width/2 - c.width/2, screen_height/2 - c.height/2)) - self.position) * ratio

        if self.position.x < 0:
            self.position = Vec2d(0, self.position.y)
        if self.width - screen_width < self.position.x:
            self.position = Vec2d(self.width - screen_width, self.position.y)
        if self.position.y < 0:
            self.position = Vec2d(self.position.x, 0)
        if self.height - screen_height < self.position.y:
            self.position = Vec2d(self.position.x, self.height - screen_height)

    def relative_location(self, c):
        c.body.rposition = c.body.position - self.position


map = Map(screen_width * 5, screen_height * 3)

statics = []
class Static:
    def __init__(self, size, position, friction=0.9, color="black"):
        w,h = size[0], size[1]
        self.size = size
        self.body = space.static_body
        self.body.position = position
        self.position = position
        self.shape = pymunk.Poly(self.body, vertices=[(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)], radius=1)
        self.shape.elasticity = 0.01
        self.shape.density = 0.01
        self.shape.friction = friction
        self.color = color

        space.add(self.shape)
        statics.append(self)

    def draw(self, map, screen):
        self.rposition = self.position - map.position
        rect = pygame.Rect((0, 0), self.size)
        rect.center = self.rposition

        pygame.draw.rect(screen, color=self.color, rect=rect, width=5)

    def collide(self, jessi):
        jessi_rect = pygame.Rect(0, 0, jessi.width + 4, jessi.height + 6)
        jessi_rect.center = jessi.body.rposition

        rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        rect.center = self.position - map.position

        if rect.colliderect(jessi_rect): return True
        else: return False

wall_width = 1000
Static(size=(map.width, wall_width), position=(map.width/2, map.height + wall_width/2), friction=0.5)
Static(size=(wall_width, map.height), position=(-wall_width/2, map.height/2), friction=0.1)
Static(size=(wall_width, map.height), position=(map.width + wall_width/2, map.height/2), friction=0.1)
for i in range(0):
    w, h = 200, 50
    x, y = randint(int(w/2), int(map.width-w/2)), randint(int(h/2), int(map.height-h/2))
    static = Static((w, h), (x, y), friction=0.5)

boxes = []
class Box:
    def __init__(self, size, position, friction=0.9, color="grey"):
        self.size = size
        self.width, self.height = size
        self.color = color
        self.body = pymunk.Body(mass=size[0] * size[1] / 100, moment=size[0] * size[1] / 10)
        self.body.position = position
        self.vertices = [Vec2d(-size[0]/2, -size[1]/2), Vec2d(size[0]/2, -size[1]/2), Vec2d(size[0]/2, size[1]/2), Vec2d(-size[0]/2, size[1]/2)]
        self.shape = pymunk.Poly(body=self.body, vertices=self.vertices, radius=1)
        self.shape.friction = friction
        self.shape.density = 0.01
        self.shape.elasticity = 0.01

        space.add(self.body, self.shape)
        boxes.append(self)

    def draw(self, map, screen):
        self.rposition = self.body.position - map.position
        self.vertices = [Vec2d(-self.size[0]/2, -self.size[1]/2), Vec2d(self.size[0]/2, -self.size[1]/2), Vec2d(self.size[0]/2, self.size[1]/2), Vec2d(-self.size[0]/2, self.size[1]/2)]
        self.rotated_vertices = [vertice.rotated(self.body.angle) + self.rposition for vertice in self.vertices]

        if box_width > 0: pygame.draw.polygon(screen, color=particle_inside_color, points=self.rotated_vertices, width=0)
        pygame.draw.polygon(screen, color=self.color, points=self.rotated_vertices, width=box_width)

characters = []
enemys = []
particles = []
class Character:
    def __init__(self, width, height, position=(map.width/2, 0)):
        self.body = pymunk.Body(mass=width*height/100, moment=width*height/10)
        self.body.position = position
        self.body.rposition = 0, 0
        self.shape = []
        self.shape.append(pymunk.Poly(self.body, ((-width/2, -height/2), (width/2, -height/2), (width/2, height/2), (-width/2, height/2)), radius=1))
        self.shape[0].elasticity = .01
        self.shape[0].friction = .7
        self.shape[0].density = .01
        self.width, self.height = width, height
        self.left, self.right = 0, 0
        self.land_time = 0
        self.sit_time = 0
        self.jump_time = 0
        self.dash_time = 0
        self.act = "stand"
        self.direction = -1
        self.color = "black"

        self.run_speed = 250
        self.walk_speed = 50
        self.sit_speed = 30
        self.move_scale = 100
        self.max_speed = 600
        self.jump_speed = 1200
        self.dash_speed = 500
        self.dash_act_amount = 400
        self.dash_jump_ratio = 0.5
        self.charge_jump_ratio = 0.2
        self.charge_dash_ratio = 0.2
        self.sit_charge_time = 30

        self.HP = 100
        self.STAMINA = 100
        self.MAX_HP = 100
        self.MAX_STAMINA = 100
        self.SpannerAttackStaminaConsumeAmount = 1
        self.self_hp_healing_amount = self.MAX_HP * 1/6000
        self.self_stamina_healing_amount = self.MAX_STAMINA * 1/2000

        space.add(self.body)
        for shape in self.shape: space.add(shape)
        characters.append(self)

    def speed_limit(self, speed_limit):
        if self.body.velocity.x > speed_limit:
            self.body.velocity = (speed_limit, self.body.velocity.y)
        elif self.body.velocity.x < -speed_limit:
            self.body.velocity = (-speed_limit, self.body.velocity.y)

    def dash(self):
        if abs(self.body.velocity.y) < up_down_minimun:
            if self == jessi:
                self.direction = - pygame.key.get_pressed()[pygame.K_LEFT] + pygame.key.get_pressed()[pygame.K_RIGHT] + (pygame.key.get_pressed()[pygame.K_LEFT]==False)*(pygame.key.get_pressed()[pygame.K_RIGHT]==False)*(-left+right)
                self.body.velocity += (self.dash_speed * self.direction * (1 + jessi.charge_dash_ratio * (jessi.sit_time >= jessi.sit_charge_time)), -self.jump_speed * self.dash_jump_ratio * (1 + jessi.charge_dash_ratio * (jessi.sit_time >= jessi.sit_charge_time)))
                self.dash_time = t
                self.sit_time = 0
            else: self.body.velocity += (self.dash_speed * (((self.direction.x > 0) - 1/2)*2), -self.jump_speed * self.dash_jump_ratio)

    def jump(self):
        if abs(self.body.velocity.y) < up_down_minimun:
            self.body.velocity += (0, -self.jump_speed * (1 + jessi.charge_jump_ratio * (jessi.sit_time >= jessi.sit_charge_time)))
            self.jump_time = t
            self.sit_time = 0

    def draw(self, screen):
        for shape in self.shape:
            vertices = shape.get_vertices()
            vertices = [Vec2d(v[0], v[1]).rotated(self.body.angle) + self.body.rposition for v in vertices]

            pygame.draw.polygon(screen, color=self.color, points=vertices, width=character_box_width)

    def rotate_limit(self):
        self.body.angular_velocity = 0
        self.body.angle = 0

    def JessiPartMake(self):
        facedic = ["leo", "lec", "reo", "rec", "leb", "reb", "nose", "mouth"]
        hairdic = []
        for i in range(9) :
            hairdic.append("hair" + "{}".format(i+1))
        self.partdic = {"downbody": (126, 223,30, 30), "downbodyc": (121, 218,40, 40), "upbody":(118,196,42,42), "upbodyc":(118,196,42,42),"leftbagnod":(118,196,42,42),"rightbagnod":(118,196,42,42), "bag":(110,190,82,82), \
                   "neck":(136,191,13,13), "head":(93,108,99,99), "hatdownb":(58,30,179,179),"hatdownf":(58,30,179,179),"hatup":(58,30,179,179),"hatglass":(58,30,179,179)}
        for p in facedic : self.partdic[p] = self.partdic["head"]
        for p in hairdic : self.partdic[p] = (38, 53, 209, 209)
        partdic_rest = {"lleftthigh": (132 ,232 ,32,32), "lleftthighc": (132 ,232 ,32,32), "lleftleg": (135 ,256 ,28,28), "lleftlegc": (130 ,251 ,38,38),\
                         "lleftfoot": (146 ,280 ,15,15), "lleftfootc": (145 ,279 ,17,17), "lrightthigh":(116 ,234 ,30,30), "lrightthighc":(116 ,234 ,30,30), \
                        "lrightleg": (118 ,257 ,28,28), "lrightlegc": (113 ,252 ,38,38),"lrightfoot": (117 ,281 ,15,15), "lrightfootc": (117 ,281 ,15,15), \
                        "lleftuparm": (135 ,198 ,42,42),"lleftuparmc": (135 ,198 ,42,42), "lleftdownarm": (135 ,203 ,42,42), "llefthand": (132 ,200 ,35,35),\
                        "lrightuparm": (105 ,198 ,42,42), "lrightuparmc": (105 ,198 ,42,42), "lrightdownarm": (105 ,198 ,42,42), "lrighthand": (112, 200, 35, 35)}
        self.partdic.update(partdic_rest)

        draw_order = []
        fhairidc, bhairidc = ["hair1", "hair2", "hair4", "hair9"], ["hair6","hair7", "hair3", "hair5","hair8"]
        leftdic, rightdic = ["lleftleg", "lleftthigh","lleftfoot"], \
                            ["lrightleg", "lrightthigh", "lrightfoot"]

        # 왼편을 바라볼 때
        draw_order = []
        draw_order.extend(["hatdownf", "hatglass", "hatup"])
        draw_order.extend(facedic)
        draw_order.extend(fhairidc)
        draw_order.extend(["lrighthand","llefthand", "lleftdownarm","lleftuparmc", "lleftuparm",\
                            "lleftthighc","lleftlegc", "lleftfootc", "lrightthighc","lrightlegc",  "lrightfootc", \
                           "downbodyc","leftbagnod", "rightbagnod","upbodyc","head", "neck", "upbody",\
                           "lrightdownarm","lrightuparmc", "lrightuparm"])
        draw_order.extend(leftdic)
        draw_order.extend(rightdic)
        draw_order.extend(["downbody"])
        draw_order.extend(bhairidc)
        draw_order.append("hatdownb")
        draw_order.append("bag")
        draw_order.reverse()
        global draw_order_left
        draw_order_left = draw_order

        # 오른편을 바라볼 때
        draw_order = []
        draw_order.extend(["hatdownf", "hatglass", "hatup"])
        draw_order.extend(facedic)
        draw_order.extend(fhairidc)
        draw_order.extend(["llefthand",  "lrighthand","lrightdownarm","lrightuparmc", "lrightuparm", \
                           "lrightthighc","lrightlegc",  "lrightfootc",  "lleftthighc","lleftlegc", "lleftfootc", \
                           "downbodyc","leftbagnod", "rightbagnod","upbodyc","head", "neck", "upbody",\
                           "lleftdownarm","lleftuparmc", "lleftuparm"])
        draw_order.extend(rightdic)
        draw_order.extend(leftdic)
        draw_order.extend(["downbody"])
        draw_order.extend(bhairidc)
        draw_order.append("hatdownb")
        draw_order.append("bag")
        draw_order.reverse()
        global draw_order_right
        draw_order_right = draw_order

        self.partdic2 = {}
        for p in self.partdic.keys():
            exec("""jessi.%s = {"theta":0, "pi2":0, "end_value_tuple_list":[], "position_x":0, "position_y":0}""" % p)
            exec("self.partdic2[p] = [jessi.%s, self.partdic[p]]" % p)
            t, left ,right = 0, 0, 0
            rotation_list = [
                ["downbody", 0], \
                ["upbody", "downbody"], \
                ["neck", "upbody"], \
                ["head", "neck"], \
                ["leo", "neck"], \
                ["lec", "neck"], \
                ["reo", "neck"], \
                ["rec", "neck"], \
                ["leb", "neck"], \
                ["reb", "neck"], \
                ["nose", "neck"], \
                ["mouth", "neck"], \
                ["hair1", "head"], \
                ["hair2", "head"], \
                ["hair3", "head"], \
                ["hair4", "head"], \
                ["hair5", "head"], \
                ["hair6", "head"], \
                ["hair7", "head"], \
                ["hair8", "hair3"], \
                ["hair9", "hair4"], \
                ["hatdownf", "head"], \
                ["hatdownb", "head"], \
                ["hatglass", "hatdownf"], \
                ["hatup", "head"], \
                ["lleftuparm", "upbody"], \
                ["lleftdownarm", "lleftuparm"], \
                ["llefthand", "lleftdownarm"], \
                ["lrightuparm", "upbody"], \
                ["lrightdownarm", "lrightuparm"], \
                ["lrighthand", "lrightdownarm"], \
                ["lleftthigh", "downbody"], \
                ["lleftleg", "lleftthigh"], \
                ["lleftfoot", "lleftleg"], \
                ["lrightthigh", "downbody"], \
                ["lrightleg", "lrightthigh"], \
                ["lrightfoot", "lrightleg"], \
                ["upbodyc", "upbody"], \
                ["leftbagnod", "upbody"], \
                ["rightbagnod", "upbody"], \
                ["bag", "upbody"], \
                ["downbodyc", "downbody"], \
                ["lleftthighc", "lleftthigh"], \
                ["lleftlegc", "lleftleg"], \
                ["lleftfootc", "lleftfoot"], \
                ["lrightthighc", "lrightthigh"], \
                ["lrightlegc", "lrightleg"], \
                ["lrightfootc", "lrightfoot"], \
                ["lleftuparmc", "lleftuparm"], \
                ["lrightuparmc", "lrightuparm"] ]
            for rl in rotation_list:
                if p == rl[0]:
                    if p == "downbody": pass
                    else: exec("self.partdic2[p].append(jessi.%s)" % rl[1])

        self.downbody["end_value_tuple_list"] = [(10, 1, 10, 1), (-10, 3, -10, 3), (1, -5, -1, -5), (0,0,0,0)]
        self.upbody["end_value_tuple_list"] = [(18, -6, 11, -10), (-13, -6, -18, -6), (4, -13, -4, -13), (0,0,0,0), (0,0,0,0),(0,0,0,0),(0,-12,0,-12)]
        self.neck["end_value_tuple_list"] = [(0, -2, 0, -2)]
        for i in range(len(facedic)) : self.neck["end_value_tuple_list"].append((0, -2, 0, -2))
        self.head["end_value_tuple_list"] = []
        hev = [(8, -35, 0, -35),(8, -35, 0, -35),(8, -38, 0, -38),(8, -38, 0, -38),(8, -38, 0, -38),  (20,15,30,15),(-30,15,-20,15)]
        for i in range(7) : self.head["end_value_tuple_list"].append(hev[i])
        self.hair3["end_value_tuple_list"] = [(-43,46,40,46)]
        self.hair4["end_value_tuple_list"] = [(40,48,-35,48)]

        self.head["end_value_tuple_list"].extend([(0, -35, 2, -35),(0, -35, 2, -35),(0, -35, 2, -35)])
        self.hatdownf["end_value_tuple_list"] = [(0,0,0,0)]

        self.lleftuparm["end_value_tuple_list"] = [(5, 11, -6, 11), (0,0,0,0)]
        self.lleftdownarm["end_value_tuple_list"] = [(-5, -7, 6, -7)]
        self.llefthand["end_value_tuple_list"] = []
        self.lrightuparm["end_value_tuple_list"] = [(-2, 11, 2, 11), (0,0,0,0)]
        self.lrightdownarm["end_value_tuple_list"] = [(0, -4, 0, -4)]
        self.lrighthand["end_value_tuple_list"] = []
        self.lleftthigh["end_value_tuple_list"] = [(1, 11, 1, 11), (0,0,0,0)]
        self.lleftleg["end_value_tuple_list"] = [(2, 9, -1, 9), (0,0,0,0)]
        self.lleftfoot["end_value_tuple_list"] = [(0,0,0,0)]
        self.lrightthigh["end_value_tuple_list"] = [(0, 10, 0, 10), (0,0,0,0)]
        self.lrightleg["end_value_tuple_list"] = [(-4, 9, 4, 9), (0,0,0,0)]
        self.lrightfoot["end_value_tuple_list"] = [(0,0,0,0)]

        for p in self.partdic:
            part = self.partdic2[p][0]
            subsf = self.partdic2[p][1]
            part["image"] = pygame.image.load('parts/'+p+'.png')
            part["image"] = part["image"].subsurface(subsf)
            part["r"] = part["image"].get_rect().size[0]
            part["leftimage"] = part["image"]
            part["rightimage"] = pygame.transform.flip(part["image"], True ,False)
            part["leftimages"] = [part["leftimage"]]
            part["rightimages"] = [part["rightimage"]]
            if p == "lleftfootc":
                part["leftimages"][0] = part["rightimage"]
                part["rightimages"][0] = part["leftimage"]
            for i in range(1, int(360/angle_split)):
                part["leftimages"].append(pygame.transform.rotate(part["leftimage"], i * angle_split))
                if p == "lleftfootc":
                    part["leftimages"][-1] = pygame.transform.rotate(part["rightimage"], i * angle_split)
                r, rr = part["leftimages"][0].get_rect().size[0], part["leftimages"][i].get_rect().size[0]
                part["leftimages"][i] = part["leftimages"][i].subsurface((rr - r) / 2, (rr - r) / 2, r, r)

                part["rightimages"].append(pygame.transform.rotate(part["rightimage"], i * angle_split))
                if p == "lleftthighc" or p == "lrightthighc" or p == "lleftfootc":
                    part["rightimages"][-1] = pygame.transform.rotate(part["leftimage"], i * angle_split)
                r, rr = part["rightimages"][0].get_rect().size[0], part["rightimages"][i].get_rect().size[0]
                part["rightimages"][i] = part["rightimages"][i].subsurface((rr - r) / 2, (rr - r) / 2, r, r)
    def JessiPartMove(self, t, act):
        if jessi.body.velocity.y < - up_down_minimun :
            act = "up"
            if abs(jessi.body.velocity.x) >= self.dash_speed - self.dash_act_amount :
                act = "dash"
        elif jessi.body.velocity.y > up_down_minimun :
            act = "down"

        for p in self.partdic2.keys() :
            part = self.partdic2[p][0]
            noe = len(part["end_value_tuple_list"])
            for i in range(noe) :
                part["left_end_point{}x".format(str(i+1))] = part["end_value_tuple_list"][i][0]
                part["left_end_point{}y".format(str(i+1))] = part["end_value_tuple_list"][i][1]
                part["right_end_point{}x".format(str(i+1))] = part["end_value_tuple_list"][i][2]
                part["right_end_point{}y".format(str(i+1))] = part["end_value_tuple_list"][i][3]
                part["end_point{}x".format(str(i+1))] = left * part["left_end_point{}x".format(str(i+1))] + right * part["right_end_point{}x".format(str(i+1))]
                part["end_point{}y".format(str(i+1))] = left * part["left_end_point{}y".format(str(i+1))] + right * part["right_end_point{}y".format(str(i+1))]

        # Animation
        if act == "stand" :
            rotation_list = [
                ["downbody", 0, 0, 0, (- 0 + (-1*sin(t/20)+1)*left + (-1*sin(t/20)+3)*(1-left), + 0 + (-1*sin(t/20)+1)*left + (1*sin(t/20)+1)*(1-left))], \
                ["upbody", "downbody", (-2*sin(t/20+pi/6)+25)/180*pi*left + -(2*sin(t/20+pi/8)+15)/180*pi*(1-left), 3, (0, -20, 0 ,-20)], \
                ["neck", "upbody", 0, 3, (0,-4,0,-4)], \
                ["head", "neck", (3*sin(t/20-pi/3)-15)/180*pi*left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-left), 1, (0,-35,0,-35)], \
                ["leo", "neck", (3*sin(t/20-pi/3)-15)/180*pi*left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-left), 1, (0,-35,0,-35)], \
                ["lec", "neck", (3*sin(t/20-pi/3)-15)/180*pi*left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-left), 1, (0,-35,0,-35)], \
                ["reo", "neck", (3*sin(t/20-pi/3)-15)/180*pi*left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-left), 1, (0,-35,0,-35)], \
                ["rec", "neck", (3*sin(t/20-pi/3)-15)/180*pi*left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-left), 1, (0,-35,0,-35)], \
                ["leb", "neck", (3*sin(t/20-pi/3)-15)/180*pi*left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-left), 1, (0,-35,0,-35)], \
                ["reb", "neck", (3*sin(t/20-pi/3)-15)/180*pi*left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-left), 1, (0,-35,0,-35)], \
                ["nose", "neck", (3*sin(t/20-pi/3)-15)/180*pi*left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-left), 1, (0,-35,0,-35)], \
                ["mouth", "neck", (3*sin(t/20-pi/3)-15)/180*pi*left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-left), 1, (0,-35,0,-35)], \
                ["hair1", "head",(1*sin(t/20))/180*pi*left + (1*sin(t/16)-10)/180*pi*(1-left), 1, (-10,35,10,35)], \
                ["hair2", "head",(1*sin(t/21))/180*pi*left + (1*sin(t/18)-10)/180*pi*(1-left), 2, (-10,35,10,35)], \
                ["hair3", "head",(1*sin(t/17)+5)/180*pi*left + (1*sin(t/15)-10)/180*pi*(1-left), 3, (-10,35,10,35)], \
                ["hair4", "head",(1*sin(t/18)+3)/180*pi*left + (1*sin(t/19)-10)/180*pi*(1-left), 4, (-10,35,10,35)], \
                ["hair5", "head",(1*sin(t/15))/180*pi*left + (1*sin(t/20)-5)/180*pi*(1-left), 5, (-10,35,10,35)], \
                ["hair6", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*(1-left), 6, (-23,-10,23,-10)], \
                ["hair7", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*(1-left), 7, (33,-7,-34,-8)], \
                ["hair8", "hair3",(5*sin(t/15)+10)/180*pi, 1, (40,-45,-35,-45)], \
                ["hair9", "hair4",(5*sin(t/17)+10)/180*pi, 1, (-45,-46,43,-46)], \
                ["hatdownf", "head", 0, 8, (0,0,0,0)], \
                ["hatdownb", "head", 0, 9, (0,0,0,0)], \
                ["hatglass", "hatdownf", 0, 1, (0,0,0,0)], \
                ["hatup", "head", 0, 10, (0,0,0,0)], \
                ["lleftuparm", "upbody", 0*left + pi/7*(1-left), 1, (2, 10, -2, 11)], \
                ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
                ["llefthand", "lleftdownarm", 0, 1, (0, -2, -5, -2)], \
                ["lrightuparm", "upbody", 0*left + -pi/7*right, 2, (-4,11,4,11)], \
                ["lrightdownarm", "lrightuparm", 0, 1, (2, -10, -2, -10)], \
                ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
                ["lleftthigh", "downbody", (5*sin(t/20) - 10)/180*pi*left + (5*sin(t/20) + 30)/180*pi*right, 1, (-4, 10, -4, 10)], \
                ["lleftleg", "lleftthigh", (-10*sin(t/20)+27)/180*pi*left + (-10*sin(t/20)-45)/180*pi*right, 1, (1, 8, -1, 8)], \
                ["lleftfoot", "lleftleg", -jessi.lleftleg["theta"], 1, (-1, 6, 1, 6)], \
                ["lrightthigh", "downbody", (5*sin(t/20)-10)/180*pi*left + (5*sin(t/20)+10)/180*pi*right, 2, (0, 9, 0, 9)], \
                ["lrightleg", "lrightthigh", (-10*sin(t/20)+35)/180*pi*left + (-10*sin(t/20)-30)/180*pi*right, 1, (1, 8, -2, 8)], \
                ["lrightfoot", "lrightleg", -jessi.lrightleg["theta"], 1, (-4, 6, 3, 6)], \
                ["upbodyc", "upbody", 0, 4, (0,0,0,0)], \
                ["leftbagnod", "upbody", 0, 5, (0,0,0,0)], \
                ["rightbagnod", "upbody", 0, 6, (0,0,0,0)], \
                ["bag", "upbody", 0, 7, (0,0,0,0)], \
                ["downbodyc", "downbody", 0, 4, (0,0,0,0)], \
                ["lleftthighc", "lleftthigh", 0, 2, (0,0,0,0)], \
                ["lleftlegc", "lleftleg", 0, 2, (0,0,0,0)], \
                ["lleftfootc", "lleftfoot", 0, 1, (0,0,0,0)], \
                ["lrightthighc", "lrightthigh", 0, 2, (0,0,0,0)], \
                ["lrightlegc", "lrightleg", 0, 2, (0,0,0,0)], \
                ["lrightfootc", "lrightfoot", 0, 1, (0,0,0,0)], \
                ["lleftuparmc", "lleftuparm", 0, 2, (0,0,0,0)], \
                ["lrightuparmc", "lrightuparm", 0, 2, (0,0,0,0)] ]
        if act == "walk" :
            head_theta = (-15)/180*pi*left + 0*right
            rotation_list = [
                ["downbody", 0, 0, 0, (-0, 0 + (3*sin(t/5-pi/2) + 1)*left + (3*sin(t/5-pi/2) + 1)*right)], \
                ["upbody", "downbody", (3*sin(t/20) + 15)/180*pi * left + (3*sin(t/20) + -8)/180*pi*right, 3, (0, -20, 0 ,-20)], \
                ["neck", "upbody", 0, 3, (0,-4,0,-4)], \
                ["head", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["lec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["rec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["nose", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["mouth", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["hair1", "head",(1 * sin(t / 20)) / 180 * pi * left + (1 * sin(t / 16) - 10) / 180 * pi * right, 1, (-10,35,10,35)], \
                ["hair2", "head",(1 * sin(t / 21)) / 180 * pi * left + (1 * sin(t / 18) - 10) / 180 * pi * right, 2, (-10,35,10,35)], \
                ["hair3", "head",(1 * sin(t / 17) + 5) / 180 * pi * left + (1 * sin(t / 15) - 10) / 180 * pi * right, 3, (-10,35,10,35)], \
                ["hair4", "head",(1 * sin(t / 18) + 3) / 180 * pi * left + (1 * sin(t / 19) - 10) / 180 * pi * right, 4, (-10,35,10,35)], \
                ["hair5", "head",(1 * sin(t / 15)) / 180 * pi * left + (1 * sin(t / 20) - 5) / 180 * pi * right, 5, (-10,35,10,35)], \
                ["hair6", "head",(3 * sin(t / 20)) / 180 * pi * left + (3 * sin(t / 20)) / 180 * pi * right, 6, (-23,-10,23,-10)], \
                ["hair7", "head",(3 * sin(t / 20)) / 180 * pi * left + (3 * sin(t / 20)) / 180 * pi * right, 7, (33,-7,-34,-8)], \
                ["hair8", "hair3",(5 * sin(t / 9) + 10) / 180 * pi, 1, (40,-45,-35,-45)], \
                ["hair9", "hair4",(5 * sin(t / 12) + 10) / 180 * pi, 1, (-45,-46,43,-46)], \
                ["hatdownf", "head", 0, 8, (0,0,0,0)], \
                ["hatdownb", "head", 0, 9, (0,0,0,0)], \
                ["hatglass", "hatdownf", 0, 1, (0,0,0,0)], \
                ["hatup", "head", 0, 10, (0,0,0,0)], \
                ["lleftuparm", "upbody", 0 * left + pi / 7 * right, 1, (2, 10, -2, 11)], \
                ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
                ["llefthand", "lleftdownarm", 0, 1, (0, -2, -5, -2)], \
                ["lrightuparm", "upbody", 0 * left + -pi / 7 * right, 2, (-4,11,4,11)], \
                ["lrightdownarm", "lrightuparm", 0, 1, (2, -10, -2, -10)], \
                ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
                ["lleftthigh", "downbody", (15*sin(t/10) - 5) / 180*pi*left + (15*sin(t/10) + 0)/180*pi*right, 1, (-4, 10, -4, 10)], \
                ["lleftleg", "lleftthigh", (5*sin(t/10) + 10) /180*pi*left + 0*right, 1, (1, 8, -1, 8)], \
                ["lleftfoot", "lleftleg", (2.5*sin(t/10)-2.5)/180*pi*left + 0*right, 1, (-1, 6, 1, 6)], \
                ["lrightthigh", "downbody", (-15*sin(t/10) + 5) / 180*pi*left + (-15*sin(t/10) + 10)/180*pi*right, 2, (0, 9, 0, 9)], \
                ["lrightleg", "lrightthigh", (-15*sin(t/10) + 20) /180*pi*left + (-5*sin(t/10)-30)/180*pi*right, 1, (1, 8, -2, 8)], \
                ["lrightfoot", "lrightleg", (10*sin(t/10)-20)/180*pi*left + (5*sin(t/10)+15)/180*pi*right, 1, (-4, 6, 3, 6)], \
                ["upbodyc", "upbody", 0, 4, (0,0,0,0)], \
                ["leftbagnod", "upbody", 0, 5, (0,0,0,0)], \
                ["rightbagnod", "upbody", 0, 6, (0,0,0,0)], \
                ["bag", "upbody", 0, 7, (0,0,0,0)], \
                ["downbodyc", "downbody", 0, 4, (0,0,0,0)], \
                ["lleftthighc", "lleftthigh", 0, 2, (0,0,0,0)], \
                ["lleftlegc", "lleftleg", 0, 2, (0,0,0,0)], \
                ["lleftfootc", "lleftfoot", 0, 1, (0,0,0,0)], \
                ["lrightthighc", "lrightthigh", 0, 2, (0,0,0,0)], \
                ["lrightlegc", "lrightleg", 0, 2, (0,0,0,0)], \
                ["lrightfootc", "lrightfoot", 0, 1, (0,0,0,0)], \
                ["lleftuparmc", "lleftuparm", 0, 2, (0,0,0,0)], \
                ["lrightuparmc", "lrightuparm", 0, 2, (0,0,0,0)] ]
        if act == "run" :
            head_theta = (3*sin(t/7)-15)/180*pi*left + (3*sin(t/7)+15)/180*pi*right
            rotation_list = [
                ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-0, 0 + 6+ (3*sin(t/3.5-pi/2) + -1)*left + (3*sin(t/3.5-pi/2) + -1)*right)], \
                ["upbody", "downbody", 30/180*pi*left + (-30)/180*pi*right, 3, (0, -20, 0 ,-20)], \
                ["neck", "upbody", (3*sin(t/6)-15)/180*pi*left + (3*sin(t/6)+15)/180*pi*right, 3, (0,-4,0,-4)], \
                ["head", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["lec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["rec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["nose", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["mouth", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["hair1", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/16)-10)/180*pi*right, 1, (-10,35,10,35)], \
                ["hair2", "head",(3*sin(t/10))/180*pi*left + (3*sin(t/18)-10)/180*pi*right, 2, (-10,35,10,35)], \
                ["hair3", "head",(3*sin(t/17))/180*pi*left + (3*sin(t/15)-10)/180*pi*right, 3, (-10,35,10,35)], \
                ["hair4", "head",(3*sin(t/12))/180*pi*left + (3*sin(t/19)-10)/180*pi*right, 4, (-10,35,10,35)], \
                ["hair5", "head",(3*sin(t/15))/180*pi*left + (3*sin(t/20)-5)/180*pi*right, 5, (-10,35,10,35)], \
                ["hair6", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 6, (-23,-10,23,-10)], \
                ["hair7", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 7, (33,-7,-34,-8)], \
                ["hair8", "hair3",(5*sin(t/9)+10)/180*pi, 1, (40,-45,-35,-45)], \
                ["hair9", "hair4",(5*sin(t/12)+10)/180*pi, 1, (-45,-46,43,-46)], \
                ["hatdownf", "head", 0, 8, (0,0,0,0)], \
                ["hatdownb", "head", 0, 9, (0,0,0,0)], \
                ["hatglass", "hatdownf", 0, 1, (0,1*sin(t/4)-1,0,1*sin(t/4)-1)], \
                ["hatup", "head", 0, 10, (0,0,0,0)], \
                ["lleftuparm", "upbody", (10*sin(t/7)-30)/180*pi*left + (10*sin(t/7)+40)/180*pi*right, 1, (2, 10, -2, 11)], \
                ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
                ["llefthand", "lleftdownarm", -jessi.lleftdownarm["theta"], 1, (0, -2, -5, -2)], \
                ["lrightuparm", "upbody", (-10*sin(t/7-pi/2)+10)/180*pi*left + (-10*sin(t/7+pi/2)+10)/180*pi*right, 2, (-4,11,4,11)], \
                ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
                ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
                ["lleftthigh", "downbody", (30*sin(t/7)-10)/180*pi*left + (40*sin(t/7)+10)/180*pi*right, 1, (-4, 10, -4, 10)], \
                ["lleftleg", "lleftthigh", (10*sin(t/7)+15)/180*pi*left + (10*sin(t/7)-15)/180*pi*right, 1, (1, 8, -1, 8)], \
                ["lleftfoot", "lleftleg", (2.5*sin(t/10)-2.5)/180*pi*left + 0*right, 1, (-1, 6, 1, 6)], \
                ["lrightthigh", "downbody", (-40*sin(t/7-pi/7)-10)/180*pi*left + (-30*sin(t/7+pi/6)+20)/180*pi*right, 2, (0, 9, 0, 9)], \
                ["lrightleg", "lrightthigh", (-10*sin(t/7)+40)/180*pi*left + (-10*sin(t/7)-40)/180*pi*right, 1, (1, 8, -2, 8)], \
                ["lrightfoot", "lrightleg", (10*sin(t/7)-30)/180*pi*left + (10*sin(t/7)+30)/180*pi*right, 1, (-4, 6, 3, 6)], \
                ["upbodyc", "upbody", 0, 4, (0,0,0,0)], \
                ["leftbagnod", "upbody", 0, 5, (0,0,0,0)], \
                ["rightbagnod", "upbody", 0, 6, (0,0,0,0)], \
                ["bag", "upbody", 0, 7, (0,0,0,0)], \
                ["downbodyc", "downbody", 0, 4, (0,0,0,0)], \
                ["lleftthighc", "lleftthigh", 0, 2, (0,0,0,0)], \
                ["lleftlegc", "lleftleg", 0, 2, (0,0,0,0)], \
                ["lleftfootc", "lleftfoot", 0, 1, (0,0,0,0)], \
                ["lrightthighc", "lrightthigh", 0, 2, (0,0,0,0)], \
                ["lrightlegc", "lrightleg", 0, 2, (0,0,0,0)], \
                ["lrightfootc", "lrightfoot", 0, 1, (0,0,0,0)], \
                ["lleftuparmc", "lleftuparm", 0, 2, (0,0,0,0)], \
                ["lrightuparmc", "lrightuparm", 0, 2, (0,0,0,0)] ]
        if act == "up" :
            head_theta = -15/180*pi*left + 15/180*pi*right
            rotation_list = [
                ["downbody", 0, (0)/180*pi*left + (-0)/180*pi*right, 0, (-0, 0)], \
                ["upbody", "downbody", 10/180*pi*left + (-10)/180*pi*right, 3, (0, -20, 0 ,-20)], \
                ["neck", "upbody", 0, 3, (0,-4,0,-4)], \
                ["head", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["lec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["rec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["nose", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["mouth", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["hair1", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/16)-10)/180*pi*right, 1, (-10,35,10,35)], \
                ["hair2", "head",(3*sin(t/10))/180*pi*left + (3*sin(t/18)-10)/180*pi*right, 2, (-10,35,10,35)], \
                ["hair3", "head",(3*sin(t/17))/180*pi*left + (3*sin(t/15)-10)/180*pi*right, 3, (-10,35,10,35)], \
                ["hair4", "head",(3*sin(t/12))/180*pi*left + (3*sin(t/19)-10)/180*pi*right, 4, (-10,35,10,35)], \
                ["hair5", "head",(3*sin(t/15))/180*pi*left + (3*sin(t/20)-5)/180*pi*right, 5, (-10,35,10,35)], \
                ["hair6", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 6, (-23,-10,23,-10)], \
                ["hair7", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 7, (33,-7,-34,-8)], \
                ["hair8", "hair3",(5*sin(t/9)+10)/180*pi, 1, (40,-45,-35,-45)], \
                ["hair9", "hair4",(5*sin(t/12)+10)/180*pi, 1, (-45,-46,43,-46)], \
                ["hatdownf", "head", 0, 8, (0,0,0,0)], \
                ["hatdownb", "head", 0, 9, (0,0,0,0)], \
                ["hatglass", "hatdownf", 0, 1, (0,0,0,0)], \
                ["hatup", "head", 0, 10, (0,0,0,0)], \
                ["lleftuparm", "upbody", -20/180*pi*left + 30/180*pi*right, 1, (2, 10, -2, 11)], \
                ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
                ["llefthand", "lleftdownarm", -jessi.lleftdownarm["theta"], 1, (0, -2, -5, -2)], \
                ["lrightuparm", "upbody", -0/180*pi*left + 10/180*pi*right, 2, (-4,11,4,11)], \
                ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
                ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
                ["lleftthigh", "downbody", -0/180*pi*left + -0/180*pi*right, 1, (-4, 10, -4, 10)], \
                ["lleftleg", "lleftthigh", 0/180*pi*left + -20/180*pi*right, 1, (1, 8, -1, 8)], \
                ["lleftfoot", "lleftleg", 35/180*pi*left + 0/180*pi*right, 1, (-1, 6, 1, 6)], \
                ["lrightthigh", "downbody", -0/180*pi*left + 0/180*pi*right, 2, (0, 9, 0, 9)], \
                ["lrightleg", "lrightthigh", 20/180*pi*left + -20/180*pi*right, 1, (1, 8, -2, 8)], \
                ["lrightfoot", "lrightleg", 15/180*pi*left + 0/180*pi*right, 1, (-4, 6, 3, 6)], \
                ["upbodyc", "upbody", 0, 4, (0,0,0,0)], \
                ["leftbagnod", "upbody", 0, 5, (0,0,0,0)], \
                ["rightbagnod", "upbody", 0, 6, (0,0,0,0)], \
                ["bag", "upbody", 0, 7, (0,0,0,0)], \
                ["downbodyc", "downbody", 0, 4, (0,0,0,0)], \
                ["lleftthighc", "lleftthigh", 0, 2, (0,0,0,0)], \
                ["lleftlegc", "lleftleg", 0, 2, (0,0,0,0)], \
                ["lleftfootc", "lleftfoot", 0, 1, (0,0,0,0)], \
                ["lrightthighc", "lrightthigh", 0, 2, (0,0,0,0)], \
                ["lrightlegc", "lrightleg", 0, 2, (0,0,0,0)], \
                ["lrightfootc", "lrightfoot", 0, 1, (0,0,0,0)], \
                ["lleftuparmc", "lleftuparm", 0, 2, (0,0,0,0)], \
                ["lrightuparmc", "lrightuparm", 0, 2, (0,0,0,0)] ]
        if act == "down" :
            head_theta = -15/180*pi*left + 15/180*pi*right
            rotation_list = [
                ["downbody", 0, (0)/180*pi*left + (-0)/180*pi*right, 0, (-0, 0)], \
                ["upbody", "downbody", 30/180*pi*left + (-30)/180*pi*right, 3, (0, -20, 0 ,-20)], \
                ["neck", "upbody", 0, 3, (0,-4,0,-4)], \
                ["head", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["lec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["rec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["nose", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["mouth", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["hair1", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/16)-10)/180*pi*right, 1, (-10,35,10,35)], \
                ["hair2", "head",(3*sin(t/10))/180*pi*left + (3*sin(t/18)-10)/180*pi*right, 2, (-10,35,10,35)], \
                ["hair3", "head",(3*sin(t/17))/180*pi*left + (3*sin(t/15)-10)/180*pi*right, 3, (-10,35,10,35)], \
                ["hair4", "head",(3*sin(t/12))/180*pi*left + (3*sin(t/19)-10)/180*pi*right, 4, (-10,35,10,35)], \
                ["hair5", "head",(3*sin(t/15))/180*pi*left + (3*sin(t/20)-5)/180*pi*right, 5, (-10,35,10,35)], \
                ["hair6", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 6, (-23,-10,23,-10)], \
                ["hair7", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 7, (33,-7,-34,-8)], \
                ["hair8", "hair3",(5*sin(t/9)+10)/180*pi, 1, (40,-45,-35,-45)], \
                ["hair9", "hair4",(5*sin(t/12)+10)/180*pi, 1, (-45,-46,43,-46)], \
                ["hatdownf", "head", 0, 8, (0,0,0,0)], \
                ["hatdownb", "head", 0, 9, (0,0,0,0)], \
                ["hatglass", "hatdownf", 0, 1, (0,0,0,0)], \
                ["hatup", "head", 0, 10, (0,0,0,0)], \
                ["lleftuparm", "upbody", -20/180*pi*left + 30/180*pi*right, 1, (2, 10, -2, 11)], \
                ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
                ["llefthand", "lleftdownarm", -jessi.lleftdownarm["theta"], 1, (0, -2, -5, -2)], \
                ["lrightuparm", "upbody", -0/180*pi*left + 10/180*pi*right, 2, (-4,11,4,11)], \
                ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
                ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
                ["lleftthigh", "downbody", -15/180*pi*left + 35/180*pi*right, 1, (-4, 10, -4, 10)], \
                ["lleftleg", "lleftthigh", 30/180*pi*left + -70/180*pi*right, 1, (1, 8, -1, 8)], \
                ["lleftfoot", "lleftleg", 35/180*pi*left + 0/180*pi*right, 1, (-1, 6, 1, 6)], \
                ["lrightthigh", "downbody", -20/180*pi*left + 20/180*pi*right, 2, (0, 9, 0, 9)], \
                ["lrightleg", "lrightthigh", 50/180*pi*left + -60/180*pi*right, 1, (1, 8, -2, 8)], \
                ["lrightfoot", "lrightleg", 15/180*pi*left + 0/180*pi*right, 1, (-4, 6, 3, 6)], \
                ["upbodyc", "upbody", 0, 4, (0,0,0,0)], \
                ["leftbagnod", "upbody", 0, 5, (0,0,0,0)], \
                ["rightbagnod", "upbody", 0, 6, (0,0,0,0)], \
                ["bag", "upbody", 0, 7, (0,0,0,0)], \
                ["downbodyc", "downbody", 0, 4, (0,0,0,0)], \
                ["lleftthighc", "lleftthigh", 0, 2, (0,0,0,0)], \
                ["lleftlegc", "lleftleg", 0, 2, (0,0,0,0)], \
                ["lleftfootc", "lleftfoot", 0, 1, (0,0,0,0)], \
                ["lrightthighc", "lrightthigh", 0, 2, (0,0,0,0)], \
                ["lrightlegc", "lrightleg", 0, 2, (0,0,0,0)], \
                ["lrightfootc", "lrightfoot", 0, 1, (0,0,0,0)], \
                ["lleftuparmc", "lleftuparm", 0, 2, (0,0,0,0)], \
                ["lrightuparmc", "lrightuparm", 0, 2, (0,0,0,0)] ]
        if act == "land" :
            head_theta = -30/180*pi*left + 30/180*pi*right
            rotation_list = [
                ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-0, 0 + 13*left + 10*right)], \
                ["upbody", "downbody", 40/180*pi*left + (-40)/180*pi*right, 3, (0, -20, 0 ,-20)], \
                ["neck", "upbody", 0, 3, (0,-4,0,-4)], \
                ["head", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["lec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["rec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["nose", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["mouth", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["hair1", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/16)-10)/180*pi*right, 1, (-10,35,10,35)], \
                ["hair2", "head",(3*sin(t/10))/180*pi*left + (3*sin(t/18)-10)/180*pi*right, 2, (-10,35,10,35)], \
                ["hair3", "head",(3*sin(t/17))/180*pi*left + (3*sin(t/15)-10)/180*pi*right, 3, (-10,35,10,35)], \
                ["hair4", "head",(3*sin(t/12))/180*pi*left + (3*sin(t/19)-10)/180*pi*right, 4, (-10,35,10,35)], \
                ["hair5", "head",(3*sin(t/15))/180*pi*left + (3*sin(t/20)-5)/180*pi*right, 5, (-10,35,10,35)], \
                ["hair6", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 6, (-23,-10,23,-10)], \
                ["hair7", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 7, (33,-7,-34,-8)], \
                ["hair8", "hair3",(5*sin(t/9)+10)/180*pi, 1, (40,-45,-35,-45)], \
                ["hair9", "hair4",(5*sin(t/12)+10)/180*pi, 1, (-45,-46,43,-46)], \
                ["hatdownf", "head", 0, 8, (0,0,0,0)], \
                ["hatdownb", "head", 0, 9, (0,0,0,0)], \
                ["hatglass", "hatdownf", 0, 1, (0,0,0,0)], \
                ["hatup", "head", 0, 10, (0,0,0,0)], \
                ["lleftuparm", "upbody", -20/180*pi*left + 30/180*pi*right, 1, (2, 10, -2, 11)], \
                ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
                ["llefthand", "lleftdownarm", 0, 1, (0, -2, -5, -2)], \
                ["lrightuparm", "upbody", -0/180*pi*left + 10/180*pi*right, 2, (-4,11,4,11)], \
                ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
                ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
                ["lleftthigh", "downbody", -40/180*pi*left + 50/180*pi*right, 1, (-4, 10, -4, 10)], \
                ["lleftleg", "lleftthigh", 85/180*pi*left + -100/180*pi*right, 1, (1, 8, -1, 8)], \
                ["lleftfoot", "lleftleg", -jessi.lleftleg["theta"], 1, (-1, 6, 1, 6)], \
                ["lrightthigh", "downbody", -50/180*pi*left + 40/180*pi*right, 2, (0, 9, 0, 9)], \
                ["lrightleg", "lrightthigh", 120/180*pi*left + -90/180*pi*right, 1, (1, 8, -2, 8)], \
                ["lrightfoot", "lrightleg", -jessi.lrightleg["theta"], 1, (-4, 6, 3, 6)], \
                ["upbodyc", "upbody", 0, 4, (0,0,0,0)], \
                ["leftbagnod", "upbody", 0, 5, (0,0,0,0)], \
                ["rightbagnod", "upbody", 0, 6, (0,0,0,0)], \
                ["bag", "upbody", 0, 7, (0,0,0,0)], \
                ["downbodyc", "downbody", 0, 4, (0,0,0,0)], \
                ["lleftthighc", "lleftthigh", 0, 2, (0,0,0,0)], \
                ["lleftlegc", "lleftleg", 0, 2, (0,0,0,0)], \
                ["lleftfootc", "lleftfoot", 0, 1, (0,0,0,0)], \
                ["lrightthighc", "lrightthigh", 0, 2, (0,0,0,0)], \
                ["lrightlegc", "lrightleg", 0, 2, (0,0,0,0)], \
                ["lrightfootc", "lrightfoot", 0, 1, (0,0,0,0)], \
                ["lleftuparmc", "lleftuparm", 0, 2, (0,0,0,0)], \
                ["lrightuparmc", "lrightuparm", 0, 2, (0,0,0,0)] ]
        if act == "soft land" :
            head_theta = -30/180*pi*left + 30/180*pi*right
            rotation_list = [
                ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-0, 2*left + 8*right)], \
                ["upbody", "downbody", 40/180*pi*left + (-40)/180*pi*right, 3, (0, -20, 0 ,-20)], \
                ["neck", "upbody", 0, 3, (0,-4,0,-4)], \
                ["head", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["lec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["rec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["nose", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["mouth", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["hair1", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/16)-10)/180*pi*right, 1, (-10,35,10,35)], \
                ["hair2", "head",(3*sin(t/10))/180*pi*left + (3*sin(t/18)-10)/180*pi*right, 2, (-10,35,10,35)], \
                ["hair3", "head",(3*sin(t/17))/180*pi*left + (3*sin(t/15)-10)/180*pi*right, 3, (-10,35,10,35)], \
                ["hair4", "head",(3*sin(t/12))/180*pi*left + (3*sin(t/19)-10)/180*pi*right, 4, (-10,35,10,35)], \
                ["hair5", "head",(3*sin(t/15))/180*pi*left + (3*sin(t/20)-5)/180*pi*right, 5, (-10,35,10,35)], \
                ["hair6", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 6, (-23,-10,23,-10)], \
                ["hair7", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 7, (33,-7,-34,-8)], \
                ["hair8", "hair3",(5*sin(t/9)+10)/180*pi, 1, (40,-45,-35,-45)], \
                ["hair9", "hair4",(5*sin(t/12)+10)/180*pi, 1, (-45,-46,43,-46)], \
                ["hatdownf", "head", 0, 8, (0,0,0,0)], \
                ["hatdownb", "head", 0, 9, (0,0,0,0)], \
                ["hatglass", "hatdownf", 0, 1, (0,0,0,0)], \
                ["hatup", "head", 0, 10, (0,0,0,0)], \
                ["lleftuparm", "upbody", -20/180*pi*left + 30/180*pi*right, 1, (2, 10, -2, 11)], \
                ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
                ["llefthand", "lleftdownarm", 0, 1, (0, -2, -5, -2)], \
                ["lrightuparm", "upbody", -0/180*pi*left + 10/180*pi*right, 2, (-4,11,4,11)], \
                ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
                ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
                ["lleftthigh", "downbody", -20/180*pi*left + 55/180*pi*right, 1, (-4, 10, -4, 10)], \
                ["lleftleg", "lleftthigh", 30/180*pi*left + -80/180*pi*right, 1, (1, 8, -1, 8)], \
                ["lleftfoot", "lleftleg", -jessi.lleftleg["theta"], 1, (-1, 6, 1, 6)], \
                ["lrightthigh", "downbody", -20/180*pi*left + 40/180*pi*right, 2, (0, 9, 0, 9)], \
                ["lrightleg", "lrightthigh", 55/180*pi*left + -80/180*pi*right, 1, (1, 8, -2, 8)], \
                ["lrightfoot", "lrightleg", -jessi.lrightleg["theta"], 1, (-4, 6, 3, 6)], \
                ["upbodyc", "upbody", 0, 4, (0,0,0,0)], \
                ["leftbagnod", "upbody", 0, 5, (0,0,0,0)], \
                ["rightbagnod", "upbody", 0, 6, (0,0,0,0)], \
                ["bag", "upbody", 0, 7, (0,0,0,0)], \
                ["downbodyc", "downbody", 0, 4, (0,0,0,0)], \
                ["lleftthighc", "lleftthigh", 0, 2, (0,0,0,0)], \
                ["lleftlegc", "lleftleg", 0, 2, (0,0,0,0)], \
                ["lleftfootc", "lleftfoot", 0, 1, (0,0,0,0)], \
                ["lrightthighc", "lrightthigh", 0, 2, (0,0,0,0)], \
                ["lrightlegc", "lrightleg", 0, 2, (0,0,0,0)], \
                ["lrightfootc", "lrightfoot", 0, 1, (0,0,0,0)], \
                ["lleftuparmc", "lleftuparm", 0, 2, (0,0,0,0)], \
                ["lrightuparmc", "lrightuparm", 0, 2, (0,0,0,0)] ]
        if act == "hard land" :
            head_theta = -30/180*pi*left + 30/180*pi*right
            rotation_list = [
                ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-0, 20*left + 17*right)], \
                ["upbody", "downbody", 40/180*pi*left + (-40)/180*pi*right, 3, (0, -20, 0 ,-20)], \
                ["neck", "upbody", 0, 3, (0,-4,0,-4)], \
                ["head", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["lec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["rec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["nose", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["mouth", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["hair1", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/16)-10)/180*pi*right, 1, (-10,35,10,35)], \
                ["hair2", "head",(3*sin(t/10))/180*pi*left + (3*sin(t/18)-10)/180*pi*right, 2, (-10,35,10,35)], \
                ["hair3", "head",(3*sin(t/17))/180*pi*left + (3*sin(t/15)-10)/180*pi*right, 3, (-10,35,10,35)], \
                ["hair4", "head",(3*sin(t/12))/180*pi*left + (3*sin(t/19)-10)/180*pi*right, 4, (-10,35,10,35)], \
                ["hair5", "head",(3*sin(t/15))/180*pi*left + (3*sin(t/20)-5)/180*pi*right, 5, (-10,35,10,35)], \
                ["hair6", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 6, (-23,-10,23,-10)], \
                ["hair7", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 7, (33,-7,-34,-8)], \
                ["hair8", "hair3",(5*sin(t/9)+10)/180*pi, 1, (40,-45,-35,-45)], \
                ["hair9", "hair4",(5*sin(t/12)+10)/180*pi, 1, (-45,-46,43,-46)], \
                ["hatdownf", "head", 0, 8, (0,0,0,0)], \
                ["hatdownb", "head", 0, 9, (0,0,0,0)], \
                ["hatglass", "hatdownf", 0, 1, (0,0,0,0)], \
                ["hatup", "head", 0, 10, (0,0,0,0)], \
                ["lleftuparm", "upbody", -20/180*pi*left + 30/180*pi*right, 1, (2, 10, -2, 11)], \
                ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
                ["llefthand", "lleftdownarm", -jessi.lleftdownarm["theta"], 1, (0, -2, -5, -2)], \
                ["lrightuparm", "upbody", -0/180*pi*left + 10/180*pi*right, 2, (-4,11,4,11)], \
                ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
                ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
                ["lleftthigh", "downbody", -50/180*pi*left + 70/180*pi*right, 1, (-4, 10, -4, 10)], \
                ["lleftleg", "lleftthigh", 105/180*pi*left + -130/180*pi*right, 1, (1, 8, -1, 8)], \
                ["lleftfoot", "lleftleg", -jessi.lleftleg["theta"], 1, (-1, 6, 1, 6)], \
                ["lrightthigh", "downbody", -70/180*pi*left + 60/180*pi*right, 2, (0, 9, 0, 9)], \
                ["lrightleg", "lrightthigh", 140/180*pi*left + -120/180*pi*right, 1, (1, 8, -2, 8)], \
                ["lrightfoot", "lrightleg", -jessi.lrightleg['theta'], 1, (-4, 6, 3, 6)], \
                ["upbodyc", "upbody", 0, 4, (0,0,0,0)], \
                ["leftbagnod", "upbody", 0, 5, (0,0,0,0)], \
                ["rightbagnod", "upbody", 0, 6, (0,0,0,0)], \
                ["bag", "upbody", 0, 7, (0,0,0,0)], \
                ["downbodyc", "downbody", 0, 4, (0,0,0,0)], \
                ["lleftthighc", "lleftthigh", 0, 2, (0,0,0,0)], \
                ["lleftlegc", "lleftleg", 0, 2, (0,0,0,0)], \
                ["lleftfootc", "lleftfoot", 0, 1, (0,0,0,0)], \
                ["lrightthighc", "lrightthigh", 0, 2, (0,0,0,0)], \
                ["lrightlegc", "lrightleg", 0, 2, (0,0,0,0)], \
                ["lrightfootc", "lrightfoot", 0, 1, (0,0,0,0)], \
                ["lleftuparmc", "lleftuparm", 0, 2, (0,0,0,0)], \
                ["lrightuparmc", "lrightuparm", 0, 2, (0,0,0,0)] ]
        if act == "sit" :
            head_theta = -30/180*pi*left + 30/180*pi*right
            rotation_list = [
                ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-0, 4)], \
                ["upbody", "downbody", 40/180*pi*left + (-40)/180*pi*right, 3, (0, -20, 0 ,-20)], \
                ["neck", "upbody", 0, 3, (0,-4,0,-4)], \
                ["head", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["lec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["rec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["nose", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["mouth", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["hair1", "head",(1*sin(t/20))/180*pi*left + (1*sin(t/16)-10)/180*pi*(1-left), 1, (-10,35,10,35)], \
                ["hair2", "head",(1*sin(t/21))/180*pi*left + (1*sin(t/18)-10)/180*pi*(1-left), 2, (-10,35,10,35)], \
                ["hair3", "head",(1*sin(t/17)+5)/180*pi*left + (1*sin(t/15)-10)/180*pi*(1-left), 3, (-10,35,10,35)], \
                ["hair4", "head",(1*sin(t/18)+3)/180*pi*left + (1*sin(t/19)-10)/180*pi*(1-left), 4, (-10,35,10,35)], \
                ["hair5", "head",(1*sin(t/15))/180*pi*left + (1*sin(t/20)-5)/180*pi*(1-left), 5, (-10,35,10,35)], \
                ["hair6", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*(1-left), 6, (-23,-10,23,-10)], \
                ["hair7", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*(1-left), 7, (33,-7,-34,-8)], \
                ["hair8", "hair3",(5*sin(t/15)+10)/180*pi, 1, (40,-45,-35,-45)], \
                ["hair9", "hair4",(5*sin(t/17)+10)/180*pi, 1, (-45,-46,43,-46)], \
                ["hatdownf", "head", 0, 8, (0,0,0,0)], \
                ["hatdownb", "head", 0, 9, (0,0,0,0)], \
                ["hatglass", "hatdownf", 0, 1, (0,0,0,0)], \
                ["hatup", "head", 0, 10, (0,0,0,0)], \
                ["lleftuparm", "upbody", -20/180*pi*left + 30/180*pi*right, 1, (2, 10, -2, 11)], \
                ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
                ["llefthand", "lleftdownarm", 0, 1, (0, -2, -5, -2)], \
                ["lrightuparm", "upbody", -0/180*pi*left + 10/180*pi*right, 2, (-4,11,4,11)], \
                ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
                ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
                ["lleftthigh", "downbody", -70/180*pi*left + 90/180*pi*right, 1, (-4, 10, -4, 10)], \
                ["lleftleg", "lleftthigh", 115/180*pi*left + -140/180*pi*right, 1, (1, 8, -1, 8)], \
                ["lleftfoot", "lleftleg", -jessi.lleftleg["theta"], 1, (-1, 6, 1, 6)], \
                ["lrightthigh", "downbody", -70/180*pi*left + 90/180*pi*right, 2, (0, 9, 0, 9)], \
                ["lrightleg", "lrightthigh", 150/180*pi*left + -130/180*pi*right, 1, (1, 8, -2, 8)], \
                ["lrightfoot", "lrightleg", -jessi.lrightleg["theta"], 1, (-4, 6, 3, 6)], \
                ["upbodyc", "upbody", 0, 4, (0,0,0,0)], \
                ["leftbagnod", "upbody", 0, 5, (0,0,0,0)], \
                ["rightbagnod", "upbody", 0, 6, (0,0,0,0)], \
                ["bag", "upbody", 0, 7, (0,0,0,0)], \
                ["downbodyc", "downbody", 0, 4, (0,0,0,0)], \
                ["lleftthighc", "lleftthigh", 0, 2, (0,0,0,0)], \
                ["lleftlegc", "lleftleg", 0, 2, (0,0,0,0)], \
                ["lleftfootc", "lleftfoot", 0, 1, (0,0,0,0)], \
                ["lrightthighc", "lrightthigh", 0, 2, (0,0,0,0)], \
                ["lrightlegc", "lrightleg", 0, 2, (0,0,0,0)], \
                ["lrightfootc", "lrightfoot", 0, 1, (0,0,0,0)], \
                ["lleftuparmc", "lleftuparm", 0, 2, (0,0,0,0)], \
                ["lrightuparmc", "lrightuparm", 0, 2, (0,0,0,0)] ]
        if act == "sit walk" :
            head_theta = -30/180*pi*left + 30/180*pi*right
            rotation_list = [
                ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-0, 5*left + 5*right)], \
                ["upbody", "downbody", (-5*sin(t/15)+40)/180*pi*left + (5*sin(t/15)+-40)/180*pi*right, 3, (0, -20, 0 ,-20)], \
                ["neck", "upbody", 0, 3, (0,-4,0,-4)], \
                ["head", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["lec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["rec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["nose", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["mouth", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["hair1", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/16)-10)/180*pi*right, 1, (-10,35,10,35)], \
                ["hair2", "head",(3*sin(t/10))/180*pi*left + (3*sin(t/18)-10)/180*pi*right, 2, (-10,35,10,35)], \
                ["hair3", "head",(3*sin(t/17))/180*pi*left + (3*sin(t/15)-10)/180*pi*right, 3, (-10,35,10,35)], \
                ["hair4", "head",(3*sin(t/12))/180*pi*left + (3*sin(t/19)-10)/180*pi*right, 4, (-10,35,10,35)], \
                ["hair5", "head",(3*sin(t/15))/180*pi*left + (3*sin(t/20)-5)/180*pi*right, 5, (-10,35,10,35)], \
                ["hair6", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 6, (-23,-10,23,-10)], \
                ["hair7", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 7, (33,-7,-34,-8)], \
                ["hair8", "hair3",(5*sin(t/9)+10)/180*pi, 1, (40,-45,-35,-45)], \
                ["hair9", "hair4",(5*sin(t/12)+10)/180*pi, 1, (-45,-46,43,-46)], \
                ["hatdownf", "head", 0, 8, (0,0,0,0)], \
                ["hatdownb", "head", 0, 9, (0,0,0,0)], \
                ["hatglass", "hatdownf", 0, 1, (0,0,0,0)], \
                ["hatup", "head", 0, 10, (0,0,0,0)], \
                ["lleftuparm", "upbody", -20/180*pi*left + 30/180*pi*right, 1, (2, 10, -2, 11)], \
                ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
                ["llefthand", "lleftdownarm", -jessi.lleftdownarm["theta"], 1, (0, -2, -5, -2)], \
                ["lrightuparm", "upbody", -0/180*pi*left + 10/180*pi*right, 2, (-4,11,4,11)], \
                ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
                ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
                ["lleftthigh", "downbody", (30*sin(t/15)-70)/180*pi*left + (30*sin(t/15)+90)/180*pi*right, 1, (-4, 10, -4, 10)], \
                ["lleftleg", "lleftthigh", (15*sin(t/15)+115)/180*pi*left + -140/180*pi*right, 1, (1, 8, -1, 8)], \
                ["lleftfoot", "lleftleg", (-30*sin(t/15) - 45)/180*pi*left + 45/180*pi*right, 1, (-1, 6, 1, 6)], \
                ["lrightthigh", "downbody", (-30*sin(t/15)-70)/180*pi*left + (-30*sin(t/15)+90)/180*pi*right, 2, (0, 9, 0, 9)], \
                ["lrightleg", "lrightthigh", 160/180*pi*left + -130/180*pi*right, 1, (1, 8, -2, 8)], \
                ["lrightfoot", "lrightleg", (-30*sin(t/15) - 45)/180*pi*left + 45/180*pi*right, 1, (-4, 6, 3, 6)], \
                ["upbodyc", "upbody", 0, 4, (0,0,0,0)], \
                ["leftbagnod", "upbody", 0, 5, (0,0,0,0)], \
                ["rightbagnod", "upbody", 0, 6, (0,0,0,0)], \
                ["bag", "upbody", 0, 7, (0,0,0,0)], \
                ["downbodyc", "downbody", 0, 4, (0,0,0,0)], \
                ["lleftthighc", "lleftthigh", 0, 2, (0,0,0,0)], \
                ["lleftlegc", "lleftleg", 0, 2, (0,0,0,0)], \
                ["lleftfootc", "lleftfoot", 0, 1, (0,0,0,0)], \
                ["lrightthighc", "lrightthigh", 0, 2, (0,0,0,0)], \
                ["lrightlegc", "lrightleg", 0, 2, (0,0,0,0)], \
                ["lrightfootc", "lrightfoot", 0, 1, (0,0,0,0)], \
                ["lleftuparmc", "lleftuparm", 0, 2, (0,0,0,0)], \
                ["lrightuparmc", "lrightuparm", 0, 2, (0,0,0,0)] ]
        if act == "dash" :
            head_theta = (3*sin(t/7)-5)/180*pi*left + (3*sin(t/7)+5)/180*pi*right
            rotation_list = [
                ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-0, 0 + 4+ (3*sin(t/3.5-pi/2) + -1)*left + (3*sin(t/3.5-pi/2) + -1)*right)], \
                ["upbody", "downbody", 15/180*pi*left + (-15)/180*pi*right, 3, (0, -20, 0 ,-20)], \
                ["neck", "upbody", (3*sin(t/6)-15)/180*pi*left + (3*sin(t/6)+15)/180*pi*right, 3, (0,-4,0,-4)], \
                ["head", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["lec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reo", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["rec", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["leb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["reb", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["nose", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["mouth", "neck", head_theta, 1, (0,-35,0,-35)], \
                ["hair1", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/16)-10)/180*pi*right, 1, (-10,35,10,35)], \
                ["hair2", "head",(3*sin(t/10))/180*pi*left + (3*sin(t/18)-10)/180*pi*right, 2, (-10,35,10,35)], \
                ["hair3", "head",(3*sin(t/17))/180*pi*left + (3*sin(t/15)-10)/180*pi*right, 3, (-10,35,10,35)], \
                ["hair4", "head",(3*sin(t/12))/180*pi*left + (3*sin(t/19)-10)/180*pi*right, 4, (-10,35,10,35)], \
                ["hair5", "head",(3*sin(t/15))/180*pi*left + (3*sin(t/20)-5)/180*pi*right, 5, (-10,35,10,35)], \
                ["hair6", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 6, (-23,-10,23,-10)], \
                ["hair7", "head",(3*sin(t/20))/180*pi*left + (3*sin(t/20))/180*pi*right, 7, (33,-7,-34,-8)], \
                ["hair8", "hair3",(5*sin(t/9)+10)/180*pi, 1, (40,-45,-35,-45)], \
                ["hair9", "hair4",(5*sin(t/12)+10)/180*pi, 1, (-45,-46,43,-46)], \
                ["hatdownf", "head", 0, 8, (0,0,0,0)], \
                ["hatdownb", "head", 0, 9, (0,0,0,0)], \
                ["hatglass", "hatdownf", 0, 1, (0,1*sin(t/4)-1,0,1*sin(t/4)-1)], \
                ["hatup", "head", 0, 10, (0,0,0,0)], \
                ["lleftuparm", "upbody", (-5)/180*pi*left + (70)/180*pi*right, 1, (2, 10, -2, 11)], \
                ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
                ["llefthand", "lleftdownarm", -jessi.lleftdownarm["theta"], 1, (0, -2, -5, -2)], \
                ["lrightuparm", "upbody", (-40)/180*pi*left + (-15)/180*pi*right, 2, (-4,11,4,11)], \
                ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
                ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
                ["lleftthigh", "downbody", (-75)/180*pi*left + (-20)/180*pi*right, 1, (-4, 10, -4, 10)], \
                ["lleftleg", "lleftthigh", (10*sin(t/7)+15)/180*pi*left + (10*sin(t/7)-35)/180*pi*right, 1, (1, 8, -1, 8)], \
                ["lleftfoot", "lleftleg", (2.5*sin(t/10)-2.5)/180*pi*left + 0*right, 1, (-1, 6, 1, 6)], \
                ["lrightthigh", "downbody", (20)/180*pi*left + (75)/180*pi*right, 2, (0, 9, 0, 9)], \
                ["lrightleg", "lrightthigh", (-10*sin(t/7)+40)/180*pi*left + (-10*sin(t/7)-40)/180*pi*right, 1, (1, 8, -2, 8)], \
                ["lrightfoot", "lrightleg", (10*sin(t/7)-30)/180*pi*left + (10*sin(t/7)+30)/180*pi*right, 1, (-4, 6, 3, 6)], \
                ["upbodyc", "upbody", 0, 4, (0,0,0,0)], \
                ["leftbagnod", "upbody", 0, 5, (0,0,0,0)], \
                ["rightbagnod", "upbody", 0, 6, (0,0,0,0)], \
                ["bag", "upbody", 0, 7, (0,0,0,0)], \
                ["downbodyc", "downbody", 0, 4, (0,0,0,0)], \
                ["lleftthighc", "lleftthigh", 0, 2, (0,0,0,0)], \
                ["lleftlegc", "lleftleg", 0, 2, (0,0,0,0)], \
                ["lleftfootc", "lleftfoot", 0, 1, (0,0,0,0)], \
                ["lrightthighc", "lrightthigh", 0, 2, (0,0,0,0)], \
                ["lrightlegc", "lrightleg", 0, 2, (0,0,0,0)], \
                ["lrightfootc", "lrightfoot", 0, 1, (0,0,0,0)], \
                ["lleftuparmc", "lleftuparm", 0, 2, (0,0,0,0)], \
                ["lrightuparmc", "lrightuparm", 0, 2, (0,0,0,0)] ]

        self.rotation_list = rotation_list
        for l in rotation_list :
            part = self.partdic2[l[0]][0]
            if l[0] == "downbody":
                part["start_point_x"], part["start_point_y"] = l[4]
            else :
                upart = self.partdic2[l[0]][2]
                part["pi2"] = l[2]
                part["start_point_x"], part["start_point_y"] = upart["end_point{}x".format(l[3])], upart["end_point{}y".format(l[3])]
                part["left_center_x"], part["left_center_y"], part["right_center_x"], part["right_center_y"] = l[4]

        if t >= 2 :
            for p in self.partdic : # 모든 parts에서
                part = self.partdic2[p][0]
                if p == "downbody" :
                    if abs(part["start_point_y"] - part["bposition_spy"]) >= 5 :
                        if act == 'land' :
                            part["pi2"] = part["theta2"] + (part["pi2"] - part["theta2"]) / 2
                            part["start_point_y"] = part["bposition_spy"] + (part["start_point_y"] - part["bposition_spy"]) / 2
                        else :
                            part["pi2"] = part['theta2'] + (part["pi2"] - part["theta2"]) / 3
                            part["start_point_y"] = part["bposition_spy"] + (part["start_point_y"] - part["bposition_spy"]) / 3
                    continue
                if (part["lr"] == 'left' and left) or (part["lr"] == 'right' and right) :
                    if abs(part["pi2"] - part["theta2"]) >= 1/10 :
                        if act == "land" or act == "sit" :
                            part["pi2"] = part["theta2"] + (part["pi2"] - part["theta2"]) / 2
                        else :
                            part["pi2"] = part["theta2"] + (part["pi2"] - part["theta2"]) / 4

        # downbody
        if left : self.downbody["rotate"] = self.downbody["leftimages"][round(self.downbody["pi2"]*180/pi/angle_split)%int(360/angle_split)]
        elif right : self.downbody["rotate"] = self.downbody["rightimages"][round(self.downbody["pi2"]*180/pi/angle_split)%int(360/angle_split)]
        jessi.downbody["position_x"], jessi.downbody["position_y"] = self.body.position - (15,-20) - (0, -(jessi.act == "sit" or jessi.act == "sit walk")*20) - map.position + self.rotation_list[0][4]
        jessi.downbody["theta"] = self.rotation_list[0][2]
        if left : jessi.downbody["rotate"] = jessi.downbody["leftimages"][round(jessi.downbody["theta"]*180/pi/angle_split)%int(360/angle_split)]
        if right : jessi.downbody["rotate"] = jessi.downbody["rightimages"][round(jessi.downbody["theta"]*180/pi/angle_split)%int(360/angle_split)]
        cx, cy = jessi.downbody['position_x'], jessi.downbody["position_y"]
        ct, st = cos(-self.downbody["pi2"]), sin(-self.downbody["pi2"])
        for i in range(len(self.downbody["end_value_tuple_list"])) :
            self.downbody["end_point{}rx".format(i+1)] = ct * self.downbody["end_point{}x".format(i+1)] - st * self.downbody["end_point{}y".format(i+1)]
            self.downbody["end_point{}ry".format(i+1)] = st * self.downbody["end_point{}x".format(i+1)] + ct * self.downbody["end_point{}y".format(i+1)]

        partdic3 = list(self.partdic.keys()).copy()
        if left : draw_order_copy = draw_order_left.copy()
        elif right : draw_order_copy = draw_order_right.copy()

        partdic3.remove("downbody")

        draw_order_copy.remove("downbody")
        draw_order_copy.remove("upbody")
        draw_order_copy.remove("lleftthigh")
        draw_order_copy.remove("lleftleg")
        draw_order_copy.remove("lrightthigh")
        draw_order_copy.remove("lrightleg")
        draw_order_copy.remove("lleftfoot")
        draw_order_copy.remove("lrightfoot")

        # partdic3.remove("downbodyc")
        # draw_order_copy.remove("downbodyc")
        # partdic3.remove("lleftthighc")
        # draw_order_copy.remove("lleftthighc")
        # partdic3.remove("lrightthighc")
        # draw_order_copy.remove("lrightthighc")
        # partdic3.remove("hatglass")
        # partdic3.remove("hatup")
        # partdic3.remove("hatdownf")
        # partdic3.remove("hatdownb")
        # draw_order_copy.remove("hatglass")
        # draw_order_copy.remove("hatup")
        # draw_order_copy.remove("hatdownf")
        # draw_order_copy.remove("hatdownb")

        if "eye_close" == "eye_close" :
            ect = 0
            if t%60 == 1 :
                ect = randint(10,50)
            if ect < t%60 < ect+15 :
                partdic3.remove("leo")
                partdic3.remove("reo")
                draw_order_copy.remove("leo")
                draw_order_copy.remove("reo")
            else :
                partdic3.remove("lec")
                partdic3.remove("rec")
                draw_order_copy.remove("lec")
                draw_order_copy.remove("rec")

        for p in partdic3 :
            part, upart = self.partdic2[p][0], self.partdic2[p][2]
            x, y = part["start_point_x"], part["start_point_y"]
            pi1, pi2, ux, uy = upart["theta"], part["pi2"], upart["position_x"] + upart["r"]/2, upart["position_y"] + upart["r"]/2
            x0, y0 = ux + x, uy + y
            x1, y1 = ux + cos(pi1)*x + sin(pi1)*y, uy - sin(pi1)*x + cos(pi1)*y
            part["position_cx"], part["position_cy"] = x0 + part["left_center_x"]*left + part["right_center_x"]*right, y0 + part["left_center_y"]*left + part["right_center_y"]*right
            x2, y2 = part["position_cx"] - ux, part["position_cy"] - uy
            part["position_cx"], part["position_cy"] = ux + cos(pi1)*x2 + sin(pi1)*y2, uy - sin(pi1)*x2 + cos(pi1)*y2
            x3, y3 = part["position_cx"] - x1, part["position_cy"] - y1
            part["position_cx"], part["position_cy"] = x1 + cos(pi2)*x3 + sin(pi2)*y3, y1 - sin(pi2)*x3 + cos(pi2)*y3
            part["position_x"], part["position_y"] = part["position_cx"] - part["r"]/2 , part["position_cy"] - part["r"]/2
            part["theta"] = upart["theta"] + part["pi2"]
            if left : part["rotate"] = part["leftimages"][round(part["theta"]*180/pi/angle_split)%int(360/angle_split)]
            if right : part["rotate"] = part["rightimages"][round(part["theta"]*180/pi/angle_split)%int(360/angle_split)]
            noe = len(part["end_value_tuple_list"])
            for i in range(noe) :
                part["end_point{}x".format(i+1)] = part["left_end_point{}x".format(i+1)] * left + part["right_end_point{}x".format(i+1)] * right
                part["end_point{}y".format(i+1)] = part["left_end_point{}y".format(i+1)] * left + part["right_end_point{}y".format(i+1)] * right

            cx, cy = part["position_cx"], part["position_cy"]
            ct, st = cos(-part["theta"]), sin(-part["theta"])
            for i in range(noe):
                part["end_point{}rx".format(i+1)] = ct * part["end_point{}x".format(i+1)] - st * part["end_point{}y".format(i+1)]
                part["end_point{}rx".format(i+1)] = st * part["end_point{}x".format(i+1)] + ct * part["end_point{}y".format(i+1)]

        for p in draw_order_copy :
            part = self.partdic2[p][0]
            screen.blit(part["rotate"], (part["position_x"], part["position_y"]))

        for p in self.partdic:
            part = self.partdic2[p][0]
            part["theta2"] = part["pi2"]
            if p == "downbody" :
                jessi.downbody["bposition_spy"] = jessi.downbody["start_point_y"]
            if left: part["lr"] = 'left'
            elif right: part["lr"] = 'right'

        if t - self.land_time >= 7 and (act == "soft land") :
            act = "stand"
        if t - self.land_time >= 15 and (act == "land") :
            act = "stand"
        if t - self.land_time >= 90 and (act == "hard land") :
            act = "stand"
        self.JessiAct()
    def JessiAct(self):
        if pygame.key.get_pressed()[pygame.K_LSHIFT] :
            if pygame.key.get_pressed()[pygame.K_LEFT] :
                jessi.act = "walk"
                if self.body.velocity.x >= - self.walk_speed :
                    self.body.velocity += (-jessi.move_scale, 0)
            elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                jessi.act = "walk"
                if self.body.velocity.x <= jessi.walk_speed :
                    self.body.velocity += (jessi.move_scale, 0)
        elif pygame.key.get_pressed()[pygame.K_DOWN]:
            jessi.act = "sit"
            jessi.sit_time += 1
            if pygame.key.get_pressed()[pygame.K_LEFT] :
                jessi.act = "sit walk"
                if self.body.velocity.x >= -jessi.sit_speed :
                    self.body.velocity += (-jessi.move_scale, 0)
            elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                jessi.act = "sit walk"
                if self.body.velocity.x <= jessi.sit_speed :
                    self.body.velocity += (jessi.move_scale, 0)
        else :
            jessi.act = "stand"
            if pygame.key.get_pressed()[pygame.K_LEFT] :
                jessi.act = "run"
                if self.body.velocity.x >= -jessi.run_speed :
                    self.body.velocity += (-jessi.move_scale, 0)
            elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                jessi.act = "run"
                if self.body.velocity.x <= jessi.run_speed :
                    self.body.velocity += (jessi.move_scale, 0)
    def BarGraphic(self):
        bar_width = self.width
        bar_height = self.width * 0.15
        gap = 1
        dist = 20
        HP_rect = pygame.Rect(0, 0, bar_width, bar_height)
        HP_rect.center = Vec2d(self.body.rposition[0], self.body.rposition[1]) - (0, self.height/2 + dist + gap * 2 + bar_height * 3/2)
        HP_rest_rect = pygame.Rect(0, 0, self.HP / self.MAX_HP * bar_width, bar_height)
        HP_rest_rect.topleft = HP_rect.topleft
        HP_bright_rect = pygame.Rect(0, 0, self.HP / self.MAX_HP * bar_width, bar_height/2)
        HP_bright_rect.topleft = HP_rect.topleft

        pygame.draw.rect(screen, color="red", rect = HP_rest_rect, width=0)
        pygame.draw.rect(screen, color="pink", rect = HP_bright_rect, width=0)
        pygame.draw.rect(screen, color="black", rect = HP_rect, width=4)
        pygame.draw.rect(screen, color="white", rect = HP_rect, width=1)

        STAMINA_rect = pygame.Rect(0, 0, bar_width, bar_height)
        STAMINA_rect.center = Vec2d(self.body.rposition[0], self.body.rposition[1]) - (0, self.height/2 + dist + gap + bar_height * 1/2)
        STAMINA_rest_rect = pygame.Rect(0, 0, self.STAMINA / self.MAX_STAMINA * bar_width, bar_height)
        STAMINA_rest_rect.topleft = STAMINA_rect.topleft
        STAMINA_bright_rect = pygame.Rect(0, 0, self.STAMINA / self.MAX_STAMINA * bar_width, bar_height/2)
        STAMINA_bright_rect.topleft = STAMINA_rect.topleft

        pygame.draw.rect(screen, color="blue", rect = STAMINA_rest_rect, width=0)
        pygame.draw.rect(screen, color="lightblue", rect = STAMINA_bright_rect, width=0)
        pygame.draw.rect(screen, color="black", rect = STAMINA_rect, width=4)
        pygame.draw.rect(screen, color="white", rect = STAMINA_rect, width=1)

    def HP_STAMINA_LIMITATION(self):
        if self.HP > self.MAX_HP: self.HP = self.MAX_HP
        if self.STAMINA > self.MAX_STAMINA: self.STAMINA = self.MAX_STAMINA
        if self.HP < 0: self.HP = 0
        if self.STAMINA < 0: self.STAMINA = 0

    def SpannerAttack(self):
        if self.STAMINA >= self.SpannerAttackStaminaConsumeAmount: SpannerAttack()
        self.STAMINA -= self.SpannerAttackStaminaConsumeAmount

    def update(self):
        self.BarGraphic()
        self.self_healing()
        self.HP_STAMINA_LIMITATION()
        for sa in SpannerAttacks:
            sa.update()
        for tur in turret:
            tur.draw(screen)
            tur.BarGraphic()
            if tur.HP <= 0: tur.get_destroyed()

    def self_healing(self):
        self.HP += self.self_hp_healing_amount * (self.HP > 0)
        self.STAMINA += self.self_stamina_healing_amount * (self.STAMINA > 0)

    def SummonTurret(self):
        for tur in turret: tur.get_destroyed()
        position = self.body.position + ((-1*left + 1*right)*screen_width/4, -screen_height/3)
        Turret(position)

    def BackStep(self):
        if abs(self.body.velocity.y) < up_down_minimun and abs(self.body.velocity.x) < self.max_speed:
            self.body.velocity = ((1*left + -1*right)* self.dash_speed/1.3, -self.jump_speed/2)

SpannerAttacks = []
class SpannerAttack:
    def __init__(self):
        self.exist_time = 10
        self.initial_time = t
        self.initial_position = jessi.body.position + (-50 * pygame.key.get_pressed()[pygame.K_LEFT] + 50 * pygame.key.get_pressed()[pygame.K_RIGHT], -30 * pygame.key.get_pressed()[pygame.K_UP] + 30 * pygame.key.get_pressed()[pygame.K_DOWN])
        self.initial_direction = -1 * left + 1 * right
        self.attack_act = 0 + -1 * pygame.key.get_pressed()[pygame.K_UP] + 1 * pygame.key.get_pressed()[pygame.K_DOWN]
        self.updown = 1 + -2 * pygame.key.get_pressed()[pygame.K_UP]
        self.start_angle = (left * (pi + pi/4) + right * (-pi/4)) * (self.attack_act == 0) + (left * (pi + pi/6)        + right * (-pi/6))        * (self.attack_act == -1) + (left * (pi - pi/6) + right * (pi/6)) * (self.attack_act == 1)
        self.end_angle =   (left * (pi - pi/4) + right * ( pi/4)) * (self.attack_act == 0) + (left * (pi + pi/2 + pi/6) + right * (-pi/2 - pi/6)) * (self.attack_act == -1) + (left * (pi/2 - pi/6) + right * (pi/2 + pi/6)) * (self.attack_act == 1)
        self.attack_range_angle = abs(self.end_angle - self.start_angle)
        self.between_angle = 0.1
        self.color = "grey"
        self.draw_speed = .5 / self.between_angle
        self.line_width = 20
        self.range_tail = 100 * self.between_angle
        self.start_length = 50 + random() * 10
        self.end_length = self.start_length + (self.attack_range_angle//self.between_angle) * self.range_tail
        self.contact = []

        SpannerAttacks.append(self)

    def drawlines(self):
        time = int((t - self.initial_time) * self.draw_speed)
        if time > self.attack_range_angle//self.between_angle:
            for i in range(int(self.attack_range_angle//self.between_angle)):
                start = self.initial_position + (Vec2d(1, 0) * self.start_length).rotated(self.start_angle + i * self.initial_direction * self.updown * self.between_angle)
                end = self.initial_position + (Vec2d(1, 0) * (self.start_length + i * self.range_tail)).rotated(self.start_angle + i * self.initial_direction * self.updown * self.between_angle)
                relative_start = start - map.position
                relative_end = end - map.position
                pygame.draw.line(screen, color=self.color, start_pos=relative_start, end_pos=relative_end, width=self.line_width)
        else:
            for i in range(time):
                start = self.initial_position + (Vec2d(1, 0) * self.start_length).rotated(self.start_angle + i * self.initial_direction * self.updown * self.between_angle)
                end = self.initial_position + (Vec2d(1, 0) * (self.start_length + i * self.range_tail)).rotated(self.start_angle + i * self.initial_direction * self.updown * self.between_angle)
                relative_start = start - map.position
                relative_end = end - map.position
                pygame.draw.line(screen, color=self.color, start_pos=relative_start, end_pos=relative_end, width=self.line_width)

    def predetect(self, enemy):
        if (enemy.body.position - self.initial_position).get_length_sqrd()**.5 < 300 + ((enemy.width/2)**2 + (enemy.height/2)**2)**.5 :
            return True

    def detect(self, enemy):
        time = int((t - self.initial_time) * self.draw_speed)
        self.collide = False
        if time > self.attack_range_angle//self.between_angle:
            for i in range(int(self.attack_range_angle//self.between_angle)):
                start = self.initial_position + (Vec2d(1, 0) * self.start_length).rotated(self.start_angle + i * self.initial_direction * self.updown * self.between_angle)
                end = self.initial_position + (Vec2d(1, 0) * (self.start_length + i * self.range_tail)).rotated(self.start_angle + i * self.initial_direction * self.updown * self.between_angle)
                for i in range(4):
                    x1, y1 = start
                    x2, y2 = end
                    x3, y3 = enemy.body.position + enemy.shape[0].get_vertices()[i-1]
                    x4, y4 = enemy.body.position + enemy.shape[0].get_vertices()[i]
                    condition1 = ((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1)) * ((x2-x1)*(y4-y1) - (x4-x1)*(y2-y1)) < 0
                    condition2 = ((x4-x3)*(y1-y3) - (x1-x3)*(y4-y3)) * ((x4-x3)*(y2-y3) - (x2-x3)*(y4-y3)) < 0
                    if condition1 and condition2: self.collide = True
        else:
            for i in range(time):
                start = self.initial_position + (Vec2d(1, 0) * self.start_length).rotated(self.start_angle + i * self.initial_direction * self.updown * self.between_angle)
                end = self.initial_position + (Vec2d(1, 0) * (self.start_length + i * self.range_tail)).rotated(self.start_angle + i * self.initial_direction * self.updown * self.between_angle)
                for i in range(4):
                    x1, y1 = start
                    x2, y2 = end
                    x3, y3 = enemy.body.position + enemy.shape[0].get_vertices()[i-1]
                    x4, y4 = enemy.body.position + enemy.shape[0].get_vertices()[i]
                    condition1 = ((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1)) * ((x2-x1)*(y4-y1) - (x4-x1)*(y2-y1)) < 0
                    condition2 = ((x4-x3)*(y1-y3) - (x1-x3)*(y4-y3)) * ((x4-x3)*(y2-y3) - (x2-x3)*(y4-y3)) < 0
                    if condition1 and condition2: self.collide = True

    def update(self):
        self.drawlines()
        self.disappear()
        for enemy in enemys:
            if self.predetect(enemy):
                self.detect(enemy)
                if self.collide:
                    if enemy not in self.contact:
                        enemy.body.velocity += -enemy.direction * 300
                        enemy.HP -= enemy.MAX_HP * 1.1
                        self.contact.append(enemy)

    def disappear(self):
        if t - self.initial_time > self.exist_time:
            SpannerAttacks.remove(self)

turret = []
class Turret(Character):
    def __init__(self, position):
        self.width = turret_width
        self.height = turret_height
        super().__init__(width=self.width, height=self.height, position=position)
        self.color = "red"
        self.shape.append(pymunk.Poly(body=self.body, vertices=[Vec2d(i * self.width, (j - 1/2) * self.height)/7 - Vec2d(0, self.height/2) for i, j in poly_list], radius=1))
        self.shape.append(pymunk.Poly(body=self.body, vertices=[Vec2d(i * self.width, (j - 1/2) * self.height)/1.3 - Vec2d(0, self.height/2 + self.height/7) for i, j in poly_list], radius=1))
        self.shape[2].surface_velocity = 1000, 0
        for i in range(1, len(self.shape)):
            space.add(self.shape[i])
        turret.append(self)


    def get_destroyed(self):
        space.remove(self.body)
        for shape in self.shape: space.remove(shape)
        characters.remove(self)
        turret.remove(self)
        a = 10
        x, y = self.body.position - (self.width/2 - a/2, self.height/2 - a/2)
        for i in range(self.width//a):
            for j in range(self.height//a):
                b = Box(size=(a, a), position=(x + i*a, y + j*a), color=self.color)
                b.body.velocity = self.body.velocity.rotated(random()-1/2) + (b.body.position - self.body.position).normalized() * particle_spread_speed
                b.generated_time = t
                b.exist_time = randint(30, 60)
                particles.append(b)

    def TurretSpeedLimit(self):
        self.body.velocity = (0, self.body.velocity.y)

class Enemy(Character):
    def __init__(self, width, height, position=(map.width/2, 0)):
        super().__init__(width=width, height=height, position=position)
        enemys.append(self)

        self.move_scale = 30
        self.reaction_speed = 10  ## frame speed
        self.MAX_HP = self.width * self.height / 100
        self.HP = self.MAX_HP
        self.MAX_STAMINA = 100
        self.STAMINA = self.MAX_STAMINA
        self.stamina_consume_rate = 1/2000
        self.self_hp_healing_amount = self.MAX_HP * 1/6000
        self.self_stamina_healing_amount = self.MAX_STAMINA * 1/2000
        self.direction = (jessi.body.position - self.body.position).normalized()
        self.jump_time = randint(120, 180)
        self.dash_time = randint(300, 400)
        self.jump_speed *= 0.5
        self.dash_speed *= 0.5
        self.search_distance = screen_width/2
        self.distance = 0
        self.direction_x = 0
        self.direction_y = 0
        self.exploring_time = 0
        self.exploring_time_term = self.generate_time_term()
        self.exploring_direction_x = choice((-1, 0 ,1))
        self.run_speed *= (random() + 0.5)

    def AI(self):
        self.hunt()
        self.update()
        self.self_healing()
        if self.HP > 0: self.BarGraphic()
        else: self.get_destroyed(particle_size)

    def update(self):
        self.direction = (jessi.body.position - self.body.position).normalized()
        self.direction_x = ((self.direction.x > 0) - 1/2) * 2
        self.distance = (self.body.position - jessi.body.position).length
        self.STAMINA -= abs(self.body.velocity.x) * self.stamina_consume_rate
        if self.STAMINA <= 0: self.STAMINA = 0
        if self.STAMINA > self.MAX_STAMINA: self.STAMINA = self.MAX_STAMINA
        if self.HP > self.MAX_HP: self.HP = self.MAX_HP

    def self_healing(self):
        self.HP += self.self_hp_healing_amount
        self.STAMINA += self.self_stamina_healing_amount

    def BarGraphic(self):
        gap = 1
        bar_width = self.width
        bar_height = bar_width * .15 * (bar_width >= 80) + 10 * (bar_width < 80)
        bright_bar_height = bar_height * 0.5
        hp_bar_rect = pygame.Rect(0, 0, bar_width, bar_height)
        hp_rest_bar_rect = pygame.Rect(0, 0, self.HP / self.MAX_HP * bar_width, bar_height)
        hp_bright_bar_rect = pygame.Rect(0, 0, self.HP / self.MAX_HP * bar_width, bright_bar_height)
        hp_bar_rect.center = self.body.rposition - (0, self.height/2 + bar_height + gap * 2 + bar_height/2)
        hp_rest_bar_rect.topleft = hp_bar_rect.topleft
        hp_bright_bar_rect.topleft = hp_bar_rect.topleft
        stamina_bar_rect = pygame.Rect(0, 0, bar_width, bar_height)
        stamina_bar_rect.center = self.body.rposition - (0, self.height/2 + gap + bar_height/2)
        stamina_rest_bar_rect = pygame.Rect(0, 0, self.STAMINA / self.MAX_STAMINA * bar_width, bar_height)
        stamina_rest_bar_rect.topleft = stamina_bar_rect.topleft
        stamina_bright_bar_rect = pygame.Rect(0, 0, self.STAMINA / self.MAX_STAMINA * bar_width, bright_bar_height)
        stamina_bright_bar_rect.topleft = stamina_bar_rect.topleft

        pygame.draw.rect(screen, color="red", rect=hp_rest_bar_rect, width=0)
        pygame.draw.rect(screen, color="#F08080", rect=hp_bright_bar_rect, width=0)
        pygame.draw.rect(screen, color="black", rect=hp_bar_rect, width=4)
        pygame.draw.rect(screen, color="lightgrey", rect=hp_bar_rect, width=1)

        pygame.draw.rect(screen, color="blue", rect=stamina_rest_bar_rect, width=0)
        pygame.draw.rect(screen, color="#97b0d1", rect=stamina_bright_bar_rect, width=0)
        pygame.draw.rect(screen, color="black", rect=stamina_bar_rect, width=4)
        pygame.draw.rect(screen, color="lightgrey", rect=stamina_bar_rect, width=1)

    def collide(self, c):
        relative_velocity = (self.body.velocity - c.body.velocity).length
        if abs(self.body.position.x - c.body.position.x) <= self.width/2 + c.width/2:
            if abs(self.body.position.y - c.body.position.y) <= self.height/2 + c.height/2:
                c.body.velocity += self.direction * 200
                c.HP -= relative_velocity * self.body.mass * RelativevelcityToDamageAdjustConstant
                self.HP -= relative_velocity * c.body.mass * RelativevelcityToDamageAdjustConstant
                self.body.velocity += -self.direction * 200

    def hunt(self):
        self.normal_hunt()

    def normal_hunt(self):
        self.body.velocity += (self.direction_x * self.move_scale * (-self.run_speed < self.body.velocity.x < self.run_speed), 0)
        if t % self.jump_time == 0: self.jump()
        if t % self.dash_time == 0: self.dash()

    def warn_hunt(self):
        if t - self.exploring_time > self.exploring_time_term:
            self.exploring_time = t
            self.exploring_time_term = self.generate_time_term()
            self.exploring_direction_x = choice((-1, -1, 0, 1, 1))
        else:
            self.body.velocity += (self.exploring_direction_x * self.move_scale * (-self.run_speed < self.body.velocity.x < self.run_speed), 0)

    def get_destroyed(self, particle_size=3):
        enemys.remove(self)
        characters.remove(self)
        space.remove(self.body)
        for shape in self.shape: space.remove(shape)
        a = particle_size
        x, y = self.body.position - (self.width/2 - a/2, self.height/2 - a/2)
        for i in range(self.width//a):
            for j in range(self.height//a):
                b = Box(size=(a, a), position=(x + i*a, y + j*a), color=particle_color)
                b.width, b.height = a, a
                b.body.velocity = self.body.velocity.rotated(random()-.5)
                b.generated_time = t
                b.exist_time = randint(20, 50)
                particles.append(b)

    def generate_time_term(self):
        return randint(1, 7) * 10

def CleanParticles():
    for particle in particles:
        if particle.exist_time / 2 < t - particle.generated_time :
            particle.size = particle.width * ((t - particle.generated_time)/(particle.exist_time / 2))**-4, particle.height * ((t - particle.generated_time)/(particle.exist_time / 2))**-4
            particle.vertices = [Vec2d(-particle.size[0]/2, -particle.size[1]/2), Vec2d(particle.size[0]/2, -particle.size[1]/2), Vec2d(particle.size[0]/2, particle.size[1]/2), Vec2d(-particle.size[0]/2, particle.size[1]/2)]

        if t - particle.generated_time > particle.exist_time:
            particles.remove(particle)
            boxes.remove(particle)
            space.remove(particle.body, particle.shape)

def EnemyRefill():
    if len(enemys) < number_of_enemys:
        Enemy(width=enemy_width, height=enemy_height, position=(map.width/2 - randint(200, 600), randint(-100, 100)))


## 상수
up_down_minimun = 50
angle_split = 1
jessi = Character(width=70, height=170)
jessi.JessiPartMake()
particle_size = 10
enemy_size = 30
particle_spread_speed = 500
particle_color = "black"
particle_inside_color = "white"
box_width = 2
character_box_width = 3
number_of_enemys = 1
enemy_width, enemy_height = 50, 100
poly_list = [(-1/2, -1/2), (1/2, -1/2), (1/2, 1/2), (-1/2, 1/2)]
RelativevelcityToDamageAdjustConstant = 1/10000

turret_width, turret_height = 80, 50


for i in range(number_of_enemys):
    Enemy(width=enemy_width, height=enemy_height, position=(map.width/2 - randint(200, 600), randint(-100, 100)))

map_ratio = 1/20
t, dt = 0, 1/60
left, right = 1, 0

running = True
while running:
    clock.tick(1/dt)
    t += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_x:
                jessi.SpannerAttack()
            if event.key == pygame.K_s:
                jessi.SummonTurret()
            if event.key == pygame.K_c:
                jessi.jump()
            if event.key == pygame.K_f:
                for tur in turret: tur.get_destroyed()
            if event.key == pygame.K_SPACE:
                jessi.dash()
            if event.key == pygame.K_a:
                jessi.BackStep()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                jessi.sit_time = 0

    if pygame.key.get_pressed()[pygame.K_LEFT]: left, right = 1, 0
    if pygame.key.get_pressed()[pygame.K_RIGHT]: left, right = 0, 1

    screen.fill("white") ## 새하얀 도화지 깔기
    map.move(jessi, ratio=map_ratio) ## 맵뷰는 "제시" 포커스로 움직일 것.
    jessi.JessiPartMove(t, jessi.act) ## 제시의 파츠들 애니메이션
    jessi.update()
    # jessi.draw(screen)

    for w in statics: w.draw(map, screen)

    for b in boxes: b.draw(map, screen)

    for c in characters:
        map.relative_location(c)
        # c.speed_limit(c.max_speed)
        c.rotate_limit()

    for e in enemys:
        if e.HP > 0: e.draw(screen)
        e.AI()
        e.collide(jessi)
        for tur in turret: e.collide(tur)
    for tur in turret:
        tur.TurretSpeedLimit()

    EnemyRefill()
    CleanParticles()

    space.step(dt)
    pygame.display.update()
    pygame.display.set_caption("fps: " + str(clock.get_fps()))


pygame.quit()