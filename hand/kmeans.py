import cv2
import numpy
import pygame
import random

def kmeans(cluster=8, iteration=12, data=None):
    global center
    center = numpy.ones(shape=(5, cluster))
    for i in range(cluster):
        col = [random.randint(0, screen_height), random.randint(0, screen_width), 0, 0, 0]
        col[2:5] = frame[col[0], col[1]]
        center[:,i] = col
    onen = numpy.ones(shape=(screen_width*screen_height, 1), dtype=int)

    distance = numpy.ones(shape=(screen_width*screen_height, cluster), dtype=int)

    data[:, 2:5] = data[:, 2:5] * ratio

    for repeat in range(iteration):
        for i in range(cluster):
            col = numpy.ones(shape=(5, 1))
            col[:, 0] = center[:,i]
            A = data[:, 0:5] - numpy.dot(col, onen.transpose()).transpose()
            A = A ** 2
            distance[:, i] = A[:,0] + A[:,1] + A[:,2] + A[:,3] + A[:,4]

        new_column = numpy.argmin(distance, axis=1)
        data[:, 5] = new_column

        for i in range(cluster):
            center[:, i] = data[data[:, 5] == i][:,0:5].mean(axis=0)



pygame.init()
screen_width, screen_height = 1920, 1080
screen_width, screen_height = 1280, 720
capture = cv2.VideoCapture(1)
centers = 5
divide = 1
trial = 0
# capture.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
# capture.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)
X = numpy.ndarray(shape=(screen_width*screen_height, 6), dtype=int)
for i in range(screen_height):
    for j in range(screen_width):
        X[trial, 0], X[trial, 1] = i, j
        trial += 1


while cv2.waitKey(33) < 0:
    ret, frame = capture.read()
    frame = cv2.flip(frame, 1)

    trial = 0
    ratio = 20

    X[:, 2:5] = (frame.reshape(-1, 3))
    kmeans(cluster=centers, iteration=2, data=X)

    frame = numpy.ones(frame.shape, numpy.uint8) * 0

    for x in range(int(X.shape[0] / divide)):
        i, j = X[x * divide, 0], X[x * divide, 1]
        cluster = int(X[x * divide, 5])
        color_number = int(center[:, cluster][2]/ratio), int(center[:, cluster][3]/ratio), int(center[:, cluster][4]/ratio)
        cv2.circle(frame, center=(j, i), radius=1, color=color_number, thickness=0)

    cv2.imshow("VideoFrame", frame)
    print("work over")

capture.release()
cv2.destroyAllWindows()
