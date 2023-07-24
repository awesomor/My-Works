import pygame
import numpy as np
from math import *

pygame.init()

pygame.display.set_caption("3 dimension")
screen_width, screen_height = 1440, 760
# screen_width, screen_height = 2048, 1092
# screen_width, screen_height = 2048, 9R90
# screen_width, screen_height = 2560, 960

screen = pygame.display.set_mode((screen_width, screen_height))
game_font = pygame.font.Font(None, 30)

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
def tuple_multiply(a, c):
    list_a = list(a)
    for i in range(len(a)) :
        list_a[i] = a[i]*c
    return tuple(list_a)
def len_vector(v):
    len_v = 0
    for i in range(len(v)):
        len_v += v[i] ** 2
    return len_v ** .5
def unit_vector(v):
    unit_v = [0] * len(v)
    if len_vector(v) == 0 :
        return tuple(unit_v)
    else :
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

g=9.8

cc = (30, 30, 10)
u = unit_vector((-1, -1, 0))
v6 = unit_vector((-u[1], u[0], 0))

move_forward = 0
move_backward = 0
move_left = 0
move_right = 0
move_speed = .3

mouse = {}
mouse["click"] = {"btn1":{"on":False, "off":False}, "btn2":{"on":False, "off":False}}
mouse["position"] = {"x":-1, "y":-1}
mouse["position"]["indicator"] = False
theta1, theta2 = 0, 0
theta1_scale, theta2_scale = 2*pi/360/200, 2*pi/360/400


