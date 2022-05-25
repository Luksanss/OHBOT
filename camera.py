# import the opencv library
import cv2
from ohbot import ohbot
import mediapipe as mp
import math
import os
import time

HORIZONTAL_FOV = 70.42
VERTICAL_FOV = 43.3

VERTICAL_MOVE_SCALE = (VERTICAL_FOV/90) * 10
HORIZONTAL_MOVE_SCALE = (HORIZONTAL_FOV/180) * 10

HEADNOD = 0
HEADTURN = 1
EYETURN = 2
LIDBLINK = 3
TOPLIP = 4
BOTTOMLIP = 5
EYETILT = 6

CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080

SPEED = 10
SPEED_LIMIT = 10
DISTANCE_TRESHOLD = 0.05

DIRECTION = -1
OHBOT_ROT_LIMIT = 10

vid = cv2.VideoCapture(0)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

mp_face_detection = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection()

cur_x_rotation = 5
cur_y_rotation = 5

ohbot.reset()
ohbot.move(HEADTURN, 5)
ohbot.move(HEADNOD, 5)
ohbot.wait(5)
print("Ohbot resetted!")

def direct_move_to_target(x, y, speed):
    currentMotorXRotation = ohbot.motorPos[HEADTURN]
    currentMotorYRotation = 10 - ohbot.motorPos[HEADNOD]

    move_x = (x - 0.5) * HORIZONTAL_MOVE_SCALE * DIRECTION
    move_y = (y - 0.5) * VERTICAL_MOVE_SCALE * DIRECTION

    if currentMotorXRotation+move_x<0 or currentMotorXRotation+move_x>OHBOT_ROT_LIMIT or currentMotorYRotation+move_y>OHBOT_ROT_LIMIT or currentMotorYRotation+move_y<0:
        print("Target too far!")
        return

    ohbot.move(HEADTURN, currentMotorXRotation + move_x, spd=speed)
    ohbot.move(HEADNOD, currentMotorYRotation+move_y, spd = speed)

def move_to_face(pos, img):
    global cur_y_rotation, cur_x_rotation

    if pos == None:
        face_x = 0.5
        face_y = 0.5
    else:
        face_x = pos.xmin + pos.width / 2
        face_y = pos.ymin + pos.height / 3

    x_distance = abs(0.5 - face_x)
    y_distance = abs(0.5 - face_y)
    distance_total = math.sqrt(x_distance**2+y_distance**2)

    speed_x = max(min(x_distance * SPEED, SPEED_LIMIT), 0.1)
    speed_y = max(min(y_distance * SPEED, SPEED_LIMIT), 0.1)

    ohbot.move(EYETURN, (1-face_x)*7)
    ohbot.move(EYETILT, (1-face_y)*7)

    if x_distance > DISTANCE_TRESHOLD:
        dir_x = -(face_x - 0.5) / x_distance
        cur_x_rotation += 3*dir_x*(x_distance**2)
        cur_x_rotation = max(min(OHBOT_ROT_LIMIT, cur_x_rotation), 0)
        ohbot.move(HEADTURN, cur_x_rotation, spd=speed_x)

    if y_distance > DISTANCE_TRESHOLD:
        dir_y = -(face_y - 0.5) / y_distance
        cur_y_rotation += 3*dir_y * (y_distance**2)
        cur_y_rotation = max(min(OHBOT_ROT_LIMIT, cur_y_rotation), 0)
        ohbot.move(HEADNOD, cur_y_rotation, spd=speed_y)


    start_y = 50
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (255, 255, 255)
    thickness = 2

    texts = [
        f"Distance X: {x_distance}",
        f"Distance X: {y_distance}"
    ]

    for i, text in enumerate(texts):
        continue
        img = cv2.putText(img, text, (50, start_y+50*i), font, font_scale, color, thickness=thickness)

    cv2.imshow("camera_0", img)


def detect_face(frame):
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(imgRGB)

    detected_face = None
    if results.detections:
        for id, detection in enumerate(results.detections):
            if detection.location_data.relative_bounding_box.xmin>0.01 and detection.location_data.relative_bounding_box.ymin>0.01:
                #mp_draw.draw_detection(frame, detection)
                detected_face = detection.location_data.relative_bounding_box

    return detected_face, frame

while True:
    ret, frame = vid.read()
    face, img = detect_face(frame)
    move_to_face(face, img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        ohbot.reset()
        break
    cv2.imshow("camera_1", img)
  
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()

ohbot.close()