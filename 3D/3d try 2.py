import pygame
from numpy import *
from random import *
import pandas as pd
import math

pygame.init()
screen_width = 1440
screen_height = 765
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Jongin 3 dimension View")

clock = pygame.time.Clock()
game_font = pygame.font.Font(None, 40)
click_start = 0
click_time = 100


######################### 함수들 #############################
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
    list_a[0], list_a[1], list_a[2] = a[0] * c, a[1] * c, a[2] * c
    return tuple(list_a)
def dir_vector(a, b):
    return unit_vector(tuple_add(b, a, "-"))
def inner_product(a, b):
    product = 0
    for i in range(len(a)):
        product += a[i] * b[i]
    return product
def vertical_vector(o, c, n=1):
    if n == 0 or n == 1:
        return (o[0] + (-1) ** n * (c[0] - o[1]) / len_vector(tuple_add(o, c, "-")),
                o[1] + (-1) ** n * (c[1] - c[0]) / len_vector(tuple_add(o, c, "-")))
    else:
        print("n은 0이나 1을 입력해야합니다.")
def project(p, o):
    a, b, c, x, y, z = o[0], o[1], o[2], p[0], p[1], p[2]
    b_vect = [0] * len(p)
    if c != 0:
        b_vect[2] = (-c * (a * x + b * y) + (a ** 2 + b ** 2) * (z + c) + c ** 3) / (a ** 2 + b ** 2 + c ** 2)
        b_vect[1] = y + b / c * (b_vect[2] - z)
        b_vect[0] = x + a / c * (b_vect[2] - z)
    else:
        b_vect[2] = (a ** 2 + b ** 2) * z / (a ** 2 + b ** 2)
        b_vect[1] = (b ** 3 + a * b * (a - x) + a ** 2 * y) / (a ** 2 + b ** 2)
        b_vect[0] = x + a / b * (b_vect[1] - y)
    return tuple(b_vect)
def perp_unit_vect(p, o, n=0):
    a, b, c, x, y, z = o[0], o[1], o[2], p[0], p[1], p[2]
    len_u = ((c * y - b * z) ** 2 + (a * z - c * x) ** 2 + (b * x - a * y) ** 2) ** .5
    b_vect = [0] * len(p)
    if n == 0 or n == 1:
        b_vect[0] = a + (-1) ** n * (c * y - b * z) / len_u
        b_vect[1] = b + (-1) ** n * (a * z - c * x) / len_u
        b_vect[2] = c + (-1) ** n * (b * x - a * y) / len_u
        return tuple(b_vect)
    else:
        print("n은 0이나 1을 입력하세요")
def project2(p, n, a) :
    p, q, r = p[0], p[1], p[2]
    a, b, c, x1, y1, z1 = n[0], n[1], n[2], a[0], a[1], a[2]
    t = ((a*x1+b*y1+c*z1)-(a*p+b*q+c*r))/(a**2+b**2+c**2)
    b_list = [0] * 3
    b_list[0] = p + a*t
    b_list[1] = q + b*t
    b_list[2] = r + c*t
    return tuple(b_list)

def perp_vector_pos(u, n, a, plus=0) :
    u1, u2, u3, a, b, c = u[0], u[1], u[2], n[0], n[1], n[2]
    d1 = (-1)**plus*(b/(a**2+b**2)**.5)
    d2 = (-1)**plus*(-a/(a**2+b**2)**.5)
    d3 = 0
    d = d1,d2,d3
    return tuple_add(o_proj, d)



A = 3, 3, 0
a, b, c = 1,1,1
main_normal_vector = (a, b, c)
o = 0, 0, 0