t = 0
dt = 1/60
pygame.key.set_repeat(3)
clock = pygame.time.Clock()
running = True
while running :
    clock.tick(60)
    t += 1
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_ESCAPE :
                running = False
            if event.key == pygame.K_w:
                move_forward = move_speed
            if event.key == pygame.K_s:
                move_backward = move_speed
            if event.key == pygame.K_a:
                move_left = move_speed
            if event.key == pygame.K_d:
                move_right = move_speed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                move_forward = 0
            if event.key == pygame.K_s:
                move_backward = 0
            if event.key == pygame.K_a:
                move_left = 0
            if event.key == pygame.K_d:
                move_right = 0
        if event.type == pygame.MOUSEBUTTONDOWN :
            if event.button == 3:
                mouse["click"]["btn2"]["on"] = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                # mouse["click"]["btn2"]["off"] = True
                mouse["position"]["indicator"] = False
                mouse["position"]["x"], mouse["position"]["y"] = tuple_add(pygame.mouse.get_pos(), (theta1, theta2),"-")
    screen.fill("white")

    cc = tuple_add( cc,tuple_multiply(unit_vector((u[0],u[1],0)), move_forward))
    cc = tuple_add(cc, tuple_multiply(unit_vector((u[0],u[1],0)), -move_backward))
    cc = tuple_add( cc,tuple_multiply(v6, move_left))
    cc = tuple_add( cc,tuple_multiply(v6, -move_right))

    if mouse["click"]["btn2"]["on"] == True :
        mouse["click"]["btn2"]["on"] = False
        mouse["position"]["x"], mouse["position"]["y"] = pygame.mouse.get_pos()
        mouse["position"]["indicator"] = True
    if mouse["position"]["indicator"] == True :
        theta1 = (pygame.mouse.get_pos()[0] - mouse["position"]["x"]) * -theta1_scale
        if theta2 > pi/6 :
            theta2 = pi/6
        elif theta2 < -pi/6 :
            theta2 = -pi/6
        else :
            theta2 = (pygame.mouse.get_pos()[1] - mouse["position"]["y"]) * -theta2_scale
        sinpi = u[2]
        cospi = (1-u[2]**2)**.5
        sinth = u[1]/cospi
        costh = u[0]/cospi
        u = (cospi*cos(theta2)-sinpi*sin(theta2))*(costh*cos(theta1)-sinth*sin(theta1)),\
        (cospi*cos(theta2)-sinpi*sin(theta2))*(sinth*cos(theta1)+costh*sin(theta1)),\
        sinpi*cos(theta2) + cospi*sin(theta2)

    u_amount = .3
    uu = tuple_multiply(u, u_amount)
    unit_height_half = u_amount/2
    unit_width_half = unit_height_half * (screen_width / screen_height)
    # uup, uuq, uur = uu[0], uu[1], uu[2]
    # if uur == 0 :
    #     uuabc = 0, 0, 1
    # elif uup == 0 :
    #     uuabc = 0, -uur, uuq
    # elif uuq == 0 :
    #     uuabc = -uur, 0, uup
    # else :
    #     uuabc = -(uup*uur)/(uup**2+uuq**2), -(uuq*uur)/(uup**2+uuq**2), 1
    sinpi = u[2]
    cospi = (1 - u[2] ** 2) ** .5
    sinth = u[1] / cospi
    costh = u[0] / cospi
    v5 = -sinpi*costh, -sinpi*sinth, cospi
    vv5 = tuple_multiply(v5, unit_height_half)
    vv5m = tuple_multiply(v5, -unit_height_half)
    v6 = unit_vector((-u[1], u[0], 0))
    vv6 = tuple_multiply(v6, unit_width_half)
    vv6m = tuple_multiply(v6, -unit_width_half)
    v1 = ( tuple_add( tuple_add(vv5, vv6), uu) )
    v2 = ( tuple_add( tuple_add(vv5m, vv6), uu) )
    v3 = ( tuple_add( tuple_add(vv5m, vv6m), uu) )
    v4 = ( tuple_add( tuple_add(vv5, vv6m), uu) )

    u1 = unit_vector(v1)
    u2 = unit_vector(vv6m)
    u3 = unit_vector(vv5m)
    umt = np.array((u1, u2, u3))
    umt_inv = np.linalg.inv(umt)
    point = 1, 2, 3
    point = tuple_add(point, cc, "-")
    p_array = np.array(point)
    p_pqr = np.dot(umt_inv, p_array)
    pmw = p_pqr[0] * 72 / 3101 ** .5
    pmh = p_pqr[0] * 38 / 3101 ** .5

    for i in range(-1000, 1000):
        for j in range(3) :
            color = ["red","blue","green"]
            ii = [0]*3
            ii[j] = i/10
            point = tuple_add(ii, cc, "-")
            pp = np.dot(umt_inv, np.array(point))
            if abs(pp[0]) > 200 :
                continue
            ppmw = pp[0] * 72 / 3101 ** .5
            ppmh = pp[0] * 38 / 3101 ** .5
            if (pp[0] >= 0 and 0 <= pp[1] <= ppmw and 0 <= pp[2] <= ppmh) == False :
                continue
            else :
                xx = pp[1]/ppmw * screen_width
                yy = pp[2]/ppmh * screen_height
                if ii == [0,0,0] :
                    pygame.draw.circle(screen, "black", (xx, yy), 5, 3)
                elif pp[0] <30 :
                    pygame.draw.circle(screen, color[j], (xx, yy), 10, 1)
                elif pp[0] <50 :
                    pygame.draw.circle(screen, color[j], (xx, yy), 5, 1)
                elif pp[0] < 100 :
                    pygame.draw.circle(screen, color[j], (xx, yy), 3, 1)
                elif pp[0] < 300 :
                    pygame.draw.circle(screen, color[j], (xx, yy), 1, 1)
                else : pygame.draw.circle(screen, color[j], (xx, yy), 1, 1)








    label_x, label_y = 1100, 30
    label_color = "black"
    mouse_pos = game_font.render("({0},{1})".format(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]), True, "lightgrey")
    screen.blit(mouse_pos, (pygame.mouse.get_pos()[0]+30, pygame.mouse.get_pos()[1]))
    label = game_font.render("label {}".format(1000), True, label_color)
    screen.blit(label, (label_x, label_y))
    label_y += 30
    u_label = game_font.render("uv {}".format((round(u[0],2),round(u[1],2),round(u[2],2))), True, label_color)
    screen.blit(u_label, (label_x, label_y))
    label_y += 30
    cc_label = game_font.render("cc {}".format((round(cc[0], 2), round(cc[1], 2), round(cc[2], 2))), True, label_color)
    screen.blit(cc_label, (label_x, label_y))
    label_y += 30

    pygame.display.update()

