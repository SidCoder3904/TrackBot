import cv2 as cv
import mediapipe as mp

mesh = mp.solutions.face_mesh
live = cv.VideoCapture(0)

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
                    centerX = int(marks[6].x * W)
                    centerY = int(marks[6].y * H)
                    isFirst = False
                cv.circle(image, (centerX, centerY), 5, (0, 255, 0), -1)
                cv.imshow("Display", image)
            if(cv.waitKey(20) & 0xFF == ord('d')) :
                break
        else :
            continue
live.release()
cv.destroyAllWindows()