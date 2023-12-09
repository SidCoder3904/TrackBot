# Program to control an arduino based turret (a camera with a laser) that auto locks to a target (hand in this case) and follows its movement
import time
import threading as td
import cv2 as cv
import mediapipe as mp
from pyfirmata import Arduino, SERVO

# initializing arduino and servos
port = 'COM6'   # depends on the port used
board = Arduino(port)

servoPin1 = 9   # horizontal
servoPin2 = 10  # vertical
board.digital[servoPin1].mode = SERVO
board.digital[servoPin2].mode = SERVO
laser = board.get_pin('d:11:s')    # laser port

# hyper-parameters
e = 0.04    # error margin for target locking
m = 5   # scaling factor for servo movement

def moveServo(pin, angle) :     # function to rotate servos
    if angle<180 and angle>0 :
        board.digital[pin].write(angle)

# feedback display on screen
def show_feedback(frame, X, Y) : # instead of 0.5(strict inequality) give minute error lease
    H, W, Z = frame.shape
    if X>0.5 :
        # AntiClock
        cv.arrowedLine(frame, (int(0.7*W), int(0.5*H)), (int((0.7+0.3*(X-0.5)/0.5)*W), int(0.5*H)), (0, 255, 0), 2)
    else :
        # Clock
        cv.arrowedLine(frame, (int(0.3*W), int(0.5*H)), (int((0.3+0.3*(X-0.5)/0.5)*W), int(0.5*H)), (0, 255, 0), 2)
    if Y>0.5:
        # Down
        cv.arrowedLine(frame, (int(0.5*W), int(0.7*H)), (int(0.5*W), int((0.7+0.3*(Y-0.5)/0.5)*H)), (0, 255, 0), 2)
    else :
        # Up
        cv.arrowedLine(frame, (int(0.5*W), int(0.3*H)), (int(0.5*W), int((0.3+0.3*(Y-0.5)/0.5)*H)), (0, 255, 0), 2)
    
    with angles_lock :
        locked1 = abs(X-0.5)<e
        locked2 = abs(Y-0.5)<e
        l1, l2 = locked1, locked2
    
    if l1 and l2 :
        cv.putText(frame, "TARGET LOCKED", (int(0.05*W), int(0.05*H)), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv.circle(frame, (int(X*W), int(Y*H)), 20, (0, 0, 255), 2)
        laser.write(255)
    else :
        cv.circle(frame, (int(X*W), int(Y*H)), 5, (0, 255, 0), 1)
        laser.write(0)
    cv.imshow("Display", frame)

# opencv frame reading and object tracking thread
def opencv() :
    global servoAngle1, servoAngle2, locked1, locked2
    servoAngle1 = 90
    servoAngle2 = 45
    locked1 = False
    locked2 = False

    with mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2) as hands :
        live = cv.VideoCapture(1) # replace 0 by 1 for external webcam
        while live.isOpened() :
            success, frame = live.read()
            image = cv.flip(frame, 1)
            if success :
                output = hands.process(cv.cvtColor(image, cv.COLOR_BGR2RGB))
                points = output.multi_hand_landmarks
                H, W, Z = image.shape
                if points :
                    marks = points[0].landmark
                    show_feedback(image, marks[9].x, marks[9].y)
                    
                    # depth perception using calibration for average hand
                    width = ((marks[17].x - marks[5].x)**2 + (marks[17].y - marks[5].y)**2)**(1/2)
                    dist = 5.8 / width
                    print('dist (in cm): ', dist)

                    with angles_lock :
                        a1, a2 = servoAngle1, servoAngle2
                    if a1<=180 and a1>=0 :
                        a1 += m * (marks[9].x - 0.5)
                    else :
                        a1 = 90
                    if a2<=180 and a2>=0 : 
                        a2 -= m * (marks[9].y - 0.5)
                    else :
                        a2 = 45
                    with angles_lock:
                        servoAngle1, servoAngle2 = a1, a2
                else :
                    cv.putText(image, "TARGET NOT DETECTED", (int(0.05*W), int(0.05*H)), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                    cv.imshow("Display", image)
                if(cv.waitKey(20) & 0xFF == ord('d')) :
                    break
            else :
                continue
    live.release()
    cv.destroyAllWindows()

# thread to control servo1
def control_servo1() :
    islocked = False
    while True :
        with angles_lock :
            angle, islocked = servoAngle1, locked1
        if angle<180 and angle>0 and not islocked :
            board.digital[servoPin1].write(angle)
            time.sleep(1)

# thread to control servo2
def control_servo2() :
    islocked = False
    while True :
        with angles_lock :
            angle, islocked = servoAngle2, locked2
        if angle<180 and angle>0 and not islocked :
            board.digital[servoPin2].write(angle)
            time.sleep(0.5)

# main loop // program flow
board.digital[servoPin1].write(90)
board.digital[servoPin2].write(45)
print('servos initialized.')
time.sleep(5)   # initial delay for stabilization

# initialize threads and lock
angles_lock = td.Lock()
opencv_thread = td.Thread(target = opencv)
servo1_thread = td.Thread(target = control_servo1)
servo2_thread = td.Thread(target = control_servo2)

opencv_thread.start()
servo1_thread.start()
servo2_thread.start()