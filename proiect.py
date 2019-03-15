import numpy as np
import cv2
import sys
import time

cap = cv2.VideoCapture(0)
frontal_face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
profile_face_cascade = cv2.CascadeClassifier('lbpcascade_profileface.xml')
#sys.exit(0)

hasStabilityTimerAlreadyStarted = False
stabilityStartTime = None

betweenSendsStartTime = None


while(True):
    # Capture frame-by-frame
    ret, originalFrame = cap.read()

    if not ret:
        continue

    # Our operations on the frame come here
    gray = cv2.cvtColor(originalFrame, cv2.COLOR_BGR2GRAY)

    faces_frontal = frontal_face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=15,
        minSize=(30, 30)
    )

    
    if len(faces_frontal) != 0:
        if not hasStabilityTimerAlreadyStarted:
            stabilityStartTime = time.time()
            hasStabilityTimerAlreadyStarted = True
    else:
        #print("not!!!!!!!!!")
        hasStabilityTimerAlreadyStarted = False


    if stabilityStartTime:
        if hasStabilityTimerAlreadyStarted:
            stabilityEndTime = time.time()
            stabilityDuration = stabilityEndTime - stabilityStartTime
            #print(duration)
            if stabilityDuration > 1:
                print("a trecut 1 sec")
                hasStabilityTimerAlreadyStarted = False



    

    for (x,y,w,h) in faces_frontal:
        cv2.rectangle(originalFrame, (x,y), (x+w,y+h), (255,0,0), 2)

    #faces_profile = profile_face_cascade.detectMultiScale(gray, 1.3, 5)
    #for (x,y,w,h) in faces_profile:
        #cv2.rectangle(originalFrame, (x,y), (x+w,y+h), (0,255,0), 2)

    # Display the resulting frame
    cv2.imshow('frame',originalFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()