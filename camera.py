# import the opencv library
import cv2
from ohbot import ohbot
import mediapipe as mp
import math
import os
import time

HORIZONTAL_FOV = 70.42
VERTICAL_FOV = 43.3

move_v = VERTICAL_FOV/100

HEADNOD = 0
HEADTURN = 1
EYETURN = 2
LIDBLINK = 3
TOPLIP = 4
BOTTOMLIP = 5
EYETILT = 6

CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080

SPEED = 3
SPEED_LIMIT = 2
DISTANCE_TRESHOLD = 0.2

DIRECTION = -1
OHBOT_ROT_LIMIT = 10

vid = cv2.VideoCapture(0)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

mp_face_detection = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection()

ohbot.reset()
ohbot.wait(1)
def move_to_face(pos):
    face_x = pos.xmin + pos.width/2
    face_y = pos.ymin + pos.height/2

    x_distance = abs(0.5 - face_x)
    y_distance = abs(0.5 - face_y)
    distance_total = math.sqrt(x_distance**2+y_distance**2)

    speed_x = max(min(x_distance * SPEED, SPEED_LIMIT), 0.1)
    speed_y = max(min(y_distance * SPEED*2, SPEED_LIMIT*3), 0.1)

    currentMotorXRotation = ohbot.motorPos[HEADTURN]
    currentMotorYRotation = ohbot.motorPos[HEADNOD]

    move_x = (face_x - 0.5) * 3.91222 * DIRECTION
    move_y = (face_y - 0.5) * move_v * DIRECTION

   # print(f"X: {currentMotorXRotation + move_x}")
   # print(f"Y: {currentMotorYRotation + move_y}")
    #print(f"Speed X: {speed_x}, Speed Y: {speed_y}")
    #print(f"Distance: {distance_total}")

    if currentMotorXRotation+move_x<0 or currentMotorXRotation+move_x>OHBOT_ROT_LIMIT or currentMotorYRotation+move_y>OHBOT_ROT_LIMIT or currentMotorYRotation+move_y<0:
        return

    print(speed_x, speed_y)

    if x_distance>DISTANCE_TRESHOLD:
        ohbot.move(HEADTURN, currentMotorXRotation+move_x, spd=0.5)

    if y_distance>DISTANCE_TRESHOLD:
        ohbot.move(HEADNOD, currentMotorYRotation+move_y, spd=1)


def detect_face(frame):
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(imgRGB)

    if results.detections:
        for id, detection in enumerate(results.detections):
            mp_draw.draw_detection(frame, detection)

    cv2.imshow('img', frame)
    if results.detections:
        return results.detections[0].location_data.relative_bounding_box

    return None

while True:
    ret, frame = vid.read()
    face = detect_face(frame)
    if face is not None:
        move_to_face(face)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        ohbot.reset()
        break
  
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()

ohbot.close()