# 3차원 입체 뷰
# import pygame
# from math import *
#
# pygame.init()
#
# pygame.display.set_caption("physics")
# screen_width, screen_height = 1440, 760
# # screen_width, screen_height = 2048, 1092
# # screen_width, screen_height = 2048, 990
# # screen_width, screen_height = 2560, 960
#
# screen = pygame.display.set_mode((screen_width, screen_height))
# game_font = pygame.font.Font(None, 30)
#
# def tuple_add(a, b, operation="+"):
#     if operation == "+":
#         o = 1
#     elif operation == "-":
#         o = -1
#     else:
#         print("연산자 오류, + - 중 입력하시오")
#     list_c = [0] * len(a)
#     for i in range(len(a)):
#         list_c[i] = list(a)[i] + o * list(b)[i]
#     return tuple(list_c)
# def tuple_multiply(a, c):
#     list_a = list(a)
#     for i in range(len(a)) :
#         list_a[i] = a[i]*c
#     return tuple(list_a)
# def len_vector(v):
#     len_v = 0
#     for i in range(len(v)):
#         len_v += v[i] ** 2
#     return len_v ** .5
# def unit_vector(v):
#     unit_v = [0] * len(v)
#     if len_vector(v) == 0 :
#         return tuple(unit_v)
#     else :
#         for i in range(len(v)):
#             unit_v[i] = v[i] / len_vector(v)
#         return tuple(unit_v)
# def tuple_multiply(a, c):
#     list_a = list(a)
#     for i in range(len(a)) :
#         list_a[i] = a[i]*c
#     return tuple(list_a)
# def inner_product(a, b):
#     product = 0
#     for i in range(len(a)):
#         product += a[i] * b[i]
#     return product
#
# g=9.8
#
# cc = (30, 30, 30)
# u = unit_vector((-1, -1, -1))
# v6 = unit_vector((-u[1], u[0], 0))
#
# move_forward = 0
# move_backward = 0
# move_left = 0
# move_right = 0
# move_speed = 1
#
# mouse = {}
# mouse["click"] = {"btn1":{"on":False, "off":False}, "btn2":{"on":False, "off":False}}
# mouse["position"] = {"x":-1, "y":-1}
# theta1, theta2 = 0, 0
# theta1_scale, theta2_scale = 2*pi/360/100, 2*pi/360/100
#
#
# t = 0
# dt = 1/60
# pygame.key.set_repeat(3)
# clock = pygame.time.Clock()
# running = True
# while running :
#     clock.tick(60)
#     t += 1
#     for event in pygame.event.get() :
#         if event.type == pygame.QUIT :
#             running = False
#         if event.type == pygame.KEYDOWN :
#             if event.key == pygame.K_ESCAPE :
#                 running = False
#             if event.key == pygame.K_w:
#                 move_forward = move_speed
#             if event.key == pygame.K_s:
#                 move_backward = move_speed
#             if event.key == pygame.K_a:
#                 move_left = move_speed
#             if event.key == pygame.K_d:
#                 move_right = move_speed
#         if event.type == pygame.KEYUP:
#             if event.key == pygame.K_w:
#                 move_forward = 0
#             if event.key == pygame.K_s:
#                 move_backward = 0
#             if event.key == pygame.K_a:
#                 move_left = 0
#             if event.key == pygame.K_d:
#                 move_right = 0
#         if event.type == pygame.MOUSEBUTTONDOWN :
#             if event.button == 3:
#                 mouse["click"]["btn2"]["on"] = True
#         if event.type == pygame.MOUSEBUTTONUP:
#             if event.button == 3:
#                 # mouse["click"]["btn2"]["off"] = True
#                 mouse["position"]["x"], mouse["position"]["y"] = -1, -1
#
#     cc = tuple_add( cc,tuple_multiply(u, move_forward))
#     cc = tuple_add(cc, tuple_multiply(u, -move_backward))
#     cc = tuple_add( cc,tuple_multiply(v6, move_left))
#     cc = tuple_add( cc,tuple_multiply(v6, -move_right))
#
#     if mouse["click"]["btn2"]["on"] == True :
#         mouse["click"]["btn2"]["on"] = False
#         mouse["position"]["x"], mouse["position"]["y"] = pygame.mouse.get_pos()
#     if 0 <= mouse["position"]["x"] <= screen_width and 0 <= mouse["position"]["y"] <= screen_height :
#         theta1 = (pygame.mouse.get_pos()[0] - mouse["position"]["x"]) * theta1_scale
#         theta2 = (pygame.mouse.get_pos()[1] - mouse["position"]["y"]) * theta2_scale
#         if sin(-theta2) < sin(-pi/6) :
#             u = cos(theta2)*cos(theta1)*u[0]+sin(theta1)*u[1], -cos(theta2)*sin(theta1)*u[0]+cos(theta1)*u[1], sin(-pi/6)
#         elif sin(-theta2) > sin(pi/6) :
#             u = cos(theta2) * cos(theta1) * u[0] + sin(theta1) * u[1], -cos(theta2) * sin(theta1) * u[0] + cos(theta1) * u[1], sin(pi / 6)
#         else :
#             u = cos(theta2) * cos(theta1) * u[0] + sin(theta1) * u[1], -cos(theta2) * sin(theta1) * u[0] + cos(theta1) * u[1], u[2] + sin(-theta2)
#
#     u_amount = .3
#     uu = tuple_multiply(u, u_amount)
#     unit_height_half = u_amount/2
#     unit_width_half = unit_height_half * (screen_width / screen_height)
#     v5 = -sin(theta2)*cos(theta1), -sin(theta2)*sin(theta1), cos(theta2)
#     vv5 = tuple_multiply(v5, unit_height_half)
#     vv5m = tuple_multiply(v5, -unit_height_half)
#     v6 = unit_vector((-u[1], u[0], 0))
#     vv6 = tuple_multiply(v6, unit_width_half)
#     vv6m = tuple_multiply(v6, -unit_width_half)
#     v1 = ( tuple_add( tuple_add(vv5, vv6), uu) )
#     v2 = ( tuple_add( tuple_add(vv5m, vv6), uu) )
#     v3 = ( tuple_add( tuple_add(vv5m, vv6m), uu) )
#     v4 = ( tuple_add( tuple_add(vv5, vv6m), uu) )
#
#     screen.fill("white")
#     end_point = 200
#     for i in range(1, end_point):
#         for j in range(3):
#             for j2 in range(2):
#                 for j3 in range(11):
#                     meet = False
#                     x0, y0, z0 = tuple_add(cc,tuple_multiply(u,u_amount*i) )
#                     vv5i = tuple_multiply( v5, unit_height_half*i)
#                     vv5mi = tuple_multiply( v5, -unit_height_half * i)
#                     vv6i = tuple_multiply( v6, unit_width_half*i)
#                     vv6mi = tuple_multiply( v6, -unit_width_half * i)
#                     a, b, c = u
#                     d = a*x0 + b*y0 + c*z0
#                     efg = [0]*3
#                     efg[j2] = 5-j3
#                     x1, y1, z1 = tuple(efg) ## x축, y축, z축이 지나는 점이기 때문
#                     efg2 = [0]*3
#                     efg2[j] = 1
#                     e, f, g = tuple(efg2)
#
#                     if a*e + b*f + c*g == 0 :
#                         meet = False
#                     else :
#                         k = (d - a*x1 - b*y1 - c*z1)/(a*e + b*f + c*g)
#                         meet = True
#
#                     x, y, z = k*e + x1, k*f + y1, k*g + z1
#
#                     x2, y2, z2 = x, y, z
#                     x3, y3, z3 = tuple_add((x0,y0,z0), tuple_add(vv5i, vv6i))
#                     x4, y4, z4 = tuple_add((x0,y0,z0), tuple_add(vv5i, vv6mi))
#
#                     if z0 - len_vector(vv5i) <= z <= z0 + len_vector(vv5i) and meet == True:
#                         l, m, n = vv6mi
#                         if l == 0 :
#                             k23, k24 = (y3-y2)/m, (y4-y2)/m
#                         elif m == 0 :
#                             k23, k24 = (x3-x2)/l, (x4-x2)/l
#                         else :
#                             k23, k24 = ((x3-x2)-(y3-y2))/(l-m),((x4-x2)-(y4-y2))/(l-m)
#
#                         if k23 * k24 <= 0 :
#                             v1ip = tuple_add((x0, y0, z0), tuple_add(vv5i, vv6i))
#                             rxyz = tuple_add((x,y,z), v1ip, "-")
#                             rux = tuple_multiply( unit_vector(vv6m), screen_width/(len_vector(vv6i)*2))
#                             ruy = tuple_multiply( unit_vector(vv5m), screen_height/(len_vector(vv5i)*2))
#                             pos =  inner_product(rux,rxyz), inner_product(ruy, rxyz)
#                             if x1 == 0 and y1 == 0 :
#                                 pygame.draw.circle(screen, "black", pos,1,  1)
#                             elif j != 2:
#                                 pygame.draw.circle(screen, "grey", pos, 1, 1)
#
#     label_x, label_y = 1100, 30
#     label_color = "black"
#     mouse_pos = game_font.render("({0},{1})".format(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]), True, "lightgrey")
#     screen.blit(mouse_pos, (pygame.mouse.get_pos()[0]+30, pygame.mouse.get_pos()[1]))
#     label = game_font.render("label {}".format(1000), True, label_color)
#     screen.blit(label, (label_x, label_y))
#     label_y += 30
#
#     pygame.display.update()

