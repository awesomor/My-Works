import random
import turtle as t
from random import *
from math import *
import time

x_end = 240
y_end = 340
def right() :
    player.setheading(0)
    if player.xcor() <= x_end :
        player.forward(10)
def left() :
    player.setheading(180)
    if player.xcor() >= -x_end :
        player.forward(10)
def up() :
    player.setheading(90)
    if player.ycor() <= y_end :
        player.forward(10)
def down() :
    player.setheading(270)
    if player.ycor() >= -y_end :
        player.forward(10)
def dash() :
    if player.heading() == 0 :
        if player.xcor() <= x_end:
            player.forward(10)
            player.forward(10)
            player.forward(10)
    elif player.heading() == 180 :
        if player.xcor() >= -x_end:
            player.forward(10)
            player.forward(10)
            player.forward(10)
    elif player.heading() == 90  :
        if player.ycor() <= y_end:
            player.forward(10)
            player.forward(10)
            player.forward(10)
    elif player.heading() == 270 :
        if player.ycor() >= -y_end:
            player.forward(10)
            player.forward(10)
            player.forward(10)
t.bgcolor("yellow")
t.setup(550, 750)

#turtle
player = t.Turtle()
player.shape("turtle")
player.shapesize(2, 2)
player.up()
player.speed(0)
player.goto(0, -270)

#ball_turtle
ball = t.Turtle()
ball.shape("turtle")
ball.shapesize(1.3)
ball.up()
ball.speed(0)
ball.color("white")
#o 원점
o = t.Turtle()
o.shape("circle")
o.shapesize(.01)
o.ht()

t.listen()
t.onkeypress(up, "Up")
t.onkeypress(down, "Down")
t.onkeypress(left, "Left")
t.onkeypress(right, "Right")
t.onkeypress(dash, "d")
# t.onkeypress(shield, "s")

game_on = True

# 점수 표시
fear_distance = 200
dan_distance = 100
safety = 10
dist1, dist2 = 40, 60
side = 100
xs = x_end - side
ys = y_end - side
dan_dash_part = 30
win_dis = 40