wheel_x, wheel_y = 0, 0
wheel_x_sum, wheel_y_sum = 15, 3
wheel_scale = 1 / 20
zoom, zoom_sum = False, 2000
zoom_sum_limit, zoom_scale = 20, 1
scale = zoom_sum * .1
# move_x, move_y = 2, 200
# move_x_start, move_y_start = 0, 0
drag_state, drag_before = 0, 0
move_scale = 1
character_x = 30
character_y = 30
character_z = 0
mouse_x_pos, mouse_y_pos = 0, 0
mouse_x_pos_before, mouse_y_pos_before = 0, 0
mouse_move_x, mouse_move_y = 4000, -550
move_scale = 0.001
z_move_scale = 0.006
to_forward, to_left = 0, 0
move_forward_amount, move_left_amount = .1, .1
vanishing_point = 0, 200
center_x, center_y = 0, 0
center_move_x, center_move_y = 0, 0
center_move_scale = 5

def to_2dim(c,x,y):
    # x0,y0,z0, x1,y1,z1 = A[0],A[1],A[2], c[0],c[1],c[2]
    # t = ((x1-x0)**2+(y1-y0)**2+(z1-z0)**2)**.5
    # x2 = x0 + t*(x1-x0)
    # y2 = y0 + t*(y1-y0)
    # z2 = z0 + t*(z1-z0)
    return inner_product(c, unit_hori_vect) + screen_width  / 2 + x \
        , -inner_product(c, unit_vert_vect) + screen_height / 2 - y
pygame.key.set_repeat(3)

