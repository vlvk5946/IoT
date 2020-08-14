import numpy as np
import cv2
import pickle

import RPi.GPIO as GPIO
from time import sleep
import threading
from flask import Flask
import textLCD

detect_state = False

app = Flask(__name__)

def controlDevice():
    app.run(host='0.0.0.0',port=5000,debug=False)

@app.route('/')
def hello():
    return "hello world"

@app.route('/led/<onoff>')
def ledonoff(onoff):
    if detect_state:
        if onoff == "on":
            print("LED Turn on")
            GPIO.output(4,1)
            return "LED on"
        elif onoff == "off":
            print("LED Turn off")
            GPIO.output(4,0)
            return "LED off"
    else:
        print("LED Access Denied")
        return "LED Access Denied"

@app.route('/fan/<onoff>')
def fanonoff(onoff):
    if detect_state:
        if onoff == "on":
            print("FAN Turn on")
            GPIO.output(18,1)
            GPIO.output(27,0)
            return "FAN on"
        elif onoff == "off":
            GPIO.output(18,0)
            GPIO.output(27,0)
            return "FAN off"
    else:
        print("FAN Access Denied")
        return "FAN Access Denied"

def faceRecognition():
    global detect_state
    face_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_alt2.xml')
    eye_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_eye.xml')
    smile_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_smile.xml')


    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("./recognizers/face-trainner.yml")

    labels = {"person_name": 1}
    with open("pickles/face-labels.pickle", 'rb') as f:
        og_labels = pickle.load(f)
        labels = {v:k for k,v in og_labels.items()}

    cap = cv2.VideoCapture(-1)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
        for (x, y, w, h) in faces:
            #print(x,y,w,h)
            roi_gray = gray[y:y+h, x:x+w] #(ycord_start, ycord_end)
            roi_color = frame[y:y+h, x:x+w]
            # recognize? deep learned model predict keras tensorflow pytorch scikit learn
            id_, conf = recognizer.predict(roi_gray)
            if conf>=4 and conf <= 85:
                #print(5: #id_)
                #print(labels[id_])
                font = cv2.FONT_HERSHEY_SIMPLEX
                name = labels[id_]
                color = (255, 255, 255)
                stroke = 2
                cv2.putText(frame, name, (x,y), font, 1, color, stroke, cv2.LINE_AA)
                if name == "obama":
                    detect_state = True
                    textLCD.lcd.clear()
                    line = "ACCESS ALLOWED"
                    textLCD.displayText(line,0,0)
                else:
                    detect_state = False
                    textLCD.lcd.clear()
                    line = "ACCESS DENIED"
                    textLCD.displayText(line,0,0)
            img_item = "7.png"
            cv2.imwrite(img_item, roi_color)

            color = (255, 0, 0) #BGR 0-255
            stroke = 2
            end_cord_x = x + w
            end_cord_y = y + h
            cv2.rectangle(frame, (x, y), (end_cord_x, end_cord_y), color, stroke)

        # Display the resulting frame
        cv2.imshow('frame',frame)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            sleep(0.5)
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    print('bye')
    return

if __name__ == '__main__':
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(4,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(18,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(27,GPIO.OUT,initial=GPIO.LOW)
        
        textLCD.initTextlcd()
        textLCD.displayText('ACCESS DENIED',0,0)
        t = threading.Thread(target=faceRecognition,args=())
        t.daemon = True
        t.start()
        controlDevice()
