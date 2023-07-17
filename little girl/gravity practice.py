import pygame
from random import *

pygame.init()
pygame.display.set_caption("Jongin Game")

screen_width = 1440
screen_height = 760
screen = pygame.display.set_mode((screen_width, screen_height))
game_font = pygame.font.Font(None, 40)

# land 생성, ceiling 생성
floor_width, floor_height, ceiling_width, ceiling_height = screen_width, 50, screen_width, 30
floor_start_x, floor_start_y, ceiling_start_x, ceiling_start_y = 0, screen_height -floor_height, 0, 0
# wall 생성
wall_width = 30
wall_left_width, wall_left_height, wall_right_width, wall_right_height = wall_width , screen_height, wall_width , screen_height
wall_left_start_x, wall_left_start_y, wall_right_start_x, wall_right_start_y = 0, 0, screen_width-wall_width,0
# land 생성
land1_h, land2_h, land3_h, land4_h = 150, 250, 350, 450
screen_random_width_lower, screen_random_width_upper = 2,3
land1_width, land1_height = screen_width/uniform(screen_random_width_lower, screen_random_width_upper), 30
land1_start_x, land1_start_y = uniform(wall_width, screen_width-wall_width-land1_width), screen_height-land1_h
land2_width, land2_height = screen_width/uniform(screen_random_width_lower, screen_random_width_upper), 30
land2_start_x, land2_start_y = uniform(wall_width, screen_width-wall_width-land2_width), screen_height-land2_h
land3_width, land3_height = screen_width/uniform(screen_random_width_lower, screen_random_width_upper), 30
land3_start_x, land3_start_y = uniform(wall_width, screen_width-wall_width-land3_width), screen_height-land3_h
land4_width, land4_height = screen_width/uniform(screen_random_width_lower, screen_random_width_upper), 30
land4_start_x, land4_start_y = uniform(wall_width, screen_width-wall_width-land4_width), screen_height-land4_h

character = pygame.image.load("girl.png")
character_r = pygame.transform.flip(character, True, False)
character_l = character
character_size = character.get_rect().size
character_width = character_size[0]
character_height = character_size[1]
character_x_pos = screen_width/2 - character_width/2
character_y_pos = screen_height/2 - character_height/2

character_weight = 40
character_net_force = 0
character_speed = .7
g_coef = 9.8
to_x = 0
clock = pygame.time.Clock()
pygame.key.set_repeat(3)
time_sum = 0
jump = False
jump_time_sum = 0
jump_f = 0
unit = 0.002
def to_meter(cm) : return unit * cm
def to_cm(meter) :return meter / (unit)
time_scale = 1/60
character_v = 0
character_a = 0
jump_height = 150
character_energy = character_weight * g_coef * to_meter(jump_height) # E=15.5232
character_jump_max_speed = (character_energy * 2 / character_weight)**.5  # v0=0.388
beta = - character_jump_max_speed**2/4/jump_height
max_height_time = 2*jump_height/character_jump_max_speed
jump_time = 2 * max_height_time
reaction_f = 0

# 함수들
def pass_line(line) :
    if (character_y_pos + character_height - line) < 0 and(character_y_pos + character_height + to_cm(character_v) * time_scale - line) >= 0: return True
    else : False
def inside_width(left, right) :
    if left<=character_x_pos+character_width*.4<=right or left<=character_x_pos+character_width*.6<=right : return True
    else : return False
def landing(line, left, right) :
    if pass_line(line) and inside_width(left, right) : return True
    else : False




