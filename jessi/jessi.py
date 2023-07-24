import pygame
import random
import cv2
from math import *
# from numpy import *
import time
from screeninfo import get_monitors

pygame.init()
pygame.display.set_caption("Fucking Jessi")


if pygame.display.get_num_displays() >= 2 :
    screen_number = 1
    screen_crop = 55
else :
    screen_number = 0
    screen_crop = 145
    if get_monitors()[screen_number].height >= 1000:
        screen_crop = 170

x, y = 2012,2104 # 고화질 pixels
283, 296 # 저화질(원본) pixels
# x_ratio, y_ratio = 2012/283, 2104/296
x_ratio, y_ratio = 1, 1
sc = 1
x_ratio, y_ratio = x_ratio*sc , y_ratio*sc


if screen_number >= 1 :
    screen_width, screen_height = get_monitors()[screen_number-1].width, get_monitors()[screen_number-1].height - screen_crop
    screen2 = pygame.display.set_mode((screen_width, screen_height), display=screen_number-1)
screen_width, screen_height = get_monitors()[screen_number].width, get_monitors()[screen_number].height - screen_crop
screen = pygame.display.set_mode((screen_width, screen_height), display=screen_number)
game_font = pygame.font.Font(None, 30)

# 전체화면, 확대해서 보기
sc = 1
screen_width, screen_height = int(pygame.display.get_desktop_sizes()[0][0]/sc), int(pygame.display.get_desktop_sizes()[0][1]/sc)
screen = pygame.display.set_mode((screen_width, screen_height), flags=pygame.FULLSCREEN)
# if pygame.display.get_num_displays()>=2:
#     screen = pygame.display.set_mode((screen_width, screen_height), flags=pygame.SCALED | pygame.FULLSCREEN, display=1)

class expand :
    pass
class position :
    def __init__(self) :
        self.x = screen_width/2
        self.y = screen_height/2
        self.rx = 0
        self.ry = 0
        self.cx = 0
        self.cy = 0
acts = ["stand", "walk", "run", "jump ready", "up", "down", "land", "soft land", "sit", "sit walk", "dash",\
        "eball ready", "eball ready walk", "eball ready sit walk"]
class size :
    def __init__(self):
        self.width = 0
        self.height = 0