#################################################################################################
#################################################################################################
#################################################################################################
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                zoom = True
            if event.key == pygame.K_w :
                # to_forward += move_forward_amount
                center_move_y = center_move_scale
            if event.key == pygame.K_s :
                # to_forward -= move_forward_amount
                center_move_y = -center_move_scale
            if event.key == pygame.K_a:
                # to_left += move_left_amount
                center_move_x = -center_move_scale
            if event.key == pygame.K_d:
                # to_left -= move_left_amount
                center_move_x = center_move_scale
        if event.type == pygame.MOUSEMOTION :
            mouse_x_pos, mouse_y_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[2] == True :
                if mouse_x_pos > mouse_x_pos_before :
                    mouse_move_x -= 10
                else : mouse_move_x += 10
                if mouse_y_pos < mouse_y_pos_before :
                    mouse_move_y += 10
                else : mouse_move_y -= 10
        if event.type == pygame.MOUSEWHEEL:
            wheel_x = event.x
            # wheel_y = event.y
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                zoom = False
            if event.key == pygame.K_w:
                # to_forward = 0
                center_move_y = 0
            if event.key == pygame.K_s:
                # to_forward = 0
                center_move_y = 0
            if event.key == pygame.K_a:
                # to_left = 0
                center_move_x = 0
            if event.key == pygame.K_d:
                # to_left = 0
                center_move_x = 0
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
            # if drag_state==0 :
            # move_x_start, move_y_start = pygame.mouse.get_pos()
            # drag_state = 1
            # drag_before = 1
        if event.type == pygame.MOUSEBUTTONUP:
            pass
            # drag_state = 0

    # if drag_state == 1:
    #     move_x -= (pygame.mouse.get_pos()[0] - move_x_start) * move_scale
    #     move_y += (pygame.mouse.get_pos()[1] - move_y_start) * move_scale
    #     drag_before = 0
    # move_x_start, move_y_start = pygame.mouse.get_pos()



    z_move_scale1 = z_move_scale
    z_move_scale2 = z_move_scale * 3
    if -500 <= mouse_move_y <= 500 :
        main_normal_vector = 5 * cos(mouse_move_x * move_scale), 5 * sin(mouse_move_x * move_scale),\
                         mouse_move_y * z_move_scale1
    elif mouse_move_y > 500 :
        main_normal_vector = 5 * cos(mouse_move_x * move_scale), 5 * sin(mouse_move_x * move_scale), mouse_move_y * z_move_scale2 - 6
    else : main_normal_vector = 5 * cos(mouse_move_x * move_scale), 5 * sin(mouse_move_x * move_scale), mouse_move_y * z_move_scale2 +6
    main_normal_xy = main_normal_vector[0], main_normal_vector[1]

    # character move
    direction_left = unit_vector((-main_normal_xy[1], main_normal_xy[0],0))
    direction_forward = unit_vector((main_normal_xy[0],main_normal_xy[1],0))
    direction_left_multiply = tuple_multiply(direction_left, to_left)
    direction_forward_multiply = tuple_multiply(direction_forward, to_forward)
    A = tuple_add(tuple_add(A, direction_forward_multiply), direction_left_multiply)

    o = 0, 0, 0
    o_proj = project2(o, main_normal_vector, A)
    z_direct_before = (0, 0, ((a ** 2 + b ** 2 + c ** 2) / (a ** 2 + b ** 2)) ** .5)
    vertical_vector_pos = project2((0, 0, ((a ** 2 + b ** 2 + c ** 2) / (a ** 2 + b ** 2)) **.5),main_normal_vector, A)
    horizon_vector_pos = perp_vector_pos(vertical_vector_pos, main_normal_vector,A,0)
    unit_vert_vect = tuple_add(vertical_vector_pos, o_proj, "-")
    unit_hori_vect = tuple_add(horizon_vector_pos, o_proj, "-")

    center_x += center_move_x
    center_y += center_move_y
    lim = 500
    n = 100
    o_pos, x_end, y_end, z_end = (0, 0, 0), (lim, 0, 0), (0, lim, 0), (0, 0, lim / 1.5)
    x_start, y_start, z_start = (-lim, 0, 0), (0, -lim, 0), (0, 0, -lim / 3)
    o_2dim = to_2dim(o_pos,center_x,center_y)
    x_2dim, y_2dim, z_2dim = to_2dim(x_end,center_x,center_y), to_2dim(y_end,center_x,center_y), to_2dim(z_end,center_x,center_y)
    x_start_2dim, y_start_2dim, z_start_2dim = to_2dim(x_start, center_x, center_y), to_2dim(y_start, center_x, center_y), to_2dim(z_start, center_x, center_y)

    # 반구 중점, 반지름, 세 요소 벡터
    # globe_center_pos = 3,3,10
    # globe_r = 3
    # Ao_vect = tuple_add(A,globe_center_pos, "-")
    # a_vect = tuple_add((project2((0, 0, ((Ao_vect[0]**2+Ao_vect[1]**2+Ao_vect[2]**2)/(Ao_vect[0]**2+Ao_vect[1]**2))**.5),Ao_vect,globe_center_pos)),globe_center_pos, "-")
    # b_vect = tuple_add(perp_vector_pos(a_vect, Ao_vect, globe_center_pos), o_proj,"-")
    # c_vect = unit_vector(tuple_add(A, globe_center_pos,"-"))

    mouse_x_pos_before, mouse_y_pos_before = pygame.mouse.get_pos()

    # 레이블
    screen.fill("lightgrey")
    label_x = 1100
    label_y = 10
    wheel_y_label = game_font.render("wheel y sum : " + str(int(wheel_y_sum)), True, (255, 255, 255))
    screen.blit(wheel_y_label, (label_x, label_y))
    label_y += 30
    wheel_amount_label = game_font.render("wheel x sum : " + str(int(wheel_x_sum)), True, (255, 255, 255))
    screen.blit(wheel_amount_label, (label_x, label_y))
    label_y += 30
    normal_label = game_font.render(
        "({0}, {1}, {2})".format(round(main_normal_vector[0], 2), round(main_normal_vector[1], 2),
                                 round(main_normal_vector[2], 2)), True, (255, 255, 255))
    screen.blit(normal_label, (label_x, label_y))
    label_y += 30
    zoom_label = game_font.render("zoom  : " + str(int(zoom)), True, (255, 255, 255))
    screen.blit(zoom_label, (label_x, label_y))
    label_y += 30
    zoom_sum_label = game_font.render("zoom sum  : " + str(int(zoom_sum)), True, (255, 255, 255))
    screen.blit(zoom_sum_label, (label_x, label_y))
    label_y += 30
    scale_label = game_font.render("scale  : " + str(int(scale)), True, (255, 255, 255))
    screen.blit(scale_label, (label_x, label_y))
    label_y += 30
    A_point = game_font.render("({0},{1},{2})".format(round(A[0],2),round(A[1],2),round(A[2],2)), True, (255, 255, 255))
    screen.blit(A_point, (label_x, label_y))
    label_y += 30
    mouse_move_x_label = game_font.render("mouse move x  : " + str(int(mouse_move_x)), True, (255, 255, 255))
    screen.blit(mouse_move_x_label, (label_x, label_y))
    label_y += 30

    ## 3차원 좌표의 2차원 사영


    # for i in range(n):
    #     pygame.draw.line(screen, "purple", to_2dim((lim / (n) * (i + 1), 0, 0),A,center_x,center_y), to_2dim((lim / n * (i + 1), lim, 0),A,center_x,center_y), width=1)
    #     pygame.draw.line(screen, "purple", to_2dim((0, lim / n * (i + 1), 0),A,center_x,center_y),to_2dim((lim, lim / n * (i + 1), 0),A,center_x,center_y), width=1)
    #     pygame.draw.line(screen, "red", to_2dim((lim/n*i,0,0),A,center_x,center_y), to_2dim((lim/n*(i+1),0,0),A,center_x,center_y), width=3)  # x축
    #     pygame.draw.line(screen, "blue", to_2dim((0, lim / n * i, 0), A, center_x, center_y),
    #                      to_2dim((0, lim / n * (i + 1), 0), A, center_x, center_y), width=3)  # y축
    #     pygame.draw.line(screen, "green", to_2dim((0, 0, lim / n * i), A, center_x, center_y),
    #                      to_2dim((0, 0, lim / n * (i + 1)), A, center_x, center_y), width=3)  # z축

    # for k in range(4):
    #     a_vect_loop = tuple_multiply(a_vect, round(cos(pi / 4 + pi / 2 * k) * 2 ** .5))
    #     b_vect_loop = tuple_multiply(b_vect, round(sin(pi / 4 + pi / 2 * k) * 2 ** .5))
    #     c_vect_loop = c_vect
    #     n = 5
    #     for i in range(1,n+1) :
    #         for j in range(1, n+1):
    #             if j/n*globe_r < (globe_r ** 2 - (i / n * globe_r) ** 2) ** .5:
    #                 p1 = tuple_add(tuple_add(globe_center_pos, tuple_multiply(a_vect_loop,(i-1)/n*globe_r)), tuple_add(tuple_multiply(b_vect_loop,(j-1)/n*globe_r), tuple_multiply(c_vect_loop,(globe_r**2-((i-1)/n)**2-((j-1)/n)**2)**.5)))
    #                 p2 = tuple_add(tuple_add(globe_center_pos, tuple_multiply(a_vect_loop, (i - 1) / n * globe_r)), tuple_add(tuple_multiply(b_vect_loop, (j) / n * globe_r), tuple_multiply(c_vect_loop, (globe_r ** 2 - ((i - 1) / n) ** 2 - ((j) / n) ** 2) ** .5)))
    #                 p3 = tuple_add(tuple_add(globe_center_pos, tuple_multiply(a_vect_loop, (i) / n * globe_r)), tuple_add(tuple_multiply(b_vect_loop, (j) / n * globe_r), tuple_multiply(c_vect_loop, (globe_r ** 2 - ((i) / n) ** 2 - ((j) / n) ** 2) ** .5)))
    #                 p4 = tuple_add(tuple_add(globe_center_pos, tuple_multiply(a_vect_loop, (i) / n * globe_r)), tuple_add(tuple_multiply(b_vect_loop, (j-1) / n * globe_r), tuple_multiply(c_vect_loop, (globe_r ** 2 - ((i) / n) ** 2 - ((j-1) / n) ** 2) ** .5)))
    #                 pygame.draw.polygon(screen, "black", (to_2dim(p1, A, center_x, center_y),to_2dim(p2, A, center_x, center_y),to_2dim(p3, A, center_x, center_y),to_2dim(p4, A, center_x, center_y)), True)
    tri_size = 20
    x_tri1, x_tri2, x_tri3 = tuple_add(x_end,(0,tri_size/2,0)),tuple_add(x_end,(0,-tri_size/2,0)),tuple_add(x_end,(tri_size*(3**.5/2),0,0))
    y_tri1, y_tri2, y_tri3 = tuple_add(y_end, (tri_size / 2,0, 0)), tuple_add(y_end, ( -tri_size / 2,0, 0)), tuple_add(y_end, (0, tri_size * (3 ** .5 / 2), 0))
    z_tri1, z_tri2, z_tri3 = tuple_add(z_end, (0, tri_size / 2, 0)), tuple_add(z_end, (0, -tri_size / 2, 0)), tuple_add(z_end, (0, 0,tri_size * (3 ** .5 / 2)))
    x_tri1_2dim, x_tri2_2dim, x_tri3_2dim = to_2dim(x_tri1,center_x, center_y), to_2dim(x_tri2,center_x, center_y), to_2dim(x_tri3,center_x, center_y)
    y_tri1_2dim, y_tri2_2dim, y_tri3_2dim = to_2dim(y_tri1, center_x, center_y), to_2dim(y_tri2, center_x, center_y), to_2dim(y_tri3, center_x, center_y)
    z_tri1_2dim, z_tri2_2dim, z_tri3_2dim = to_2dim(z_tri1, center_x, center_y), to_2dim(z_tri2, center_x, center_y), to_2dim(z_tri3, center_x, center_y)

    lines_n = 50
    if main_normal_vector[2] <= 0 :
        lines_color = "white"
    else : lines_color = "black"
    for i in range(1, lines_n) :
        lines_x_start_plus = tuple_add(x_start, (0,lim/lines_n*i,0))
        lines_x_start_minus = tuple_add(x_start, (0, -lim / lines_n * i, 0))
        lines_y_start_plus = tuple_add(y_start, (lim / lines_n * i,0,0))
        lines_y_start_minus = tuple_add(y_start, (-lim / lines_n * i,0,0))
        lines_x_end_plus = tuple_add(x_end, (0, lim / lines_n * i, 0))
        lines_x_end_minus = tuple_add(x_end, (0, -lim / lines_n * i, 0))
        lines_y_end_plus = tuple_add(y_end, (lim / lines_n * i, 0, 0))
        lines_y_end_minus = tuple_add(y_end, (-lim / lines_n * i, 0, 0))
        pygame.draw.line(screen, lines_color, to_2dim(lines_x_start_plus,center_x, center_y), to_2dim(lines_x_end_plus,center_x,center_y) , width=3)
        pygame.draw.line(screen, lines_color, to_2dim(lines_x_start_minus, center_x, center_y), to_2dim(lines_x_end_minus, center_x, center_y), width=3)
        pygame.draw.line(screen, lines_color, to_2dim(lines_y_start_plus, center_x, center_y), to_2dim(lines_y_end_plus, center_x, center_y), width=3)
        pygame.draw.line(screen, lines_color, to_2dim(lines_y_start_minus, center_x, center_y), to_2dim(lines_y_end_minus, center_x, center_y), width=3)

    pygame.draw.line(screen, "red", x_start_2dim, x_2dim, width=3)  # x축
    pygame.draw.line(screen, "blue", y_start_2dim, y_2dim, width=3)  # y축
    pygame.draw.line(screen, "green", z_start_2dim, z_2dim, width=3)  # z축

    pygame.draw.lines(screen, "red", True, (x_tri1_2dim,x_tri2_2dim,x_tri3_2dim), width=3)
    pygame.draw.lines(screen, "blue", True, (y_tri1_2dim, y_tri2_2dim, y_tri3_2dim), width=3)
    pygame.draw.lines(screen, "green", True, (z_tri1_2dim, z_tri2_2dim, z_tri3_2dim), width=3)


    pygame.draw.circle(screen, "black", o_2dim, 3, 25)
    # pygame.draw.circle(screen, "black", to_2dim((10,10,5),A,center_x, center_y), 50, 5)
    pygame.display.update()
pygame.quit()