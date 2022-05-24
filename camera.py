# import the opencv library
import cv2
from ohbot import ohbot
import math 

HEADNOD = 0
HEADTURN = 1
EYETURN = 2
LIDBLINK = 3
TOPLIP = 4
BOTTOMLIP = 5
EYETILT = 6

SPEED_DIVISOR = 100

# img size 480x640
# define a video capture object
vid = cv2.VideoCapture(0)

currentX = 5
currentY = 5
ohbot.reset()
def move_to_face(pos):
    global currentX, currentY

    x = ((pos[0]+pos[2]/2)/48)-5
    y = ((pos[1]+pos[3]/2)/64)-5
    currentX -= x / 10
    currentY -= y / 10

    speed = math.sqrt(abs(240-x)**2+abs(320-y)**2)/SPEED_DIVISOR
    
    if currentX<1 or currentX>9 or currentY>9 or currentY<1 or speed<0.3:
        return

    ohbot.move(HEADTURN, currentX, spd=speed)
    ohbot.move(HEADNOD, currentY, spd=speed)   


def detect_face(frame):
    face_cascade=cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml") #Note the change
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    if len(faces)>0:
        face = faces[0]
        move_to_face(face)
        ohbot.move(TOPLIP, 5)
    else:
        ohbot.move(TOPLIP, 0)
    print(frame.shape)
    cv2.imshow('img', frame)



while(True):
    ret, frame = vid.read()
    cv2.imshow('frame', frame)
    detect_face(frame)
    
    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        ohbot.reset()
        break
  
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
