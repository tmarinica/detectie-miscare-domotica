import numpy as np
import cv2
import sys
import time
import pika
import base64

#connect to rabbitmq

credentials = pika.PlainCredentials('test', 'test')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.43.211', 5672, '/', credentials))
channel = connection.channel()
channel.exchange_declare(exchange='poze', exchange_type='fanout', durable='true')


cap = cv2.VideoCapture(0)
frontal_face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
profile_face_cascade = cv2.CascadeClassifier('lbpcascade_profileface.xml')
upper_body_cascade = cv2.CascadeClassifier('haarcascade_upperbody.xml')

#sys.exit(0)

hasStabilityTimerAlreadyStarted = False
stabilityStartTime = None
stabilityEndTime = None

hasBetweenSendsTimeTimerAlreadyStarted = False
betweenSendsStartTime = None
betweenSendsEndTime = None
betweenSendsTimerDuration = None

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

    upper_body_profile = []

    '''
    upper_body_profile = upper_body_cascade.detectMultiScale(
        gray,
        scaleFactor=2,
        minNeighbors=15,
        minSize=(30, 30)
    )
    '''

    if (len(faces_frontal) != 0 or len(upper_body_profile) != 0):
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
                print("a trecut 1 sec de stabilitate")

                if not hasBetweenSendsTimeTimerAlreadyStarted or (hasBetweenSendsTimeTimerAlreadyStarted and betweenSendsTimerDuration >= 5): 
                    print("trimit poza...")

                    retval, buffer = cv2.imencode('.jpg', originalFrame)
                    jpg_as_text = base64.b64encode(buffer)
                    
                    #print(jpg_as_text)

                    channel.basic_publish(exchange='poze', routing_key='poze', body=jpg_as_text)

                    hasBetweenSendsTimeTimerAlreadyStarted = False
                    betweenSendsTimerDuration = 0
                
                if not hasBetweenSendsTimeTimerAlreadyStarted:
                    hasBetweenSendsTimeTimerAlreadyStarted = True
                    betweenSendsStartTime = time.time()

                hasStabilityTimerAlreadyStarted = False

    if betweenSendsStartTime:
        betweenSendsEndTime = time.time()
        betweenSendsTimerDuration = betweenSendsEndTime - betweenSendsStartTime
        print("betweenSendsTimerDuration = "+str(betweenSendsTimerDuration))
    

    for (x,y,w,h) in faces_frontal:
        cv2.rectangle(originalFrame, (x,y), (x+w,y+h), (255,0,0), 2)

    #faces_profile = profile_face_cascade.detectMultiScale(gray, 1.3, 5)
    #for (x,y,w,h) in faces_profile:
        #cv2.rectangle(originalFrame, (x,y), (x+w,y+h), (0,255,0), 2)

    
    for (x,y,w,h) in upper_body_profile:
        cv2.rectangle(originalFrame, (x,y), (x+w,y+h), (0,255,0), 2)

    # Display the resulting frame
    cv2.imshow('frame',originalFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        connection.close()
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
connection.close()