########################### while 반복문 시작 ##############################
running = True
while running :
    dt = clock.tick(60)
    time_sum += time_scale
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_ESCAPE :
                running = False
            # 좌우 방향키
            if event.key == pygame.K_LEFT :
                to_x = - character_speed
                character = character_l
            if event.key == pygame.K_RIGHT:
                to_x = character_speed
                character = character_r
            # 점프 키
            if event.key == pygame.K_SPACE:
                jump = True
        if event.type == pygame.KEYUP :
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT :
                to_x = 0
            if event.key == pygame.K_SPACE :
                jump = False
    # 방향키 이동 실현
    character_x_pos += to_x * dt
    # 좌우 이동범위 제한
    if character_x_pos < wall_width-1/4*character_width :
        character_x_pos = wall_width-1/4*character_width
    elif character_x_pos > screen_width - character_width - wall_width + .2*character_width:
        character_x_pos = screen_width - character_width - wall_width + .2*character_width
    # 객체 사각형 생성
    # character_rect = character.get_rect()
    # character_rect.left = character_x_pos
    # character_rect.top = character_y_pos

    # 점프할 때 가속하는 찰나의 바닥을 미는 힘 가하기
    if jump == True and character_net_force == 0:
        jump_f += - character_weight * character_jump_max_speed / time_scale
        jump = False
        reaction_f = 0

    ## 힘 계산
    character_f = 0
    character_net_force = 0

    character_f += character_weight * g_coef
    character_f += jump_f
    jump_f = 0
    character_net_force += character_f + reaction_f

    # 벽과 붙어있다면 작용하는 반작용
    character_a = character_net_force / character_weight
    character_v += character_a * time_scale
    if landing(screen_height-floor_height, floor_start_x, floor_start_x+floor_width) : # 바닥에 닿을 때
        character_net_force = -character_weight*character_v/time_scale
        character_a = character_net_force / character_weight
        character_v += character_a * time_scale
        character_y_pos = screen_height- floor_height - character_height + 1
        reaction_f = -character_weight * g_coef
    elif landing(land1_start_y, land1_start_x, land1_start_x+land1_width) : # land1에 착지할 때
        character_net_force = -character_weight*character_v/time_scale
        character_a = character_net_force / character_weight
        character_v += character_a * time_scale
        character_y_pos = land1_start_y - character_height + 1
        reaction_f = -character_weight * g_coef
    elif landing(land2_start_y, land2_start_x, land2_start_x + land2_width):  # land2에 착지할 때
        character_net_force = -character_weight * character_v / time_scale
        character_a = character_net_force / character_weight
        character_v += character_a * time_scale
        character_y_pos = land2_start_y - character_height + 1
        reaction_f = -character_weight * g_coef
    elif landing(land3_start_y, land3_start_x, land3_start_x + land3_width):  # land3에 착지할 때
        character_net_force = -character_weight * character_v / time_scale
        character_a = character_net_force / character_weight
        character_v += character_a * time_scale
        character_y_pos = land3_start_y - character_height + 1
        reaction_f = -character_weight * g_coef
    elif landing(land4_start_y, land4_start_x, land4_start_x + land4_width):  # land4에 착지할 때
        character_net_force = -character_weight * character_v / time_scale
        character_a = character_net_force / character_weight
        character_v += character_a * time_scale
        character_y_pos = land4_start_y - character_height + 1
        reaction_f = -character_weight * g_coef
    elif character_y_pos < screen_height - character_height - floor_height and \
            character_net_force == 0:
        if character_y_pos + character_height - 1 == land1_start_y and inside_width(land1_start_x, land1_start_x + land1_width) == False:
            reaction_f = 0
        elif character_y_pos + character_height - 1 == land2_start_y and inside_width(land2_start_x, land2_start_x + land2_width) == False:
            reaction_f = 0
        elif character_y_pos + character_height - 1 == land3_start_y and inside_width(land3_start_x, land3_start_x + land3_width) == False:
            reaction_f = 0
        elif character_y_pos + character_height - 1 == land4_start_y and inside_width(land4_start_x, land4_start_x + land4_width) == False:
            reaction_f = 0

    else :
        character_y_pos += to_cm(character_v) * time_scale # original move

    # 주어진 힘에 의한 가속도에 의한 속도에 의한 이동 계산

    ################ 객체 출력 ##################
    screen.fill("lightgrey")
    wall_color = "#ffdab9"
    pygame.Surface.fill(screen, wall_color, rect = (land1_start_x, land1_start_y, land1_width, land1_height))
    pygame.Surface.fill(screen, wall_color, rect=(land2_start_x, land2_start_y, land2_width, land2_height))
    pygame.Surface.fill(screen, wall_color, rect=(land3_start_x, land3_start_y, land3_width, land3_height))
    pygame.Surface.fill(screen, wall_color, rect=(land4_start_x, land4_start_y, land4_width, land4_height))
    pygame.Surface.fill(screen, wall_color, rect = (ceiling_start_x, ceiling_start_y, ceiling_width, ceiling_height))
    pygame.Surface.fill(screen, wall_color, rect=(floor_start_x, floor_start_y, floor_width, floor_height))
    pygame.Surface.fill(screen, wall_color, rect=(wall_left_start_x, wall_left_start_y, wall_left_width, wall_left_height))
    pygame.Surface.fill(screen, wall_color, rect=(wall_right_start_x, wall_right_start_y, wall_right_width, wall_right_height))

    screen.blit(character, (character_x_pos, character_y_pos))

    timer = game_font.render(str(round(time_sum, 2)), True, (255, 255, 255))
    screen.blit(timer, (10, 10)) # 타이머
    blit_x = 1100
    blit_y = 10
    font_character_net_force = game_font.render("net force : "+ str(round(character_net_force,1)), True, (255, 255, 255))
    screen.blit(font_character_net_force, (blit_x, blit_y)) # 알짜힘

    font_character_v = game_font.render("velocity : "+str(round(character_v, 2)), True, (255, 255, 255))
    screen.blit(font_character_v, (blit_x, blit_y + 30)) # 속도

    font_character_a = game_font.render("accel : "+str(round(character_a, 2)), True, (255, 255, 255))
    screen.blit(font_character_a, (blit_x, blit_y + 60)) # 가속도

    font_character_jts = game_font.render("jump_time_sum : "+str(round(jump_time_sum, 2)), True, (255, 255, 255))
    screen.blit(font_character_jts, (blit_x, blit_y + 90)) # jump time sum

    font_character_jump = game_font.render("jump : "+str(round(jump, 2)),True, (255, 255, 255))
    screen.blit(font_character_jump, (blit_x, blit_y + 120))  # jump 상태

    font_character_reaction = game_font.render("reaction : " + str(round(reaction_f, 2)), True, (255, 255, 255))
    screen.blit(font_character_reaction, (blit_x, blit_y + 150))  # reaction 상태

    pygame.display.update()

pygame.quit()