while game_on :
    bx = ball.xcor()
    by = ball.ycor()

    px = player.xcor()
    py = player.ycor()
    dis = int(player.distance(ball))
    dir = player.towards(ball)
    abs_dir = o.towards(ball)

    if by > ys or by < -ys or bx > xs or bx < -xs :
        if dis < dan_distance : # 위험 사정거리 안으로 들어왔을 때
            if bx >= xs and by >= ys : # 1사분면 모서리 사각형
                if bx >= px and by >= py : # ball이 player의 1사분면에
                    a = choice([0,1])
                    b = 0
                    if a == 0 :
                        ball.setheading(135+dir/2+int(uniform(-30, 30)))
                        while True :
                            b += 1
                            if  dan_dash_part * sin(radians(ball.heading())) > y_end - by :
                                ball.setheading(180)
                            ball.forward(dan_dash_part)
                            if b == 9 :
                                break
                    elif a == 1 :
                        ball.setheading(270 + dir / 2 + int(uniform(-30, 30)))
                        while True :
                            b += 1
                            if  dan_dash_part * cos(radians(ball.heading())) > x_end - bx :
                                ball.setheading(270)
                            ball.forward(dan_dash_part)
                            if b == 9 :
                                break
                elif bx < px and by >= py :
                    b = 0
                    ball.setheading(dir+uniform(-30, 30))
                    while True :
                        b += 1
                        if dist2 / 4 * sin(radians(ball.heading())) > y_end - by :
                            ball.setheading(180)
                        ball.forward(dist2 / 4)
                        if b == 4 :
                            break
                elif bx >= px and by < py :
                    b = 0
                    ball.setheading(dir+uniform(-30, 30))
                    while True :
                        b += 1
                        if dist2 / 4 * cos(radians(ball.heading())) > x_end - bx :
                            ball.setheading(270)
                        ball.forward(dist2 / 4)
                        if b == 4 :
                            break
                else :
                    ball.setheading(int(uniform(180, 270)))
                    for i in range(4) :
                        ball.forward(dist2 / 4)
            elif bx < -xs and by >= ys : # 2사분면 사각형
                if bx < px and by >= py : # ball이 player의 1사분면에
                    a = choice([0, 1])
                    b = 0
                    if a == 0 :
                        ball.setheading(dir/2-45+int(uniform(-30, 30)))
                        while True :
                            b += 1
                            if  dan_dash_part * sin(radians(ball.heading())) > y_end - by :
                                ball.setheading(0)
                            ball.forward(dan_dash_part)
                            if b == 9 :
                                break
                    elif a == 1 :
                        ball.setheading(180 + dir/2 + int(uniform(-30, 30)))
                        while True :
                            b += 1
                            if  dan_dash_part * - cos(radians(ball.heading())) > x_end + bx :
                                ball.setheading(270)
                            ball.forward(dan_dash_part)
                            if b == 9 :
                                break
                elif bx < px and by < py :
                    b = 0
                    ball.setheading(dir+uniform(-30, 30))
                    while True :
                        b += 1
                        if dist2 / 4 * - cos(radians(ball.heading())) > x_end + bx :
                            ball.setheading(270)
                        ball.forward(dist2 / 4)
                        if b == 4 :
                            break
                elif bx >= px and by >= py :
                    b = 0
                    ball.setheading(dir+uniform(-30, 30))
                    while True :
                        b += 1
                        if dist2 / 4 * sin(radians(ball.heading())) > y_end - by :
                            ball.setheading(0)
                        ball.forward(dist2 / 4)
                        if b == 4 :
                            break
                else :
                    ball.setheading(int(uniform(270, 360)))
                    for i in range(4) :
                        ball.forward(dist2 / 4)
            elif bx < -xs and by < -ys : #3사분면 사각형
                if bx < px and by < py :
                    a = choice([0,1])
                    b = 0
                    if a == 0 :
                        ball.setheading(dir/2+int(uniform(-30, 30)))
                        while True :
                            b += 1
                            if  dan_dash_part * -cos(radians(ball.heading())) > x_end + bx :
                                ball.setheading(90)
                            ball.forward(dan_dash_part)
                            if b == 9 :
                                break
                    elif a == 1 :
                        ball.setheading(dir/2 + 225 + int(uniform(-30, 30)))
                        while True :
                            b += 1
                            if  dan_dash_part * -sin(radians(ball.heading())) > y_end + by :
                                ball.setheading(0)
                            ball.forward(dan_dash_part)
                            if b == 9 :
                                break
                elif bx < px and by >= py :
                    b = 0
                    ball.setheading(dir+uniform(-30, 30))
                    while True :
                        b += 1
                        if dist2 / 4 * - cos(radians(ball.heading())) > x_end + bx :
                            ball.setheading(90)
                        ball.forward(dist2 / 4)
                        if b == 4 :
                            break
                elif bx >= px and by < py :
                    b = 0
                    ball.setheading(dir+uniform(-30, 30))
                    while True :
                        b += 1
                        if dist2 / 4 * -sin(radians(ball.heading())) > y_end + by :
                            ball.setheading(0)
                        ball.forward(dist2 / 4)
                        if b == 4 :
                            break
                else :
                    ball.setheading(int(uniform(0, 90)))
                    for i in range(4) :
                        ball.forward(dist2 / 4)
            elif bx >= xs and by < -ys: # 4사분면 사각형
                if bx >= px and by < py :
                    a = choice([0,1])
                    b = 0
                    if a == 0 :
                        ball.setheading(dir/2 -90 +int(uniform(-30, 30)))
                        while True :
                            b += 1
                            if  dan_dash_part * cos(radians(ball.heading())) > x_end - bx :
                                ball.setheading(90)
                            ball.forward(dan_dash_part)
                            if b == 9 :
                                break
                    elif a == 1 :
                        ball.setheading(315 - dir/2 + int(uniform(-30, 30)))
                        while True :
                            b += 1
                            if  dan_dash_part * -sin(radians(ball.heading())) > y_end + by :
                                ball.setheading(180)
                            ball.forward(dan_dash_part)
                            if b == 9 :
                                break
                elif bx >= px and by >= py :
                    b = 0
                    ball.setheading(dir+uniform(-30, 30))
                    while True :
                        b += 1
                        if dist2 / 4 * cos(radians(ball.heading())) > x_end - bx :
                            ball.setheading(90)
                        ball.forward(dist2 / 4)
                        if b == 4 :
                            break
                elif bx < px and by < py :
                    b = 0
                    ball.setheading(dir+uniform(-30, 30))
                    while True :
                        b += 1
                        if dist2 / 4 * sin(radians(ball.heading())) > y_end + by :
                            ball.setheading(180)
                        ball.forward(dist2 / 4)
                        if b == 4 :
                            break
                else :
                    ball.setheading(int(uniform(90, 180)))
                    for i in range(4) :
                        ball.forward(dist2 / 4)
            elif bx >= xs and abs(by) < ys :
                ball.setheading(dir + uniform(-30, 30))
                if by >= py:
                    ball.setheading(dir + uniform(-45, 45))
                    b = 0
                    while True:
                        b += 1
                        if dist2 / 4 * cos(radians(dist2 / 4)) > x_end - bx:
                            ball.setheading(90)
                        ball.forward(dist2 / 4)
                        if b == 4:
                            break
                if by < py :
                    ball.setheading(dir+uniform(-45, 45))
                    b = 0
                    while True :
                        b += 1
                        if dist2/4 * cos(radians(dist2/4)) > x_end - bx :
                            ball.setheading(270)
                        ball.forward(dist2/4)
                        if b == 4 :
                            break
            elif bx < xs and abs(by) < ys:
                ball.setheading(dir + uniform(-45, 45))
                if by >= py:
                    ball.setheading(dir + uniform(-45, 45))
                    b = 0
                    while True:
                        b += 1
                        if dist2 / 4 * - cos(radians(dist2 / 4)) > x_end + bx:
                            ball.setheading(90)
                        ball.forward(dist2 / 4)
                        if b == 4:
                            break
                if by < py :
                    ball.setheading(dir +uniform(-45, 45))
                    b = 0
                    while True :
                        b += 1
                        if dist2/4 * - cos(radians(dist2/4)) > x_end + bx :
                            ball.setheading(270)
                        ball.forward(dist2/4)
                        if b == 4 :
                            break
            elif by >= ys and abs(bx) < xs:
                ball.setheading(dir + uniform(-45, 45))
                if bx >= px:
                    ball.setheading(dir + uniform(-45, 45))
                    b = 0
                    while True:
                        b += 1
                        if dist2 / 4 * sin(radians(dist2 / 4)) > y_end - by:
                            ball.setheading(0)
                        ball.forward(dist2 / 4)
                        if b == 4:
                            break
                if bx < px :
                    ball.setheading(dir+uniform(-45, 45))
                    b = 0
                    while True :
                        b += 1
                        if dist2/4 * sin(radians(dist2/4)) > y_end - by :
                            ball.setheading(180)
                        ball.forward(dist2/4)
                        if b == 4 :
                            break
            else :
                if bx >= px:
                    ball.setheading(dir + uniform(-45, 45))
                    b = 0
                    while True:
                        b += 1
                        if dist2 / 4 * - sin(radians(dist2 / 4)) > y_end + by:
                            ball.setheading(0)
                        ball.forward(dist2 / 4)
                        if b == 4:
                            break
                if bx < px :
                    ball.setheading(dir+uniform(-45, 45))
                    b = 0
                    while True :
                        b += 1
                        if dist2/4 * - sin(radians(dist2/4)) > y_end + by :
                            ball.setheading(180)
                        ball.forward(dist2/4)
                        if b == 4 :
                            break
        else :
            ball.setheading(uniform(0, 360))
            if bx >= 0 and by >= 0 :
                b = 0
                while True :
                    b += 1
                    if dist1/4 * sin(radians(ball.heading())) > y_end - by and dist1/4 * cos(radians(ball.heading())) > x_end - bx :
                        ball.setheading(uniform(180, 270))
                    if dist1/4 * sin(radians(ball.heading())) > y_end - by :
                        ball.setheading(uniform(180, 360))
                    if dist1/4 * cos(radians(ball.heading())) > x_end - bx :
                        ball.setheading(uniform(90, 270))
                    ball.forward(dist1 / 4)
                    if b == 4 :
                        break
            elif bx < 0 and by >= 0 :
                b = 0
                while True :
                    b += 1
                    if dist1/4 * sin(radians(ball.heading())) > y_end - by and dist1/4 * - cos(radians(ball.heading())) > x_end + bx :
                        ball.setheading(uniform(270, 360))
                    if dist1/4 * sin(radians(ball.heading())) > y_end - by :
                        ball.setheading(uniform(180, 360))
                    if dist1/4 * - cos(radians(ball.heading())) > x_end + bx :
                        ball.setheading(uniform(-90, 90))
                    ball.forward(dist1 / 4)
                    if b == 4 :
                        break
            elif bx < 0 and by < 0 :
                b = 0
                while True :
                    b += 1
                    if dist1/4 * - sin(radians(ball.heading())) > y_end + by and dist1/4 * - cos(radians(ball.heading())) > x_end + bx :
                        ball.setheading(uniform(0, 90))
                    if dist1/4 * (- sin(radians(ball.heading()))) > y_end + by :
                        ball.setheading(uniform(0, 180))
                    if dist1/4 * (- cos(radians(ball.heading()))) > x_end + bx :
                        ball.setheading(uniform(-90, 90))
                    ball.forward(dist1 / 4)
                    if b == 4 :
                        break
            else :
                b = 0
                while True :
                    b += 1
                    if dist1/4 * - sin(radians(ball.heading())) > y_end + by and dist1/4 * cos(radians(ball.heading())) > x_end - bx :
                        ball.setheading(uniform(90, 180))
                    if dist1/4 * (- sin(ball.heading())) > y_end + by :
                        ball.setheading(uniform(0, 180))
                    if dist1/4 * cos(radians(ball.heading())) > x_end - bx :
                        ball.setheading(uniform(90, 270))
                    ball.forward(dist1 / 4)
                    if b == 4 :
                        break
    else :
        if dis < dan_distance :
            ball.setheading(dir + uniform(-45, 45))
            for i in range(4) :
                ball.forward(dist2 / 4)
        else :
            a = int(choice([0] * safety + [dist1]))
            if a != 0 :
                ball.setheading(uniform(0, 360))
            for i in range(4) :
                ball.forward(a / 4)
    if player.distance(ball) < win_dis :
        game_on = False
        t.clear()
        t.goto(0, 0)
        t.write("Win", False, "center", ("", 20))
        player.ht()

    # if abs(ball.xcor()) > x_end :
    #     ball_xspeed *= -1
    # if abs(ball.ycor()) > y_end :
    #     ball_yspeed *= -1
    #
    # if life == 0:
    #     game_on = False
    #     t.goto(0, 0)
    #     t.write("Game Over", False, "center", ("", 20))
    #     player.ht()
    #
    # if player.distance(ball) < 30:
    #     game_on = False
    #     t.clear()
    #     t.goto(0, 0)
    #     t.write("WIN", False, "center", ("", 30))

t.done()