# 직사각형 돌리기
# 직사각형 돌리기
# f, a, v = 0, 0, 0
# s = [0, 0]
# o = []
# vv = [0]
# ll = [0]
# aa = [0]
# ff = [0]
# dd = []
# rdd = [(0,0)]
# nff = [0]
# scale = 1000
# mouse_scale = 70000
# dt = 1/60
# theta = 0
# t = -15
# friction = .002
# pygame.key.set_repeat(3)
# clock = pygame.time.Clock()
# running = True
# while running :
#     clock.tick(60)
#     # t += 1
#     for event in pygame.event.get() :
#         if event.type == pygame.QUIT :
#             running = False
#         if event.type == pygame.KEYDOWN :
#             if event.key == pygame.K_ESCAPE :
#                 running = False
#             if event.key == pygame.K_a :
#                 pass
#
#
#
#     c, b = 80, 400
#     w = 80
#     r = b-c/2
#     g = 9.8
#     rfv = tuple_multiply(rdd[-1], -ff[-1])
#     fgv = 0, w*g*(1-c/b)
#
#     f = inner_product(tuple_add(rfv, fgv),(sin(theta),cos(theta)))
#     a = f / w
#     v += a * dt
#     if v > 0 :
#         v -= friction
#     elif v < 0 :
#         v += friction
#
#     theta += v * dt / r * scale
#
#     # t = -60*theta/pi-15
#     o.append(pygame.mouse.get_pos())
#     if len(o) >= 2 :
#         ll.append(len_vector(tuple_add(o[-1], o[-2],"-"))/mouse_scale)
#         vv.append(ll[-1]/dt)
#         aa.append(vv[-1]/dt)
#         ff.append(aa[-1]*w)
#         dd.append(unit_vector(tuple_add(o[-1], o[-2],"-")))
#         rdd.append(tuple_multiply(dd[-1],-1))
#         nff.append( inner_product(tuple_multiply(rdd[-1],ff[-1]), (sin(theta),cos(theta))) )
#
#     s[0] = o[-1][0] - r*cos(theta)
#     s[1] = o[-1][1] + r*sin(theta)
#     v6 = tuple_add(s, o[-1], "-")
#     v7 = unit_vector((-v6[1], v6[0]))
#     v8 = tuple_multiply(v7, c/2)
#     v9 = tuple_multiply(v7, -c / 2)
#     v1 = tuple_add(v6, v8)
#     v2 = tuple_add(v6, v9)
#     v10 = tuple_multiply(unit_vector(v6), -c/2)
#     v3 = tuple_add(v9, v10)
#     v4 = tuple_add(v8, v10)
#
#     a1 = tuple_add(o[-1], v1)
#     a2 = tuple_add(o[-1], v2)
#     a3 = tuple_add(o[-1], v3)
#     a4 = tuple_add(o[-1], v4)
#
#     screen.fill("white")
#
#     pygame.draw.lines(screen, "black", True, (a1, a2, a3, a4))
#     # pygame.draw.lines(screen, "black", True, (v1, v2, v3, v4))
#
#
#     label_x, label_y = 1100, 30
#     label_color = "black"
#     mouse_pos = game_font.render("({0},{1})".format(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]), True, "lightgrey")
#     screen.blit(mouse_pos, (pygame.mouse.get_pos()[0]+30, pygame.mouse.get_pos()[1]))
#     label = game_font.render("label {}".format(1000), True, label_color)
#     screen.blit(label, (label_x, label_y))
#     label_y += 30
#
#     pygame.display.update()