class parts :
    def __init__(self):
        self.position = position()
        self.theta = 0
        self.theta2 = 0
        self.lr = "left"
        self.bposition = expand()
        self.lines = False
        self.end_point_sign = False
        self.pi2 = 0
        self.start_x = 0
        self.start_y = 0
        self.left_center_x = 0
        self.left_center_y = 0
        self.right_center_x = 0
        self.right_center_y = 0
        self.number_of_end = 0
        self.end_value_tuple_list = []

    def image(self, name, subsf):
        self.image = cv2.imread("parts/"+name+".png", -1)
        self.image = cv2.resize(self.image, (0,0), fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
        self.image = pygame.image.frombuffer(self.image.tobytes(), self.image.shape[1::-1], "BGRA")
        self.image = self.image.subsurface(subsf)
        self.size = size()
        self.size.width, self.size.height = self.image.get_rect().size
        self.r = self.size.width
        self.leftimage = self.image
        self.rightimage = pygame.transform.flip(self.image, True ,False)
        self.leftimages = [self.leftimage]
        self.rightimages = [self.rightimage]
        exec("""if self == jessi.part.%s :
            if name == "lleftfootc" :
                self.leftimages[0] = self.rightimage
                self.rightimages[0] = self.leftimage
            for i in range(1, 360) :
                self.leftimages.append(pygame.transform.rotate(self.leftimage, i))
                if name == "lleftfootc" :
                    self.leftimages[-1] = pygame.transform.rotate(self.rightimage, i)
                r, rr = self.leftimages[0].get_rect().size[0], self.leftimages[i].get_rect().size[0]
                self.leftimages[i] = self.leftimages[i].subsurface((rr - r) / 2, (rr - r) / 2, r, r)

                self.rightimages.append(pygame.transform.rotate(self.rightimage, i))
                if name == "lleftthighc" or name == "lrightthighc" or name == "lleftfootc":
                    self.rightimages[-1] = pygame.transform.rotate(self.leftimage, i)
                r, rr = self.rightimages[0].get_rect().size[0], self.rightimages[i].get_rect().size[0]
                self.rightimages[i] = self.rightimages[i].subsurface((rr - r) / 2, (rr - r) / 2, r, r)""" % name)


class eball :
    def __init__(self):
        self.initialsize = .4
        self.maxsize = 1.2
        self.image = [pygame.image.load("eball1.png"), pygame.image.load("eball2.png")]
        self.initialimage = self.image.copy()
        self.charge = False
        self.chargespeed = .01
        self.chargedistance = 120
        self.duration = expand()
        self.duration.entiretime = 300
        self.duration.shrinktime = 180
        self.duration.shrinkspeed = 0.07
        self.lastdisappear = 0
        self.generated = []
        self.speed = 2
        self.width = 100
        self.widthgap = 10
        self.fire = False
        self.cooldown = False
        self.cooltime = 60

class weapon :
    def __init__(self):
        self.eball = eball()


class object :
    def __init__(self):
        self.part = expand()
        self.position = position()
        self.size = size()
        self.hitbox = pygame.Rect(0,0,0,0)
        self.weight = 0
        self.xvelocity = 0
        self.yvelocity = 0
        self.tvelocity = 0
        self.theta = 0
        self.power_jump_amount = 1.2
        self.power_dash_amount = 1.2
        self.dash_jump_ratio = 0.6
        self.land = False
        self.jump = False
        self.move_scale = 1.5
        self.sit_speed = .5
        self.walk_speed = 1
        self.ew_speed = .11
        self.run_speed = 3
        self.dash_act_amount = 5
        self.dash_speed = 10
        self.jump_speed = 17
        self.dash_act_amount = 10
        self.dash_ct = 30
        self.jump_ct = 30
        self.jump_amount = .2
        self.dash_amount = .4
        self.drop_max_speed = 30
        self.land_min_speed = 17
        self.softland_min_speed = 7
        self.hardland_min_speed = 25
        self.summon = False
        self.weapon = weapon()
        self.act = "stand"
        self.left = True
        self.jump_time = 0
        self.land_time = 0
        self.dash_time = 0
        self.sit_time = 0
        self.free_time = 0
        self.free = True
        self.max_hp = 100
        self.hp = self.max_hp
        self.inland = 0



class map :
    def __init__(self):
        self.size = size()
        self.speed = 1/10
        self.position = position()

class rect :
    def __init__(self):
        self.force = expand()
        self.force.x = 0
        self.force.y = 0
        self.velocity = expand()
        self.velocity.x = 0
        self.velocity.y = 0
        self.velocity.t = 0
        self.position = expand()
        self.position.x = 0
        self.position.y = 0
        self.torque = 0
        self.theta = 0




if "func" == "func" :
    def vector_distance(u,v) :
        return len_vector(tuple_add(u, v, "-"))
    def tuple_add(a, b, operation="+"):
        if operation == "+":
            o = 1
        elif operation == "-":
            o = -1
        else:
            print("연산자 오류, + - 중 입력하시오")
        list_c = [0] * len(a)
        for i in range(len(a)):
            list_c[i] = list(a)[i] + o * list(b)[i]
        return tuple(list_c)
    def len_vector(v):
        len_v = 0
        for i in range(len(v)):
            len_v += v[i] ** 2
        return len_v ** .5
    def unit_vector(v):
        unit_v = [0] * len(v)
        for i in range(len(v)):
            unit_v[i] = v[i] / len_vector(v)
        return tuple(unit_v)
    def tuple_multiply(a, c):
        list_a = list(a)
        for i in range(len(a)) :
            list_a[i] = a[i]*c
        return tuple(list_a)
    def inner_product(a, b):
        product = 0
        for i in range(len(a)):
            product += a[i] * b[i]
        return product
    def inside(c,x_pos, width, land_x_pos, land_width) :
        if land_x_pos <= x_pos <= land_x_pos + land_width or land_x_pos <= x_pos+width <= land_x_pos + land_width :
            return True
        else : return False
    def landing(c, x, y, w, h, lx, ly, lw) :
        if (y <= ly - h) and (y+c.yvelocity *dt*scale > ly - h) \
                  and inside(c, x, w, lx,lw) :
            return True
        else : return False
    def aatan(x0, y0):
        if x0 < 0:
            return atan(y0 / x0) + pi
        elif x0 == 0 and y > 0:
            return pi / 2
        elif x0 == 0 and y < 0:
            return pi * 3 / 2
        else:
            return atan(y0 / x0)

    def head_fun(b) :
        b = b %  360
        if 0 <= b < 40: a = 32
        if 40 <= b < 50: a = 32 + (b - 40) / 2
        if 50 <= b < 90: a = 37
        if 90 <= b < 137: a = 37 + (b - 90) / (47 / 9)
        if 137 <= b < 145: a = 46
        if 145 <= b < 180: a = 46 - 9 * log(b - 144) / log(36)
        if 180 <= b < 240: a = 37
        if 240 <= b < 270: a = 37 - (b - 240) / 10
        if 270 <= b < 330: a = 34
        if 330 <= b < 360: a = 34 - (b - 330) / 15
        return a
    def upbody_fun(b) :
        b = b % 360
        if 0 <= b < 50 : a = 14 + b*(b-30)/1000*6
        if 50 <= b < 90 : a = 20
        if 90 <= b < 110 : a = 20
        if 110 <= b < 135 : a = 20 - log(b-109)/log(26)*4
        if 135 <= b < 180 : a = 20 - (b-90)/90*8
        if 180 <= b < 270 : a = 12 + (b-180)/30
        if 270 <= b < 360 : a = 20 - 4*abs(b-315)/45
        return a
    def lleftuparm_fun(b) :
        b = b % 360
        if 0 <= b < 65 : a = 6 + b*(b-15)/2600*10
        elif 65 <= b < 90 : a = 16 - (b-65)*(b-75)/375*9
        elif 90 <= b < 180 : a = 7 + (b-90)*(b-220)/3600*4
        elif 180 <= b < 255 : a = 3 + (b-180)*(b-210)/3375*11
        elif 255 <= b < 270 : a = 14 - (b-255)/15*2
        elif 270 <= b < 360 : a = 12 + (b-270)*(b-410)/4500*6
        return a
    def lleftdownarm_fun(b) :
        b = b % 360
        if 0 <= b < 60 : a = 5 + b/60*7
        if 60 <= b < 90 : a = 12 - (b-60)/30*7
        elif 90 <= b < 180 : a = 5
        elif 180 <= b < 240 : a = 5 + (b-180)/60*5
        elif 240 <= b < 270 : a = 10 - (b-240)/30*5
        elif 270 <= b < 360 : a = 5
        return a
    def lrightuparm_fun(b) :
        b = b % 360
        if 0 <= b < 90 : a = 4 + b*(b-20)/6300*8
        elif 90 <= b < 105 : a = 12 + (b-90)/15*3
        elif 105 <= b < 180 : a = 15 + (b-105)*(b-240)/4500*11
        elif 180 <= b < 270 : a = 4 + (b-180)*(b-210)/5400*6
        elif 270 <= b < 295 : a = 10 - (b-270)*(b-310)/375*4
        elif 295 <= b < 360 : a = 14 + (b-295)*(b-425)/4225*10
        return a
    def lrightdownarm_fun(b) :
        b = b % 360
        if 0 <= b < 90 : a = 2 + b*(b-60)/2700*12
        elif 90 <= b < 180 : a = 14 - (b-90)/90*10
        elif 180 <= b < 270 : a = 4 + (b-180)/90*2
        elif 270 <= b < 360 : a = 6 - (b-270)/90*4
        return a
    def llefthand_fun(b) :
        b = b % 360
        if 0 <= b < 90 : a = 6
        elif 90 <= b < 180 : a = 8
        elif 180 <= b < 270 : a = 8
        elif 270 <= b < 360 : a = 8 - (b-270)/90*2
        return a
    def lrighthand_fun(b) :
        b = b % 360
        if 0 <= b < 90 : a = 5 + b/90*3
        elif 90 <= b < 180 : a = 8 - (b-90)/90*3
        elif 180 <= b < 270 : a = 5 + (b-180)/90*3
        elif 270 <= b < 360 : a = 8 - (b-270)/90*3
        return a
    def lleftthighc_fun(b) :
        b = b % 360
        if right : b = (180 - b)%360
        if 0 <= b < 90 : a = 9 + b/90*5
        elif 90 <= b < 180 : a = 14 - (b-90)/90*7
        elif 180 <= b < 270 : a = 7 +(b-180)/90*8
        elif 270 <= b < 360 : a = 15 - (b-270)/90*6
        return a
    def lleftlegc_fun(b) :
        b = b % 360
        if 0 <= b < 30 : a = 12 + b/30*2
        if 30 <= b < 90 : a = 14 - (b-30)/60*2
        elif 90 <= b < 135 : a = 12 + (b-90)/45*3
        elif 135 <= b < 180 : a = 15 - (b-135)/45*5
        elif 180 <= b < 270 : a = 10 + (b-180)/90*5
        elif 270 <= b < 360 : a = 15 + (b-270)*(b-390)/2700*3
        return a
    def lleftfootc_fun(b) :
        b = b % 360
        if 0 <= b < 60 : a = 5 + b/60*4
        if 60 <= b < 90 : a = 9 - (b-60)/30*2
        elif 90 <= b < 135 : a = 7 + (b-90)/45*5
        elif 135 <= b < 180 : a = 12 - (b-135)/45*7
        elif 180 <= b < 270 : a = 5 + (b-180)*(b-225)/4050*4
        elif 270 <= b < 290 : a = 9 + (b-270)*(b-280)/200*2
        elif 290 <= b < 360 : a = 11 - (b-290)/70*6
        return a
    def lrightthighc_fun(b) :
        b = b % 360
        if right : b = (180 - b)%360
        if 0 <= b < 90 : a = 8 + b/90*5
        elif 90 <= b < 180 : a = 13 - (b-90)/90*7
        elif 180 <= b < 270 : a = 6 + (b-180)*(b-210)/5400*7
        elif 270 <= b < 300 : a = 13 + (b-270)/30*3
        elif 300 <= b < 360 : a = 16 + (b-300)*(b-420)/3600*8
        return a
    def lrightlegc_fun(b) :
        b = b % 360
        if 0 <= b < 90 : a = 10 - b/90*2
        elif 90 <= b < 160 : a = 8 + (b-90)/70*7
        elif 160 <= b < 180 : a = 15
        elif 180 <= b < 280 : a = 15 + (b-180)*(b-210)/7000*3
        elif 280 <= b < 360 : a = 18 + (b-280)*(b-420)/4800*8
        return a
    def lrightfootc_fun(b) :
        b = b % 360
        if 0 <= b < 45 : a = 6 + b/45*2
        if 45 <= b < 90 : a = 8 - (b-45)/45*3
        elif 90 <= b < 150 : a = 5 + (b-90)/90*5
        elif 150 <= b < 180 : a = 10 - (b-150)/30*5
        elif 180 <= b < 270 : a = 5 + (b-180)*(b-210)/5400*2
        elif 270 <= b < 300 : a = 7 + (b-270)/30*3
        elif 300 <= b < 360 : a = 10 - (b-300)/60*4
        return a
    def rot(p, th) :
        x, y = p
        xx, yy = cos(th)*x - sin(th)*y, sin(th)*x + cos(th)*y
        return (xx,yy)

facedic = ["leo", "lec", "reo", "rec", "leb", "reb", "nose", "mouth"]
hairdic = []
for i in range(9) :
    hairdic.append("hair" + "{}".format(i+1))
partdic = {"downbody": (126, 223,30, 30), "downbodyc": (121, 218,40, 40), "upbody":(118,196,42,42), "upbodyc":(118,196,42,42),"leftbagnod":(118,196,42,42),"rightbagnod":(118,196,42,42), "bag":(110,190,82,82), \
           "neck":(136,191,13,13), "head":(93,108,99,99), "hatdownb":(58,30,179,179),"hatdownf":(58,30,179,179),"hatup":(58,30,179,179),"hatglass":(58,30,179,179)}
for p in facedic : partdic[p] = partdic["head"]
for p in hairdic : partdic[p] = (38, 53, 209, 209)
partdic_rest = {"lleftthigh": (132 ,232 ,32,32), "lleftthighc": (132 ,232 ,32,32), "lleftleg": (135 ,256 ,28,28), "lleftlegc": (130 ,251 ,38,38),\
                 "lleftfoot": (146 ,280 ,15,15), "lleftfootc": (145 ,279 ,17,17), "lrightthigh":(116 ,234 ,30,30), "lrightthighc":(116 ,234 ,30,30), \
                "lrightleg": (118 ,257 ,28,28), "lrightlegc": (113 ,252 ,38,38),"lrightfoot": (117 ,281 ,15,15), "lrightfootc": (117 ,281 ,15,15), \
                "lleftuparm": (135 ,198 ,42,42),"lleftuparmc": (135 ,198 ,42,42), "lleftdownarm": (135 ,203 ,42,42), "llefthand": (132 ,200 ,35,35),\
                "lrightuparm": (105 ,198 ,42,42), "lrightuparmc": (105 ,198 ,42,42), "lrightdownarm": (105 ,198 ,42,42), "lrighthand": (112, 200, 35, 35)}
partdic.update(partdic_rest)
for part in partdic.keys() :
    partdic[part] = partdic[part][0]*x_ratio, partdic[part][1]*x_ratio, partdic[part][2]*x_ratio, partdic[part][3]*x_ratio


# 앞에 있을수록 앞으로 나오는 순서. 나중에 뒤집을 거임.
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
draw_order_right = draw_order



jessi = object()
jessi.weight = 40

for n, s  in partdic.items() :
    exec("jessi.part.%s = parts()" % (n))
    exec("jessi.part.%s.image(n, s)" % (n))



turret = object()
turret.position.x, turret.position.y = -500, -500
turret.image = expand()
turret.image.transparent = expand()
turret.image.original = pygame.image.load("cannon.png")
turret.image.cropped = turret.image.transparent.original = turret.image.original.subsurface((0,0,turret.image.original.get_rect().size[0], turret.image.original.get_rect().size[1]-1.5))
turret.image.transparent.left = pygame.transform.flip(turret.image.transparent.original, True, False)
turret.image.transparent.right = turret.image.transparent.original.copy()
turret.image.left = pygame.transform.flip(turret.image.cropped, True, False)
turret.image.right = turret.image.cropped
turret.image.select = turret.image.right
turret.distance = 100
turret.size = size()
turret.size.width, turret.size.height = turret.image.cropped.get_rect().size
turret.position = position()
turret.height = screen_height/2
turret.weight = 80
turret.summon = False
turret.land = False
turret.jump = False

jessi.part.downbody.end_value_tuple_list = [(10, 1, 10, 1), (-10, 3, -10, 3), (1, -5, -1, -5), (0,0,0,0)]
jessi.part.upbody.end_value_tuple_list = [(18, -6, 11, -10), (-13, -6, -18, -6), (4, -13, -4, -13), (0,0,0,0), (0,0,0,0),(0,0,0,0),(0,-12,0,-12)]
jessi.part.neck.end_value_tuple_list = [(0, -2, 0, -2)]
for i in range(len(facedic)) :
    jessi.part.neck.end_value_tuple_list.append((0, -2, 0, -2))
jessi.part.head.end_value_tuple_list = []
hev = [(8, -35, 0, -35),(8, -35, 0, -35),(8, -38, 0, -38),(8, -38, 0, -38),(8, -38, 0, -38),  (20,15,30,15),(-30,15,-20,15)]
for i in range(7) :
    jessi.part.head.end_value_tuple_list.append(hev[i])
jessi.part.hair3.end_value_tuple_list = [(-43,46,40,46)]
jessi.part.hair4.end_value_tuple_list = [(40,48,-35,48)]

jessi.part.head.end_value_tuple_list.extend([(0, -35, 2, -35),(0, -35, 2, -35),(0, -35, 2, -35)])
jessi.part.hatdownf.end_value_tuple_list = [(0,0,0,0)]
jessi.part.hatdownb.end_value_tuple_list = []
jessi.part.hatglass.end_value_tuple_list = []
jessi.part.hatup.end_value_tuple_list = []

jessi.part.lleftuparm.end_value_tuple_list = [(5, 11, -6, 11), (0,0,0,0)]
jessi.part.lleftdownarm.end_value_tuple_list = [(-5, -7, 6, -7)]
jessi.part.llefthand.end_value_tuple_list = []
jessi.part.lrightuparm.end_value_tuple_list = [(-2, 11, 2, 11), (0,0,0,0)]
jessi.part.lrightdownarm.end_value_tuple_list = [(0, -4, 0, -4)]
jessi.part.lrighthand.end_value_tuple_list = []
jessi.part.lleftthigh.end_value_tuple_list = [(1, 11, 1, 11), (0,0,0,0)]
jessi.part.lleftleg.end_value_tuple_list = [(2, 9, -1, 9), (0,0,0,0)]
jessi.part.lleftfoot.end_value_tuple_list = [(0,0,0,0)]
jessi.part.lrightthigh.end_value_tuple_list = [(0, 10, 0, 10), (0,0,0,0)]
jessi.part.lrightleg.end_value_tuple_list = [(-4, 9, 4, 9), (0,0,0,0)]
jessi.part.lrightfoot.end_value_tuple_list = [(0,0,0,0)]


class mouse :
    def __init__(self):
        self.click = expand()
        self.click.btn1 = expand()
        self.click.btn1.on = False
        self.click.btn1.off = False
        self.click.btn2 = expand()
        self.click.btn2.on = False
        self.click.btn2.off = False

class key :
    def __init__(self):
        self.click = expand()
        self.click.left = expand()
        self.click.left.on = False
        self.click.left.off = False
        self.click.right = expand()
        self.click.right.on = False
        self.click.right.off = False
        self.click.s = expand()
        self.click.s.on = False
        self.click.s.off = False
        self.click.x = expand()
        self.click.x.on = False
        self.click.x.off = False
        self.click.m = expand()
        self.click.m.on = False
        self.click.m.off = False
        self.click.m.switch = False
        self.click.period = expand()
        self.click.period.on = False
        self.click.period.off = False
        self.click.period.switch = False



map = map()
map.size.width, map.size.height = screen_width*5, screen_height*3
map_number = 1

lands = []
trial = 0
land_number = 50
while trial < land_number :
    lw = random.randint(100, 200)
    lh = 60
    lands.append((random.randint(0, map.size.width - lw), random.randint(0, map.size.height - lh), lw, lh))
    for land in lands[:-2] :
        if lands[trial][1] == land[1] :
            trial -= 1
            del lands[-1]
            break
    trial += 1
# box_width = 200
# box_m, box_n = map.size.width // box_width + 1, map.size.height // box_width + 1
# for i in range(box_m//2, box_m) :
#     for j in range(box_n) :
#         lands.append((i*box_width, j*box_width, box_width, box_width))
lands.insert(0, (0, map.size.height, map.size.width, 0))
lands.append((0,0,0,0))
land_width = 2

small_mmxr, small_mmyr, minimap_gap = 1/6, 1/5, screen_width * 1/50
small_minimap_surface = pygame.Surface((screen_width*small_mmxr, screen_height*small_mmyr), pygame.SRCALPHA, 32)
big_mmxr, big_mmyr, minimap_gap = 48/50, 1, screen_width * 1/50
big_minimap_surface = pygame.Surface((screen_width*big_mmxr, screen_height*big_mmyr), pygame.SRCALPHA, 32)
small_minimap_surface.set_alpha(100)
big_minimap_surface.set_alpha(100)

key = key()

dt = 1/60
t=0
t1=40
t2=20
tst = 0 # turret summon time
tsct = 120 # turret summon cooltime
stone = object()
stone.summon = True
characters = [jessi, turret, stone]
stone.size.width, stone.size.height, stone.position.x, stone.position.y = 200, 200, screen_width/2, screen_height/2
stone.theta = 30 / 180 * pi
stone.weight = 200
drop_speed = 1
drop_max_speed = 30
land_friction, air_friction = 1, 1/10
rotation_friction = 1/50
least_theta = 1/400
shake_theta = .0002
line_length, line_width = 30, 2
jessi.summon = True
jessi.size.width, jessi.size.height = 40, 188
scale = 80
impact = 70
impact_dic = ["head", "upbody", "lleftthighc", "lleftlegc", "lleftfootc", "lrightthighc", "lrightlegc", "lrightfootc", "lleftuparm", "lleftdownarm", "llefthand",\
              "lrightuparm", "lrightdownarm", "lrighthand"]
impact_dic.remove("upbody")
impact_dic.remove("llefthand")
impact_dic.remove("lrighthand")
impact_dic.remove("lleftdownarm")
impact_dic.remove("lrightdownarm")
screen_color = "white"
x = 0
zoom_number = 1
impact_velocity = 5


pygame.key.set_repeat(5)
clock = pygame.time.Clock()
running = True
##########################################################################################
##########################################################################################
##########################################################################################
while running :
    clock.tick(1/dt)
    t += 1
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_ESCAPE :
                running = False
            if event.key == pygame.K_LEFT :
                key.click.left.on = True
            if event.key == pygame.K_RIGHT :
                key.click.right.on = True
            if event.key == pygame.K_c :
                jessi.jump = True
            if event.key == pygame.K_f:
                pass
            if event.key == pygame.K_SPACE:
                jessi.dash = True
            if event.key == pygame.K_s :
                if tst==0 or t-tst>tsct :
                    key.click.s.on = True
                    key.click.s.off = False
            if event.key == pygame.K_x:
                if jessi.weapon.eball.cooldown == False :
                    jessi.weapon.eball.charge = True
                    key.click.x.on = True
            if event.key == pygame.K_m :
                key.click.m.on = True
        if event.type == pygame.KEYUP :
            if event.key == pygame.K_LEFT:
                key.click.left.on = False
                key.click.left.off = True
                jessi.act = "stand"
            if event.key == pygame.K_RIGHT:
                key.click.right.on = False
                key.click.right.off = True
                jessi.act = "stand"
            if event.key == pygame.K_c:
                jessi.jump = False
            if event.key == pygame.K_f:
                if jessi.act != "hard land" :
                    jessi.act = "hard land"
                else :
                    jessi.act = "stand"
            if event.key == pygame.K_SPACE:
                jessi.dash = False
            if event.key == pygame.K_DOWN :
                jessi.sit_time = 0
                jessi.act = "stand"
            if event.key == pygame.K_s :
                if tst==0 or t-tst>tsct :
                    key.click.s.off = True
                    key.click.s.on = False
            if event.key == pygame.K_x:
                if jessi.weapon.eball.cooldown and jessi.weapon.eball.charge :
                    jessi.weapon.eball.charge = False
                    jessi.weapon.eball.charge = False
                    jessi.weapon.eball.image = [pygame.image.load("eball1.png"), pygame.image.load("eball2.png")]
                    key.click.x.off = True
            if event.key == pygame.K_m :
                key.click.m.off = True
            if event.key == pygame.K_PERIOD :
                key.click.period.off = True
        if event.type == pygame.MOUSEBUTTONDOWN :
            if event.button == 1 : # 좌클릭
                pass
            if event.button == 3 : # 우클릭
                pass
        if event.type == pygame.MOUSEBUTTONUP :
            if event.button == 1 :
                pass
            if event.button == 3 : # 우클릭
                pass

    # left right 정의
    left, right = jessi.left, 1 - jessi.left
    screen.fill(screen_color)


    # 제시 움직임
    if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2] :
        if pygame.key.get_pressed()[pygame.K_LEFT] :
            jessi.act = "walk"
            if jessi.xvelocity >= - jessi.walk_speed :
                jessi.xvelocity += - jessi.move_scale
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            jessi.act = "walk"
            if jessi.xvelocity <= jessi.walk_speed :
                jessi.xvelocity += jessi.move_scale
    elif pygame.key.get_pressed()[pygame.K_DOWN] and jessi.land:
        jessi.act = "sit"
        jessi.sit_time += 1
        if pygame.key.get_pressed()[pygame.K_LEFT] :
            jessi.act = "sit walk"
            if jessi.xvelocity >= -jessi.sit_speed :
                jessi.xvelocity += -jessi.move_scale
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            jessi.act = "sit walk"
            if jessi.xvelocity <= jessi.sit_speed :
                jessi.xvelocity += jessi.move_scale
    else :
        # act = "stand"
        if pygame.key.get_pressed()[pygame.K_LEFT] :
            jessi.act = "run"
            if jessi.xvelocity >= -jessi.run_speed :
                jessi.xvelocity += -jessi.move_scale
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            jessi.act = "run"
            if jessi.xvelocity <= jessi.run_speed :
                jessi.xvelocity += jessi.move_scale

    # box 제거
    if t >= 2 :
        if pygame.key.get_pressed()[pygame.K_x] :
            gap = 30
            for landy in lands_inside :
                if left :
                    if jessi.position.x - gap/2 <= landy[0] + landy[2] <= jessi.position.x + gap/2:
                        if landy[1] - jessi.size.height < jessi.position.y < landy[1] + landy[3] :
                            lands.remove(landy)
                if right :
                    if jessi.position.x + jessi.size.width - gap/2 <= landy[0] <= jessi.position.x + jessi.size.width + gap/2 :
                        if landy[1] - jessi.size.height < jessi.position.y < landy[1] + landy[3] :
                            lands.remove(landy)

    # 터렛 소환
    if key.click.s.off :
        key.click.s.off = False
        if jessi.left :
            turret.position.x = jessi.position.x - turret.distance - turret.size.width
            turret.position.y = jessi.position.y + jessi.size.height - turret.height - turret.size.height
            turret.image.select = turret.image.left
        else :
            turret.position.x = jessi.position.x + jessi.size.width + turret.distance
            turret.position.y = jessi.position.y + jessi.size.height - turret.height - turret.size.height
            turret.image.select = turret.image.right
        turret.summon = True
        turret.land = False
        tst = t

    if key.click.m.on :
        key.click.m.on = False
        key.click.m.switch = True
    if key.click.m.off :
        key.click.m.off = False
        map_number += 1
        if map_number >= 3 : map_number = 0
    if key.click.period.off :
        key.click.period.off = False
        zoom_number = -(zoom_number-1) + 2

    # 랜드 랜덤 생성
    landsr = []
    lands_inside = [lands[0]]
    lands_inside_wide= [lands[0]]
    for landy in lands :
        if map.position.x - screen_width - landy[2] <= landy[0] <= map.position.x + screen_width * 2 and map.position.y - screen_height - landy[3] <= landy[1] <= map.position.y + screen_height * 2 :
            lands_inside_wide.append(landy)
            if (landy[0] + landy[2] >= map.position.x and landy[0] <= map.position.x+screen_width) and (landy[1] + landy[3] >= map.position.y and landy[1] <= map.position.y+screen_height) :
                l = len(landsr)
                landsr.append([0]*4)
                landsr[l][0] = landy[0] - map.position.x
                landsr[l][1] = landy[1] - map.position.y
                landsr[l][2] = landy[2]
                landsr[l][3] = landy[3]
                lands_inside.append(landy)

    # 일정한 중력 가해지는 식
    for c in characters :
        if c.summon :
            if c.yvelocity < c.drop_max_speed :
                c.yvelocity += drop_speed
            else : c.yvelocity = c.drop_max_speed


    # 랜딩 했을 때 중력에 대한 반작용
    for c in characters:
        if c.summon :
            if c.land :
                c.yvelocity -= drop_speed

    # 대쉬
    if jessi.land and pygame.key.get_pressed()[pygame.K_SPACE] and (jessi.dash_time == 0 or t-jessi.dash_time > jessi.dash_ct) :
        jessi.land = False
        jessi.yvelocity -= jessi.jump_speed * jessi.dash_jump_ratio
        jessi.xvelocity += -jessi.dash_speed*left + jessi.dash_speed*right
        if (jessi.act == "sit" or jessi.act == "sit walk") and jessi.sit_time >= 20 :
            jessi.yvelocity -= jessi.dash_speed * (jessi.power_jump_amount - 1)
            jessi.xvelocity += (-jessi.dash_speed * left + jessi.dash_speed * right * (jessi.power_dash_amount - 1))
        jessi.act = "dash"
        jessi.dash_time = t

    # 점프
    for c in characters :
        if c.summon :
            if c.jump and c.land and (c.jump_time == 0 or t - c.jump_time > c.jump_ct) and c.yvelocity == 0 :
                c.yvelocity -= c.jump_speed
                if (c.act == "sit" or c.act == "sit walk") and c.sit_time >= 20 :
                    c.yvelocity -= c.jump_speed * (c.power_jump_amount - 1)
                c.jump = False
                c.land = False
                c.jump_time = t

    # 낙하
    for c in characters :
        if c.summon :
            for landy in lands_inside :
                if landy[1] == jessi.position.y + jessi.size.height :
                    if landy == c.inland :
                        if jessi.xvelocity > 0 and jessi.position.x <= landy[0] + landy[2] and jessi.position.x + jessi.xvelocity*dt >= landy[0] + landy[2] :
                            c.land = False
                        elif jessi.xvelocity < 0 and jessi.position.x + jessi.size.width >= landy[0] and jessi.position.x + jessi.xvelocity*dt + jessi.size.width <= landy[0] :
                            c.land = False
                        elif (landy[0] - jessi.size.width <= jessi.position.x <= landy[0] + landy[2]) == False :
                            c.land = False

    # 공기 저항 및 마찰
    for c in characters :
        if c.summon :
            if c.land :
                if c.xvelocity > 0 :
                    if c.xvelocity < land_friction :    c.xvelocity = 0
                    else :                              c.xvelocity -= land_friction
                elif c.xvelocity < 0 :
                    if c.xvelocity > -land_friction :   c.xvelocity = 0
                    else :                              c.xvelocity += land_friction
            else :
                if c.xvelocity > 0 :
                    if c.xvelocity < air_friction : c.xvelocity = 0
                    else :                          c.xvelocity -= air_friction
                elif c.xvelocity < 0 :
                    if c.xvelocity > -air_friction : c.xvelocity = 0
                    else :                           c.xvelocity += air_friction
            if c.tvelocity > 0 :
                if c.tvelocity < rotation_friction : c.tvelocity = 0
                else : c.tvelocity -= rotation_friction
            elif c.tvelocity < 0 :
                if c.tvelocity > - rotation_friction : c.tvelocity = 0
                else : c.tvelocity -= - rotation_friction


    # 속도 음수면 up, 속도 양수면 down, x속도가 어느정도 이상이면 dash
    if "air_act" == "air_act" :
        if jessi.free and jessi.yvelocity < 0 :
            jessi.act = "up"
            if abs(jessi.xvelocity) >= jessi.dash_speed - jessi.dash_act_amount :
                jessi.act = "dash"
        elif jessi.free and jessi.yvelocity > 0 :
            jessi.act = "down"

    # 발사


    # 착지
    for c in characters :
        if c.summon :
            for landy in lands_inside :
                if landing(c, c.position.x, c.position.y, c.size.width, c.size.height, landy[0], landy[1], landy[2]) :
                    c.position.y = landy[1] - c.size.height
                    if c == jessi :
                        if abs(jessi.xvelocity) >= jessi.hardland_min_speed or jessi.yvelocity >= jessi.hardland_min_speed :
                            jessi.act = "hard land"
                        elif jessi.yvelocity >= jessi.land_min_speed :
                            jessi.act = "land"
                        elif jessi.softland_min_speed <= jessi.yvelocity < jessi.land_min_speed :
                            jessi.act = "soft land"
                        else : jessi.act = "stand"
                    c.yvelocity = 0
                    c.land = True
                    c.land_time = t
                    c.inland = landy

    if "impact ball" != "impact ball" :
        cc_x, cc_y, cc_r = map.size.width/2-200, map.size.height-100, 100
        cc_rx, cc_ry = cc_x - mx, cc_y - my

        for p in impact_dic :
            exec("px, py, pth = jessi.part.%s.position.cx, jessi.part.%s.position.cy, jessi.part.%s.theta" % (p, p, p))
            betth = aatan(cc_rx - px, cc_ry - py)
            b =(betth*180/pi) % 360
            if right : b = (180 - b) % 360
            exec("a = %s_fun(b)" % p)
            if left : ex, ey = (px + a*cos(- pth + b/180*pi), py + a*sin(- pth + b/180*pi))
            elif right : ex, ey = (px + - a*cos(pth + b/180*pi), py + a*sin(pth + b/180*pi))
            if abs(ex-cc_rx) <= cc_r :
                if (ex-cc_rx)**2 + (ey-cc_ry)**2 <= cc_r**2 :
                    dir = unit_vector((ex-cc_rx, ey-cc_ry))
                    dir = dir[0], -abs(dir[1])
                    if jessi.free :
                        jessi.free=False
                        jessi.xvelocity += dir[0] * impact
                        jessi.yvelocity += dir[1] * impact
                        jessi.land = False
                        jessi.hp -= 10
                        break
        pygame.draw.circle(screen, color="black", width=5, radius=cc_r, center=(cc_rx, cc_ry))

    #map 끝에 가면 튕겨져 나오는 거
    if jessi.position.x <= 0 or jessi.position.x + jessi.size.width >= map.size.width :
        if jessi.free :
            jessi.free = False
            jessi.xvelocity += (jessi.position.x <= map.size.width/2) * (jessi.xvelocity + impact/5) - (1-(jessi.position.x <= map.size.width/2))*(jessi.xvelocity + impact/5)
            jessi.land = False

    # free가 아닐 때 시간이 지나면 free하는 식
    if jessi.free == False and jessi.free_time == 0 :
        jessi.free_time = t
    if t-jessi.free_time > 3 :
        jessi.free = True
        jessi.free_time = 0

    # 최대 속도 제한
    for c in characters :
        if c.summon :
            if c.yvelocity > c.drop_max_speed and c.free :
                c.yvelocity = c.drop_max_speed

    # 객체 x, y 움직임 재연
    for c in characters :
        if c.summon :
            c.position.x += c.xvelocity * dt * scale
            c.position.y += c.yvelocity * dt * scale

    for c in characters :
        if c.summon :
            if c.position.y + c.size.height > map.size.height : c.position.y = map.size.height - c.size.height
            if c.position.x < 0 :
                c.position.x = 0
                c.xvelocity = impact/10
                c.position.x += c.xvelocity * dt * scale
            elif c.position.x + c.size.width > map.size.width :
                c.position.x = map.size.width - c.size.width
                c.xvelocity = - impact/10
                c.position.x += c.xvelocity * dt * scale

            for landy in lands_inside :
                if landy[1] - c.size.height < c.position.y - c.yvelocity * dt * scale  < landy[1] + landy[3] :
                    if landy[0] - c.size.width < c.position.x < landy[0] + landy[2] :
                        if c.position.x + c.size.width - c.xvelocity * dt * scale <= landy[0] :
                            c.position.x = landy[0] - c.size.width
                            if c.xvelocity >= impact_velocity :
                                c.xvelocity *= - 1/2
                                c.position.x += c.xvelocity * dt * scale
                        elif landy[0] + landy[2] <= c.position.x - c.xvelocity * dt * scale :
                            c.position.x = landy[0] + landy[2]
                            if c.xvelocity <= -impact_velocity :
                                c.xvelocity *= - 1/2
                                c.position.x += c.xvelocity * dt * scale
                if landy[0] - c.size.width < c.position.x - c.xvelocity * dt * scale < landy[0] + landy[2] :
                    if landy[1] - c.size.height < c.position.y < landy[1] + landy[3] :
                        if landy[1] + landy[3] <= c.position.y - c.yvelocity * dt * scale :
                            c.position.y = landy[1] + landy[3]
                            c.yvelocity *= 0
                            if pygame.key.get_pressed()[pygame.K_x] : lands.remove(landy)




    # 객체 상대적 위치
    for c in characters :
        if c.summon == True :
            x,y,mx,my,cw,ch = c.position.x, c.position.y, map.position.x, map.position.y, c.size.width, c.size.height
            c.position.cx = x + cw/2, y + ch/2
            c.position.rx, c.position.ry = x-mx, y-my
            c.hitbox.update(c.position.rx, c.position.ry, c.size.width, c.size.height)


    # 맵 움직임 및 맵 뷰 움직임 제한
    # 맵 x축 움직임
    map.position.x += (jessi.position.x - screen_width/2 + jessi.size.width/2 - map.position.x) * map.speed
    if abs(map.position.x - jessi.position.x + screen_width/2 - jessi.size.width/2) <= 1 :
        map.position.x = jessi.position.x - screen_width/2 + jessi.size.width/2
    if map.size.height - screen_height/2 <= jessi.position.y + jessi.size.height/2 :
        map.position.y += (map.size.height - screen_height - map.position.y) * map.speed
        if abs(map.size.height - screen_height - map.position.y) <= 1 :
            map.position.y = map.size.height - screen_height
    else :
        map.position.y += (jessi.position.y + jessi.size.height/2 - screen_height/2 - map.position.y) * map.speed
        if abs(jessi.position.y + jessi.size.height/2 - screen_height/2 - map.position.y) <= 1 :
            map.position.y = jessi.position.y + jessi.size.height/2 - screen_height/2
    if map.position.x < 0 : map.position.x = 0
    if map.position.x > map.size.width - screen_width : map.position.x = map.size.width - screen_width
    if map.position.y < 0 : map.position.y = 0

    if jessi.act == "run" or jessi.act == "dash" :
        down, width = 10, 40
        jessi.hitbox.x += -width*left + 0*right
        jessi.hitbox.y += down
        jessi.hitbox.width += width
        jessi.hitbox.height += -down
    elif jessi.act == "sit" or jessi.act == "sit walk" or jessi.act == "soft land" or jessi.act == "hard land" or jessi.act == "land" :
        jessi.size.width, jessi.size.height = 35, 188
        down, width = 55, 50
        jessi.hitbox.x += -width*left + 0*right
        jessi.hitbox.y += down
        jessi.hitbox.width += width
        jessi.hitbox.height += -down
    else :
        down, width = 10, 25
        jessi.hitbox.x += -width*left + 0*right
        jessi.hitbox.y += down
        jessi.hitbox.width += width
        jessi.hitbox.height += -down


    #######################################################################################################################################################
    #######################################################################################################################################################
    #######################################################################################################################################################
    #######################################################################################################################################################
    #######################################################################################################################################################
    #######################################################################################################################################################
    #######################################################################################################################################################
    #######################################################################################################################################################
    #######################################################################################################################################################
    #######################################################################################################################################################
    if turret.summon :
        x, y, w, r = turret.position.x, turret.position.y, turret.size.width, -5
        # pygame.draw.line(screen, "grey", start_pos=(x-r,y), end_pos=(x+w+r, y))
        lands[land_number + 1] = (x-r, y + 8, w+2*r, 0)

    # 랜드 그리기
    for landy in landsr :
        if (landy[0] + landy[2] >= 0 and landy[0] <= screen_width) and (landy[1] + landy[3] >= 0 and landy[1] <= screen_height) :
            pygame.draw.rect(screen, "white", landy, width=0)
            pygame.draw.rect(screen, "black", landy, width=land_width)

    # 소환 대기 모션
    if key.click.s.on :
        tm, ta, tp = 120, 50, 3 # transparent_mid, transparent_amplitude, transparent_period
        tr = tm - ta * sin((t / tp))
        if jessi.left :
            turret.image.transparent.left.set_alpha(abs(tr))
            mslh = map.size.height # max_summon_landing_height
            for landy in lands_inside :
                lx = jessi.position.x - turret.distance - turret.size.width
                w, h = turret.size.width, turret.size.height
                if (landy[0] <= lx <= landy[0]+landy[2] or landy[0] <= lx + w <= landy[0]+landy[2]) and landy[1] >= jessi.position.y + jessi.size.height - turret.height :
                    mslh = min(mslh, landy[1]-h)
            screen.blit(turret.image.transparent.left, (lx - map.position.x, mslh- map.position.y))
        else :
            turret.image.transparent.right.set_alpha(abs(tr))
            mslh = map.size.height
            for landy in lands_inside :
                rx = jessi.position.x + jessi.size.width + turret.distance
                w, h = turret.size.width, turret.size.height
                if (landy[0] <= rx <= landy[0]+landy[2] or landy[0] <= rx + w <= landy[0]+landy[2]) and  landy[1] >= jessi.position.y + jessi.size.height - turret.height :
                    mslh = min(mslh, landy[1]-h)
            screen.blit(turret.image.transparent.right, (rx - map.position.x, mslh- map.position.y))

    # 객체 그리기
    for c in characters :
        if c.summon :
            if c == turret :
                screen.blit(c.image.select, (c.position.rx, c.position.ry))

    for p in partdic :
        exec("noe = len(jessi.part.%s.end_value_tuple_list)" % p)
        for i in range(noe) :
            exec("jessi.part.%s.%s = jessi.part.%s.end_value_tuple_list[i][0]" % (p, "left_end_point{}x".format(str(i+1)), p))
            exec("jessi.part.%s.%s = jessi.part.%s.end_value_tuple_list[i][1]" % (p, "left_end_point{}y".format(str(i+1)), p))
            exec("jessi.part.%s.%s = jessi.part.%s.end_value_tuple_list[i][2]" % (p, "right_end_point{}x".format(str(i+1)), p))
            exec("jessi.part.%s.%s = jessi.part.%s.end_value_tuple_list[i][3]" % (p, "right_end_point{}y".format(str(i+1)), p))
            exec("jessi.part.%s.%s = jessi.part.%s.%s * jessi.left + jessi.part.%s.%s * (1-jessi.left)" % (p, "end_point{}x".format(str(i+1)), p, "left_end_point{}x".format(str(i+1)), p, "right_end_point{}x".format(str(i+1))))
            exec("jessi.part.%s.%s = jessi.part.%s.%s * jessi.left + jessi.part.%s.%s * (1-jessi.left)" % (p, "end_point{}y".format(str(i+1)), p, "left_end_point{}y".format(str(i+1)), p, "right_end_point{}y".format(str(i+1))))

    # 다양한 act act act
    if jessi.act == "stand" :
        rotation_list = [
            ["downbody", 0, 0, 0, (- 180 + (-1*sin(t/20)+1)*jessi.left + (-1*sin(t/20)+3)*(1-jessi.left), + 130 + (-1*sin(t/20)+1)*jessi.left + (1*sin(t/20)+1)*(1-jessi.left))], \
            ["upbody", "downbody", (-2*sin(t/20+pi/6)+25)/180*pi*jessi.left + -(2*sin(t/20+pi/8)+15)/180*pi*(1-jessi.left), 3, (0, -20, 0 ,-20)], \
            ["neck", "upbody", 0, 3, (0,-4,0,-4)], \
            ["head", "neck", (3*sin(t/20-pi/3)-15)/180*pi*jessi.left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-jessi.left), 1, (0,-35,0,-35)], \
            ["leo", "neck", (3*sin(t/20-pi/3)-15)/180*pi*jessi.left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-jessi.left), 1, (0,-35,0,-35)], \
            ["lec", "neck", (3*sin(t/20-pi/3)-15)/180*pi*jessi.left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-jessi.left), 1, (0,-35,0,-35)], \
            ["reo", "neck", (3*sin(t/20-pi/3)-15)/180*pi*jessi.left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-jessi.left), 1, (0,-35,0,-35)], \
            ["rec", "neck", (3*sin(t/20-pi/3)-15)/180*pi*jessi.left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-jessi.left), 1, (0,-35,0,-35)], \
            ["leb", "neck", (3*sin(t/20-pi/3)-15)/180*pi*jessi.left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-jessi.left), 1, (0,-35,0,-35)], \
            ["reb", "neck", (3*sin(t/20-pi/3)-15)/180*pi*jessi.left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-jessi.left), 1, (0,-35,0,-35)], \
            ["nose", "neck", (3*sin(t/20-pi/3)-15)/180*pi*jessi.left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-jessi.left), 1, (0,-35,0,-35)], \
            ["mouth", "neck", (3*sin(t/20-pi/3)-15)/180*pi*jessi.left + -(3*sin(t/20-pi/3)+-5)/180*pi*(1-jessi.left), 1, (0,-35,0,-35)], \
            ["hair1", "head",(1*sin(t/20))/180*pi*jessi.left + (1*sin(t/16)-10)/180*pi*(1-jessi.left), 1, (-10,35,10,35)], \
            ["hair2", "head",(1*sin(t/21))/180*pi*jessi.left + (1*sin(t/18)-10)/180*pi*(1-jessi.left), 2, (-10,35,10,35)], \
            ["hair3", "head",(1*sin(t/17)+5)/180*pi*jessi.left + (1*sin(t/15)-10)/180*pi*(1-jessi.left), 3, (-10,35,10,35)], \
            ["hair4", "head",(1*sin(t/18)+3)/180*pi*jessi.left + (1*sin(t/19)-10)/180*pi*(1-jessi.left), 4, (-10,35,10,35)], \
            ["hair5", "head",(1*sin(t/15))/180*pi*jessi.left + (1*sin(t/20)-5)/180*pi*(1-jessi.left), 5, (-10,35,10,35)], \
            ["hair6", "head",(3*sin(t/20))/180*pi*jessi.left + (3*sin(t/20))/180*pi*(1-jessi.left), 6, (-23,-10,23,-10)], \
            ["hair7", "head",(3*sin(t/20))/180*pi*jessi.left + (3*sin(t/20))/180*pi*(1-jessi.left), 7, (33,-7,-34,-8)], \
            ["hair8", "hair3",(5*sin(t/15)+10)/180*pi, 1, (40,-45,-35,-45)], \
            ["hair9", "hair4",(5*sin(t/17)+10)/180*pi, 1, (-45,-46,43,-46)], \
            ["hatdownf", "head", 0, 8, (0,0,0,0)], \
            ["hatdownb", "head", 0, 9, (0,0,0,0)], \
            ["hatglass", "hatdownf", 0, 1, (0,0,0,0)], \
            ["hatup", "head", 0, 10, (0,0,0,0)], \
            ["lleftuparm", "upbody", 0*jessi.left + pi/7*(1-jessi.left), 1, (2, 10, -2, 11)], \
            ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
            ["llefthand", "lleftdownarm", 0, 1, (0, -2, -5, -2)], \
            ["lrightuparm", "upbody", 0*left + -pi/7*right, 2, (-4,11,4,11)], \
            ["lrightdownarm", "lrightuparm", 0, 1, (2, -10, -2, -10)], \
            ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
            ["lleftthigh", "downbody", (5*sin(t/20) - 10)/180*pi*left + (5*sin(t/20) + 30)/180*pi*right, 1, (-4, 10, -4, 10)], \
            ["lleftleg", "lleftthigh", (-10*sin(t/20)+27)/180*pi*left + (-10*sin(t/20)-45)/180*pi*right, 1, (1, 8, -1, 8)], \
            ["lleftfoot", "lleftleg", -jessi.part.lleftleg.theta, 1, (-1, 6, 1, 6)], \
            ["lrightthigh", "downbody", (5*sin(t/20)-10)/180*pi*left + (5*sin(t/20)+10)/180*pi*right, 2, (0, 9, 0, 9)], \
            ["lrightleg", "lrightthigh", (-10*sin(t/20)+35)/180*pi*left + (-10*sin(t/20)-30)/180*pi*right, 1, (1, 8, -2, 8)], \
            ["lrightfoot", "lrightleg", -jessi.part.lrightleg.theta, 1, (-4, 6, 3, 6)], \
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
    if jessi.act == "walk" :
        head_theta = (-15)/180*pi*left + 0*right
        rotation_list = [
            ["downbody", 0, 0, 0, (-180, 130 + (3*sin(t/5-pi/2) + 1)*left + (3*sin(t/5-pi/2) + 1)*right)], \
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
    if jessi.act == "run" :
        head_theta = (3*sin(t/7)-15)/180*pi*left + (3*sin(t/7)+15)/180*pi*right
        rotation_list = [
            ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-180, 130 + 6+ (3*sin(t/3.5-pi/2) + -1)*left + (3*sin(t/3.5-pi/2) + -1)*right)], \
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
            ["llefthand", "lleftdownarm", -jessi.part.lleftdownarm.theta, 1, (0, -2, -5, -2)], \
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
    if jessi.act == "up" :
        head_theta = -15/180*pi*left + 15/180*pi*right
        rotation_list = [
            ["downbody", 0, (0)/180*pi*left + (-0)/180*pi*right, 0, (-180, 130)], \
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
            ["llefthand", "lleftdownarm", -jessi.part.lleftdownarm.theta, 1, (0, -2, -5, -2)], \
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
    if jessi.act == "down" :
        head_theta = -15/180*pi*left + 15/180*pi*right
        rotation_list = [
            ["downbody", 0, (0)/180*pi*left + (-0)/180*pi*right, 0, (-180, 130)], \
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
            ["llefthand", "lleftdownarm", -jessi.part.lleftdownarm.theta, 1, (0, -2, -5, -2)], \
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
    if jessi.act == "land" :
        head_theta = -30/180*pi*left + 30/180*pi*right
        rotation_list = [
            ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-180, 143*left + 140*right)], \
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
            ["llefthand", "lleftdownarm", -jessi.part.lleftdownarm.theta, 1, (0, -2, -5, -2)], \
            ["lrightuparm", "upbody", -0/180*pi*left + 10/180*pi*right, 2, (-4,11,4,11)], \
            ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
            ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
            ["lleftthigh", "downbody", -40/180*pi*left + 50/180*pi*right, 1, (-4, 10, -4, 10)], \
            ["lleftleg", "lleftthigh", 85/180*pi*left + -100/180*pi*right, 1, (1, 8, -1, 8)], \
            ["lleftfoot", "lleftleg", -jessi.part.lleftleg.theta, 1, (-1, 6, 1, 6)], \
            ["lrightthigh", "downbody", -50/180*pi*left + 40/180*pi*right, 2, (0, 9, 0, 9)], \
            ["lrightleg", "lrightthigh", 120/180*pi*left + -90/180*pi*right, 1, (1, 8, -2, 8)], \
            ["lrightfoot", "lrightleg", -jessi.part.lrightleg.theta, 1, (-4, 6, 3, 6)], \
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
    if jessi.act == "soft land" :
        head_theta = -30/180*pi*left + 30/180*pi*right
        rotation_list = [
            ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-180, 132*left + 138*right)], \
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
            ["llefthand", "lleftdownarm", -jessi.part.lleftdownarm.theta, 1, (0, -2, -5, -2)], \
            ["lrightuparm", "upbody", -0/180*pi*left + 10/180*pi*right, 2, (-4,11,4,11)], \
            ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
            ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
            ["lleftthigh", "downbody", -20/180*pi*left + 55/180*pi*right, 1, (-4, 10, -4, 10)], \
            ["lleftleg", "lleftthigh", 30/180*pi*left + -80/180*pi*right, 1, (1, 8, -1, 8)], \
            ["lleftfoot", "lleftleg", -jessi.part.lleftleg.theta, 1, (-1, 6, 1, 6)], \
            ["lrightthigh", "downbody", -20/180*pi*left + 40/180*pi*right, 2, (0, 9, 0, 9)], \
            ["lrightleg", "lrightthigh", 55/180*pi*left + -80/180*pi*right, 1, (1, 8, -2, 8)], \
            ["lrightfoot", "lrightleg", -jessi.part.lrightleg.theta, 1, (-4, 6, 3, 6)], \
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
    if jessi.act == "hard land" :
        head_theta = -30/180*pi*left + 30/180*pi*right
        rotation_list = [
            ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-180, 150*left + 147*right)], \
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
            ["llefthand", "lleftdownarm", -jessi.part.lleftdownarm.theta, 1, (0, -2, -5, -2)], \
            ["lrightuparm", "upbody", -0/180*pi*left + 10/180*pi*right, 2, (-4,11,4,11)], \
            ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
            ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
            ["lleftthigh", "downbody", -50/180*pi*left + 70/180*pi*right, 1, (-4, 10, -4, 10)], \
            ["lleftleg", "lleftthigh", 105/180*pi*left + -130/180*pi*right, 1, (1, 8, -1, 8)], \
            ["lleftfoot", "lleftleg", -jessi.part.lleftleg.theta, 1, (-1, 6, 1, 6)], \
            ["lrightthigh", "downbody", -70/180*pi*left + 60/180*pi*right, 2, (0, 9, 0, 9)], \
            ["lrightleg", "lrightthigh", 140/180*pi*left + -120/180*pi*right, 1, (1, 8, -2, 8)], \
            ["lrightfoot", "lrightleg", -jessi.part.lrightleg.theta, 1, (-4, 6, 3, 6)], \
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
    if jessi.act == "sit" :
        head_theta = -30/180*pi*left + 30/180*pi*right
        rotation_list = [
            ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-180, 154)], \
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
            ["hair1", "head",(1*sin(t/20))/180*pi*jessi.left + (1*sin(t/16)-10)/180*pi*(1-jessi.left), 1, (-10,35,10,35)], \
            ["hair2", "head",(1*sin(t/21))/180*pi*jessi.left + (1*sin(t/18)-10)/180*pi*(1-jessi.left), 2, (-10,35,10,35)], \
            ["hair3", "head",(1*sin(t/17)+5)/180*pi*jessi.left + (1*sin(t/15)-10)/180*pi*(1-jessi.left), 3, (-10,35,10,35)], \
            ["hair4", "head",(1*sin(t/18)+3)/180*pi*jessi.left + (1*sin(t/19)-10)/180*pi*(1-jessi.left), 4, (-10,35,10,35)], \
            ["hair5", "head",(1*sin(t/15))/180*pi*jessi.left + (1*sin(t/20)-5)/180*pi*(1-jessi.left), 5, (-10,35,10,35)], \
            ["hair6", "head",(3*sin(t/20))/180*pi*jessi.left + (3*sin(t/20))/180*pi*(1-jessi.left), 6, (-23,-10,23,-10)], \
            ["hair7", "head",(3*sin(t/20))/180*pi*jessi.left + (3*sin(t/20))/180*pi*(1-jessi.left), 7, (33,-7,-34,-8)], \
            ["hair8", "hair3",(5*sin(t/15)+10)/180*pi, 1, (40,-45,-35,-45)], \
            ["hair9", "hair4",(5*sin(t/17)+10)/180*pi, 1, (-45,-46,43,-46)], \
            ["hatdownf", "head", 0, 8, (0,0,0,0)], \
            ["hatdownb", "head", 0, 9, (0,0,0,0)], \
            ["hatglass", "hatdownf", 0, 1, (0,0,0,0)], \
            ["hatup", "head", 0, 10, (0,0,0,0)], \
            ["lleftuparm", "upbody", -20/180*pi*left + 30/180*pi*right, 1, (2, 10, -2, 11)], \
            ["lleftdownarm", "lleftuparm", 0, 1, (-5, -7, 5, -7)], \
            ["llefthand", "lleftdownarm", -jessi.part.lleftdownarm.theta, 1, (0, -2, -5, -2)], \
            ["lrightuparm", "upbody", -0/180*pi*left + 10/180*pi*right, 2, (-4,11,4,11)], \
            ["lrightdownarm", "lrightuparm", (-10)/180*pi*right, 1, (2, -10, -2, -10)], \
            ["lrighthand", "lrightdownarm", 0, 1, (6, -6, 0, -6)], \
            ["lleftthigh", "downbody", -70/180*pi*left + 90/180*pi*right, 1, (-4, 10, -4, 10)], \
            ["lleftleg", "lleftthigh", 115/180*pi*left + -140/180*pi*right, 1, (1, 8, -1, 8)], \
            ["lleftfoot", "lleftleg", -jessi.part.lleftleg.theta, 1, (-1, 6, 1, 6)], \
            ["lrightthigh", "downbody", -70/180*pi*left + 90/180*pi*right, 2, (0, 9, 0, 9)], \
            ["lrightleg", "lrightthigh", 150/180*pi*left + -130/180*pi*right, 1, (1, 8, -2, 8)], \
            ["lrightfoot", "lrightleg", -jessi.part.lrightleg.theta, 1, (-4, 6, 3, 6)], \
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
    if jessi.act == "sit walk" :
        head_theta = -30/180*pi*left + 30/180*pi*right
        rotation_list = [
            ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-180, 154*left + 154*right)], \
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
            ["llefthand", "lleftdownarm", -jessi.part.lleftdownarm.theta, 1, (0, -2, -5, -2)], \
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
    if jessi.act == "dash" :
        head_theta = (3*sin(t/7)-5)/180*pi*left + (3*sin(t/7)+5)/180*pi*right
        rotation_list = [
            ["downbody", 0, (10)/180*pi*left + (-10)/180*pi*right, 0, (-180, 130 + 4+ (3*sin(t/3.5-pi/2) + -1)*left + (3*sin(t/3.5-pi/2) + -1)*right)], \
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
            ["llefthand", "lleftdownarm", -jessi.part.lleftdownarm.theta, 1, (0, -2, -5, -2)], \
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

    for l in rotation_list :
        if l[0] == "downbody" :
            exec("jessi.part.%s.pi2 = %f" % (l[0], l[2]))
            exec("jessi.part.%s.start_point_x, jessi.part.%s.start_point_y = l[4]" % (l[0], l[0]))
        else :
            exec("jessi.part.%s.uppart = jessi.part.%s" % (l[0], l[1]))
            exec("jessi.part.%s.pi2 = l[2]" % l[0])
            exec("jessi.part.%s.start_point_x, jessi.part.%s.start_point_y = jessi.part.%s.end_point%sx, jessi.part.%s.end_point%sy" % (l[0], l[0], l[1], l[3], l[1], l[3]))
            exec("jessi.part.%s.left_center_x, jessi.part.%s.left_center_y, jessi.part.%s.right_center_x, jessi.part.%s.right_center_y = l[4]" % (l[0], l[0], l[0], l[0]))

    # 움직임이 끊임없게
    if t >= 10 :
        for p in partdic : # 모든 parts에서
            if p == "downbody" :
                exec("""if abs(jessi.part.%s.start_point_y - jessi.part.%s.bposition.spy) >= 5 :
                    if jessi.act == 'land' :
                        jessi.part.%s.pi2 = jessi.part.%s.theta2 + (jessi.part.%s.pi2 - jessi.part.%s.theta2) / 2
                        jessi.part.%s.start_point_y = jessi.part.%s.bposition.spy + (jessi.part.%s.start_point_y - jessi.part.%s.bposition.spy) / 2
                    else :
                        jessi.part.%s.pi2 = jessi.part.%s.theta2 + (jessi.part.%s.pi2 - jessi.part.%s.theta2) / 3
                        jessi.part.%s.start_point_y = jessi.part.%s.bposition.spy + (jessi.part.%s.start_point_y - jessi.part.%s.bposition.spy) / 3
                    """ % (p,p,p,p,p,p,p,p,p,p,p,p,p,p,p,p,p,p))
                continue
            exec("""if (jessi.part.%s.lr == 'left' and left) or (jessi.part.%s.lr == 'right' and right) :
                if abs(jessi.part.%s.pi2 - jessi.part.%s.theta2) >= 1/10 :                
                    if jessi.act == "land" or jessi.act == "sit" :
                        jessi.part.%s.pi2 = jessi.part.%s.theta2 + (jessi.part.%s.pi2 - jessi.part.%s.theta2) / 2
                    else :
                        jessi.part.%s.pi2 = jessi.part.%s.theta2 + (jessi.part.%s.pi2 - jessi.part.%s.theta2) / 4""" % (p,p,p,p,p,p,p,p,p,p,p,p))

    # 코어, 다운바디는 따로 정의
    p = jessi.part.downbody
    jessi.size.width, jessi.size.height = 39, 188
    p.position.x, p.position.y = jessi.position.rx + p.start_point_x + 186*left + 179*right, jessi.position.ry + p.start_point_y - 7

    if jessi.act == "sit" or jessi.act == "sit walk" or jessi.act == "soft land" or jessi.act == "hard land" or jessi.act == "land" :
        p.position.x, p.position.y = jessi.position.rx + p.start_point_x + 190*left + 174*right, jessi.position.ry + p.start_point_y - 7
    p.position.cx, p.position.cy = p.position.x + p.r/2, p.position.y + p.r/2
    p.theta = p.pi2
    if left : p.rotate = p.leftimages[round(p.theta*180/pi)%360]
    elif right : p.rotate = p.rightimages[round(p.theta*180/pi)%360]
    cx, cy = p.position.cx, p.position.cy
    ct, st = cos(-p.theta), sin(-p.theta)
    for i in range(len(p.end_value_tuple_list)) :
        exec("p.end_point%srx = ct * p.end_point%sx - st * p.end_point%sy" % (str(i+1), str(i+1), str(i+1)))
        exec("p.end_point%sry = st * p.end_point%sx + ct * p.end_point%sy" % (str(i+1), str(i+1), str(i+1)))
    # # 접합점 그리기
    if p.end_point_sign :
        for i in range(len(p.end_value_tuple_list)) :
            exec("pygame.draw.circle(screen, 'red', radius=2, width=1, center=(cx + p.end_point%srx, cy + p.end_point%sry))" % (str(i+1), str(i+1)))
    # 직교좌표선 그리기
    if p.lines :
        pygame.draw.line(screen, "red", start_pos=(cx, cy), end_pos=(cx + line_length * ct, cy + line_length * st), width=line_width)
        pygame.draw.line(screen, "blue", start_pos=(cx, cy), end_pos=(cx - line_length * st, cy + line_length * ct), width=line_width)
        pygame.draw.line(screen, "black", start_pos=(cx, cy), end_pos=(cx - line_length * ct, cy - line_length * st), width=line_width)
        pygame.draw.line(screen, "black", start_pos=(cx, cy), end_pos=(cx + line_length * st, cy - line_length * ct), width=line_width)

    # 움직일 때 왼쪽 다리, 오른쪽 다리 앞에 올지
    partdic3 = list(partdic.keys()).copy()
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

    # 랜덤으로 눈 깜빡임 재현
    if "eye_close" == "eye_close" :
        if t%60 == 1 :
            ect = random.randint(10,50)
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
        exec("pa = jessi.part.%s" % p)
        up = pa.uppart
        x, y = pa.start_point_x, pa.start_point_y
        pi1, pi2, ux, uy = up.theta, pa.pi2, up.position.x + up.r/2, up.position.y + up.r/2
        x0, y0 = ux + x, uy + y
        x1, y1 = ux + cos(pi1)*x + sin(pi1)*y, uy - sin(pi1)*x + cos(pi1)*y
        pa.position.cx, pa.position.cy = x0 + pa.left_center_x * left + pa.right_center_x * right, y0 + pa.left_center_y * left + pa.right_center_y * right
        x2, y2 = pa.position.cx - ux, pa.position.cy - uy
        pa.position.cx, pa.position.cy = ux + cos(pi1)*x2 + sin(pi1)*y2, uy - sin(pi1)*x2 + cos(pi1)*y2
        x3, y3 = pa.position.cx - x1, pa.position.cy - y1
        pa.position.cx, pa.position.cy = x1 + cos(pi2)*x3 + sin(pi2)*y3, y1 - sin(pi2)*x3 + cos(pi2)*y3
        pa.position.x, pa.position.y = pa.position.cx - pa.r/2, pa.position.cy - pa.r/2
        pa.theta = up.theta + pi2
        if left : pa.rotate = pa.leftimages[round(pa.theta*180/pi)%360]
        elif right : pa.rotate = pa.rightimages[round(pa.theta*180/pi)%360]
        for i in range(len(pa.end_value_tuple_list)) :
            exec("pa.end_point%sx = pa.left_end_point%sx * left + pa.right_end_point%sx * right" % (str(i+1), str(i+1), str(i+1)))
            exec("pa.end_point%sy = pa.left_end_point%sy * left + pa.right_end_point%sy * right" % (str(i+1), str(i+1), str(i+1)))
        cx, cy = pa.position.cx, pa.position.cy
        ct, st = cos(-pa.theta), sin(-pa.theta)
        for i in range(len(pa.end_value_tuple_list)):
            exec("pa.end_point%srx = ct * pa.end_point%sx - st * pa.end_point%sy" % (str(i + 1), str(i + 1), str(i + 1)))
            exec("pa.end_point%sry = st * pa.end_point%sx + ct * pa.end_point%sy" % (str(i + 1), str(i + 1), str(i + 1)))
        # # 접합점 그리기
        if pa.end_point_sign:
            for i in range(len(pa.end_value_tuple_list)):
                exec("pygame.draw.circle(screen, 'red', radius=2, width=1, center=(cx + pa.end_point%srx, cy + pa.end_point%sry))" % (str(i + 1), str(i + 1)))
        # 직교좌표선 그리기
        if pa.lines:
            pygame.draw.line(screen, "red", start_pos=(cx, cy), end_pos=(cx + line_length * ct, cy + line_length * st), width=line_width)
            pygame.draw.line(screen, "blue", start_pos=(cx, cy), end_pos=(cx - line_length * st, cy + line_length * ct), width=line_width)
            pygame.draw.line(screen, "black", start_pos=(cx, cy), end_pos=(cx - line_length * ct, cy - line_length * st), width=line_width)
            pygame.draw.line(screen, "black", start_pos=(cx, cy), end_pos=(cx + line_length * st, cy - line_length * ct), width=line_width)

    for p in draw_order_copy :
        exec("pa = jessi.part.%s" % p)
        screen.blit(pa.rotate, (pa.position.x, pa.position.y))

    for p in partdic :
        exec("jessi.part.%s.theta2 = jessi.part.%s.pi2" % (p, p))
        if p == "downbody" :
            jessi.part.downbody.bposition.spy = jessi.part.downbody.start_point_y
        if left :
            exec("jessi.part.%s.lr = 'left'" % p)
        elif right :
            exec("jessi.part.%s.lr = 'right'" % p)

    # 착지 후 자동으로 "stand" 상태로 바꾸는 식
    if t - jessi.land_time >= 7 and (jessi.act == "soft land") :
        jessi.act = "stand"
    if t - jessi.land_time >= 15 and (jessi.act == "land") :
        jessi.act = "stand"
    if t - jessi.land_time >= 90 and (jessi.act == "hard land") :
        jessi.act = "stand"

    if "foot_red_line" != "foot_red_line" :
        p1, p2, p3, p4 = jessi.part.downbody, jessi.part.lleftthigh, jessi.part.lleftleg, jessi.part.lleftfoot

        xx, yy = p1.position.cx, p1.position.cy
        aa, bb = p2.start_point_x, p2.start_point_y
        thth = p1.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa, bb = p2.left_center_x*left + p2.right_center_x*right, p2.left_center_y*left + p2.right_center_y*right
        thth = p2.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa, bb = p3.start_point_x, p3.start_point_y
        thth = p2.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa, bb = p3.left_center_x*left + p3.right_center_x*right, p3.left_center_y*left + p3.right_center_y*right
        thth = p3.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa, bb = p4.start_point_x, p4.start_point_y
        thth = p3.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa, bb = p4.left_center_x*left + p4.right_center_x*right, p4.left_center_y*left + p4.right_center_y*right
        thth = p4.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa1, bb1, aa2, bb2 = 5*left + 8*right, 7, -(9*left + 6*right), 7
        thth = p4.theta
        aa1, bb1, aa2, bb2 = cos(thth)*aa1 + sin(thth)*bb1, -sin(thth)*aa1 + cos(thth)*bb1, \
                             cos(thth)*aa2 + sin(thth)*bb2, -sin(thth)*aa2 + cos(thth)*bb2
        lfx2, lfy2, lfx1, lfy1 = xx + aa1, yy + bb1, xx + aa2, yy + bb2

        pygame.draw.line(screen, "red", width=3, start_pos=(lfx1, lfy1), end_pos=(lfx2, lfy2))



        p1, p2, p3, p4 = jessi.part.downbody, jessi.part.lrightthigh, jessi.part.lrightleg, jessi.part.lrightfoot

        xx, yy = p1.position.cx, p1.position.cy
        aa, bb = p2.start_point_x, p2.start_point_y
        thth = p1.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa, bb = p2.left_center_x*left + p2.right_center_x*right, p2.left_center_y*left + p2.right_center_y*right
        thth = p2.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa, bb = p3.start_point_x, p3.start_point_y
        thth = p2.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa, bb = p3.left_center_x*left + p3.right_center_x*right, p3.left_center_y*left + p3.right_center_y*right
        thth = p3.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa, bb = p4.start_point_x, p4.start_point_y
        thth = p3.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa, bb = p4.left_center_x*left + p4.right_center_x*right, p4.left_center_y*left + p4.right_center_y*right
        thth = p4.theta
        aa, bb = cos(thth)*aa + sin(thth)*bb, -sin(thth)*aa + cos(thth)*bb
        xx, yy = xx + aa, yy + bb

        aa1, bb1, aa2, bb2 = 6*left + 7*right, 7, -(8*left + 7*right), 7
        thth = p4.theta
        aa1, bb1, aa2, bb2 = cos(thth)*aa1 + sin(thth)*bb1, -sin(thth)*aa1 + cos(thth)*bb1, \
                             cos(thth)*aa2 + sin(thth)*bb2, -sin(thth)*aa2 + cos(thth)*bb2
        rfx2, rfy2, rfx1, rfy1 = xx + aa1, yy + bb1, xx + aa2, yy + bb2

        pygame.draw.line(screen, "red", width=3, start_pos=(rfx1, rfy1), end_pos=(rfx2, rfy2))

        for landy in landsr :
            if landy[0] < rfx1 and lfx2 < landy[0] + landy[2] and abs(landy[1]-lfy1) <= 3 and abs(landy[1]-lfy2) <= 3 and abs(landy[1]-rfy1) <= 3 and abs(landy[1]-rfy2) <= 3 :
                screen_color = "yellow"
                break
            else :
                if jessi.land :
                    # jessi.part.lleftleg.theta += 1/180*pi
                    # jessi.part.lleftfoot.theta = 0
                    screen_color = "white"

    if zoom_number > 1 :
        zoom = zoom_number
        # zoom = 1 + 1/30*(1+sin(t/120))
        zoom_shake_x, zoom_shake_y = 0, 0
        zoom_rect = pygame.Rect(0, 0, screen_width / zoom, screen_height / zoom)
        zoom_center_x, zoom_center_y = jessi.position.rx + jessi.size.width/2 + zoom_shake_x, jessi.position.ry + jessi.size.height/2 + zoom_shake_y
        if zoom_center_x <= zoom_rect.width/2 :
            zoom_center_x = zoom_rect.width/2
        elif zoom_center_x >= screen_width - zoom_rect.width/2 :
            zoom_center_x = screen_width - zoom_rect.width/2
        if zoom_center_y <= zoom_rect.height/2 :
            zoom_center_y = zoom_rect.height/2
        elif zoom_center_y >= screen_height - zoom_rect.height/2 :
            zoom_center_y = screen_height - zoom_rect.height/2
        zoom_rect.center = zoom_center_x, zoom_center_y
        zoom_surf = pygame.Surface(zoom_rect.size)
        zoom_surf.blit(screen, dest=(0,0), area=zoom_rect)
        zoom_surf = pygame.transform.scale(zoom_surf, (screen_width, screen_height))
        screen.blit(zoom_surf, dest=(0,0))

    if map_number >= 1 :
        if map_number == 1 :
            mmxr, mmyr = small_mmxr, small_mmyr
            minimap_surface = small_minimap_surface
        if map_number == 2 :
            mmxr, mmyr = big_mmxr, big_mmyr
            minimap_surface = big_minimap_surface
        pygame.draw.rect(minimap_surface, color="white", width=0, rect=(0, 0, screen_width*mmxr, screen_height*mmyr))
        pygame.draw.rect(minimap_surface, color="grey", width=1, rect=(0, 0, screen_width*mmxr, screen_height*mmyr))
        if screen_width*mmxr/screen_height*mmyr >= map.size.width/map.size.height :
            pygame.draw.rect(minimap_surface, color="white", width=0, rect=((screen_width*mmxr-map.size.width/map.size.height*screen_height*mmyr)/2,0, map.size.width/map.size.height*screen_height*mmyr, screen_height*mmyr))
            pygame.draw.rect(minimap_surface, color="black", width=1, rect=((screen_width*mmxr-map.size.width/map.size.height*screen_height*mmyr)/2+map.position.x/map.size.width*map.size.width/map.size.height*screen_height*mmyr, \
                                                                           map.position.y/map.size.height*screen_height*mmyr, \
                                                                           screen_width/map.size.width*map.size.width/map.size.height*screen_height*mmyr-1, \
                                                                           screen_height/map.size.height*screen_height*mmyr))
            for landy in lands :
                landy_width=int(landy[3]/map.size.height*screen_height*mmyr)
                if landy_width==0 : landy_width=1
                pygame.draw.line(minimap_surface, color="grey", width=landy_width, start_pos=((screen_width*mmxr-map.size.width/map.size.height*screen_height*mmyr)/2 + landy[0]/map.size.width*map.size.width/map.size.height*screen_height*mmyr, \
                                                                                              landy[1]/map.size.height*screen_height*mmyr), \
                                 end_pos=((screen_width*mmxr-map.size.width/map.size.height*screen_height*mmyr)/2 + landy[0]/map.size.width*map.size.width/map.size.height*screen_height*mmyr+ \
                                          landy[2]/map.size.width*map.size.width/map.size.height*screen_height*mmyr, landy[1]/map.size.height*screen_height*mmyr))
            pygame.draw.rect(minimap_surface, color="black", width=2, rect=((screen_width*mmxr-map.size.width/map.size.height*screen_height*mmyr)/2,0, \
                                                                            map.size.width/map.size.height*screen_height*mmyr, screen_height*mmyr))
            pygame.draw.rect(minimap_surface, color="red", width=0, rect=((screen_width*mmxr-map.size.width/map.size.height*screen_height*mmyr)/2+(jessi.hitbox.x + mx)/map.size.width*map.size.width/map.size.height*screen_height*mmyr, (jessi.hitbox.y + my)/map.size.height*screen_height*mmyr, jessi.hitbox.width/map.size.width*map.size.width/map.size.height*screen_height*mmyr, jessi.hitbox.height/map.size.height*screen_height*mmyr))
        else :
            pygame.draw.rect(minimap_surface, color="white", width=0, rect=(0, (screen_height*mmyr-map.size.height/map.size.width*screen_width*mmxr)/2, screen_width*mmxr, map.size.height/map.size.width*screen_width*mmxr))
            pygame.draw.rect(minimap_surface, color="black", width=1, rect=(map.position.x/map.size.width*screen_width*mmxr, \
                                                                            (screen_height*mmyr-map.size.height/map.size.width*screen_width*mmxr)/2 + map.position.y/map.size.height*map.size.height/map.size.width*screen_width*mmxr, \
                                                                            screen_width/map.size.width*screen_width*mmxr, \
                                                                            screen_height/map.size.height*map.size.height/map.size.width*screen_width*mmxr - 1))
            for landy in lands :
                landy_width = int(landy[3]/map.size.height*map.size.height/map.size.width*screen_width*mmxr)
                if landy_width==0 : landy_width=1
                pygame.draw.line(minimap_surface, color="grey", width=landy_width, start_pos=(landy[0]/map.size.width*screen_width*mmxr, (screen_height*mmyr-map.size.height/map.size.width*screen_width*mmxr)/2+landy[1]/map.size.height*map.size.height/map.size.width*screen_width*mmxr), \
                                 end_pos=(landy[0]/map.size.width*screen_width*mmxr+landy[2]/map.size.width*screen_width*mmxr, (screen_height*mmyr-map.size.height/map.size.width*screen_width*mmxr)/2+landy[1]/map.size.height*map.size.height/map.size.width*screen_width*mmxr))
            pygame.draw.rect(minimap_surface, color="black", width=2, rect=(0, (screen_height*mmyr-map.size.height/map.size.width*screen_width*mmxr)/2, \
                                                                            screen_width*mmxr, map.size.height/map.size.width*screen_width*mmxr))
            pygame.draw.rect(minimap_surface, color="red", width=0, rect=((jessi.hitbox.x+mx)/map.size.width*screen_width*mmxr, (screen_height*mmyr-map.size.height/map.size.width*screen_width*mmxr)/2+(jessi.hitbox.y+my)/map.size.height*map.size.height/map.size.width*screen_width*mmxr, jessi.hitbox.width/map.size.width*screen_width*mmxr, jessi.hitbox.height/map.size.height*map.size.height/map.size.width*screen_width*mmxr))
        screen.blit(minimap_surface, (screen_width*(1-mmxr)-minimap_gap, screen_height*(1-mmyr)-minimap_gap))


    pygame.draw.rect(screen, color="green", width=1, rect=(jessi.position.rx, jessi.position.ry, jessi.size.width, jessi.size.height))
    # pygame.draw.rect(screen, color="black", width=1, rect=(jessi.hitbox))
    # if turret.summon : pygame.draw.rect(screen, color="black", width=1, rect=(turret.position.rx, turret.position.ry, turret.size.width, turret.size.height))

    if "hp_bar" == "hp_bar" :
        hp_outline_width, hp_outline_height = jessi.size.width*3, jessi.size.height/8
        hp_outline_rect = pygame.Rect(0, 0, hp_outline_width, hp_outline_height)
        hp_outline_rect.center = jessi.hitbox.x + jessi.hitbox.width/2, jessi.hitbox.y - 30
        hp_outline_thickness = 3

        hp_inside_rect = pygame.Rect(0, 0, hp_outline_width * jessi.hp / jessi.max_hp, hp_outline_height)
        hp_inside_rect.topleft = hp_outline_rect.topleft
        pygame.draw.rect(screen, color="red", width=0, rect=hp_inside_rect)
        pygame.draw.rect(screen, color="grey", width=hp_outline_thickness, rect=hp_outline_rect)

    if jessi.hp <= 0 : running = False
    rect_width = 200

    # 라벨링
    label_x, label_y = screen_width - 200, 30
    label_color = "black"
    # mouse_pos = game_font.render("({0},{1})".format(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]), True, "lightgrey")
    # screen.blit(mouse_pos, (pygame.mouse.get_pos()[0]+30, pygame.mouse.get_pos()[1]))
    # jessi_pos_label = game_font.render("({0},{1})".format(round(jessi["position"]["x"]), round(jessi["position"]["y"])), True, "lightgrey")
    # screen.blit(jessi_pos_label, (jessi["position"]["relative"]["x"], jessi["position"]["relative"]["y"] - 30))
    jessi_v_label = game_font.render("x, y : {0} {1}".format(round(jessi.position.x), round(jessi.position.y)), True, label_color)
    screen.blit(jessi_v_label, (label_x, label_y))
    label_y += 30
    jessi_yv_label = game_font.render("jessi v : {}m/s".format((round(jessi.yvelocity, 2))), True, label_color)
    screen.blit(jessi_yv_label, (label_x, label_y))
    label_y += 30
    jessi_xv_label = game_font.render("jessi xv : {}m/s".format((round(jessi.xvelocity,2))), True, label_color)
    screen.blit(jessi_xv_label, (label_x, label_y))
    label_y += 30
    stone_v_label = game_font.render("stone xv : {}m/s".format((round(stone.xvelocity,2))), True, label_color)
    screen.blit(stone_v_label, (label_x, label_y))
    label_y += 30
    stone_theta_label = game_font.render("stone th : {}m/s".format((round(stone.theta,2))), True, label_color)
    screen.blit(stone_theta_label, (label_x, label_y))
    label_y += 30
    stone_tv_label = game_font.render("stone tv : {}m/s".format((round(stone.tvelocity,2))), True, label_color)
    screen.blit(stone_tv_label, (label_x, label_y))
    label_y += 30
    act_label = game_font.render("act : {}".format(jessi.act), True, label_color)
    screen.blit(act_label, (label_x, label_y))
    label_y += 30
    # jump_label = game_font.render("jump : {}".format(jessi["jump"]["indicator"]), True, label_color)
    # screen.blit(jump_label, (label_x, label_y))
    # label_y += 30
    land_label = game_font.render("land : {}".format(jessi.land), True, label_color)
    screen.blit(land_label, (label_x, label_y))
    label_y += 30
    land_label = game_font.render("free : {}".format(jessi.free), True, label_color)
    screen.blit(land_label, (label_x, label_y))
    label_y += 30
    # eball_size_label = game_font.render("({0},{1}), ({2},{3})".format(jessi["weapon"]["eball"]["image"][0].get_rect().size[0], jessi["weapon"]["eball"]["image"][0].get_rect().size[1], \
    #                                                                   jessi["weapon"]["eball"]["image"][1].get_rect().size[0], jessi["weapon"]["eball"]["image"][1].get_rect().size[1]), True, label_color)
    # screen.blit(eball_size_label, (label_x, label_y))
    # label_y += 30

    pygame.display.update()
    pygame.display.set_caption("fps: " + str(clock.get_fps()))

pygame.quit()