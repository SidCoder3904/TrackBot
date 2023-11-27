import time
import threading as td
import cv2 as cv
import mediapipe as mp
from pyfirmata import Arduino, SERVO, util

# initializing arduino
port = 'COM6'
board = Arduino(port)

servoPin1 = 9   # horizontal
servoPin2 = 10  # vertical
board.digital[servoPin1].mode = SERVO
board.digital[servoPin2].mode = SERVO

#initialize angles
servoAngle1 = 90    # horizontal
servoAngle2 = 45    # vertical

mesh = mp.solutions.face_mesh
live = cv.VideoCapture(1) # replace 0 by 1 for external webcam

e = 0.02
m = 5
def moveServo(pin, angle) :
    if angle<180 and angle>0 :
        board.digital[pin].write(angle)

def feedback(frame, X, Y) : # instead of 0.5(strict inequality) give minute error lease
    H, W, Z = frame.shape
    if X>0.5 :
        # moveAntiClock(X*1000)
        cv.arrowedLine(frame, (int(0.7*W), int(0.5*H)), (int((0.7+0.3*(X-0.5)/0.5)*W), int(0.5*H)), (0, 255, 0), 2)
    else :
        # moveClock(X*1000)
        cv.arrowedLine(frame, (int(0.3*W), int(0.5*H)), (int((0.3+0.3*(X-0.5)/0.5)*W), int(0.5*H)), (0, 255, 0), 2)
    if Y>0.5:
        # moveDown(Y)
        cv.arrowedLine(frame, (int(0.5*W), int(0.7*H)), (int(0.5*W), int((0.7+0.3*(Y-0.5)/0.5)*H)), (0, 255, 0), 2)
    else :
        # moveUp(Y)
        cv.arrowedLine(frame, (int(0.5*W), int(0.3*H)), (int(0.5*W), int((0.3+0.3*(Y-0.5)/0.5)*H)), (0, 255, 0), 2)
    if abs(X-0.5)<e and abs(Y-0.5)<e :
        with angles_lock :
            locked = True
        cv.putText(frame, "TARGET LOCKED", (int(0.05*W), int(0.05*H)), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv.circle(frame, (int(X*W), int(Y*H)), 5, (0, 0, 255), 1)
    else :
        with angles_lock :
            locked = False
        cv.circle(frame, (int(X*W), int(Y*H)), 5, (0, 255, 0), 1)
    cv.imshow("Display", frame)
    
def opencv() :
    global servoAngle1, servoAngle2, locked
    servoAngle1 = 90
    servoAngle2 = 45
    locked = False
    with mesh.FaceMesh(refine_landmarks=True) as face_mesh :
        while live.isOpened() :
            success, frame = live.read()
            image = cv.flip(frame, 1)
            if success :
                output = face_mesh.process(image)
                points = output.multi_face_landmarks
                H, W, Z = image.shape
                if points :
                    marks = points[0].landmark
                    with angles_lock :
                        a1, a2 = servoAngle1, servoAngle2
                    if a1<=180 and a1>=0 :
                        a1 -= m * (marks[6].x - 0.5)
                    else :
                        a1 = 90
                    if a2<=180 and a2>=0 : 
                        a2 -= m * (marks[6].y - 0.5)
                    else :
                        a2 = 45
                    with angles_lock:
                        servoAngle1, servoAngle2 = a1, a2
                    feedback(image, marks[6].x, marks[6].y)
                else :
                    cv.putText(image, "TARGET NOT DETECTED", (int(0.05*W), int(0.05*H)), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                    cv.imshow("Display", image)
                if(cv.waitKey(20) & 0xFF == ord('d')) :
                    break
            else :
                continue  
    live.release()
    cv.destroyAllWindows()

def control_servos() :
    while True :
        with angles_lock :
            a1, a2 = servoAngle1, servoAngle2
        print(a1, a2)
        moveServo(servoPin1, a1)
        moveServo(servoPin2, a2)
        time.sleep(0.5)

angles_lock = td.Lock()
moveServo(servoPin1, 90)
moveServo(servoPin2, 45)
print('initialized')
time.sleep(5)
opencv_thread = td.Thread(target = opencv)
servo_thread = td.Thread(target = control_servos)

opencv_thread.start()
servo_thread.start()
