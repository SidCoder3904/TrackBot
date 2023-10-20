import cv2 as cv
import mediapipe as mp

mesh = mp.solutions.face_mesh
live = cv.VideoCapture(0) # replace 0 by 1 for external webcam

# def moveUp(Y) :

# def moveDown(Y) :

# def moveClock(Y) :

# def moveAntiClock(Y) :


def feedback(frame, X, Y) : # instead of 0.5(strict inequality) give minute error lease
    H, W, Z = frame.shape
    if X>0.5 :
        # moveAntiClock(X)
        cv.arrowedLine(frame, (int(0.7*W), int(0.5*H)), (int((0.7+0.3*(X-0.5)/0.5)*W), int(0.5*H)), (0, 255, 0), 2)
    else :
        # moveClock(X)
        cv.arrowedLine(frame, (int(0.3*W), int(0.5*H)), (int((0.3+0.3*(X-0.5)/0.5)*W), int(0.5*H)), (0, 255, 0), 2)
    if Y>0.5:
        # moveDown(Y)
        cv.arrowedLine(frame, (int(0.5*W), int(0.7*H)), (int(0.5*W), int((0.7+0.3*(Y-0.5)/0.5)*H)), (0, 255, 0), 2)
    else :
        # moveUp(Y)
        cv.arrowedLine(frame, (int(0.5*W), int(0.3*H)), (int(0.5*W), int((0.3+0.3*(Y-0.5)/0.5)*H)), (0, 255, 0), 2)

with mesh.FaceMesh(refine_landmarks=True) as face_mesh :
    while live.isOpened() :
        success, frame = live.read()
        isFirst = True
        if success :
            image = cv.flip(frame, 1)
            output = face_mesh.process(image)
            points = output.multi_face_landmarks
            H, W, Z = image.shape
            if points :
                marks = points[0].landmark
                if isFirst :
                    objX = int(marks[6].x*W)
                    objY = int(marks[6].y*H)
                    isFirst = False
                cv.circle(image, (objX, objY), 5, (0, 255, 0), 1)
                feedback(image, marks[6].x, marks[6].y)
                cv.imshow("Display", image)
            if(cv.waitKey(20) & 0xFF == ord('d')) :
                break
        else :
            continue
live.release()
cv.destroyAllWindows()