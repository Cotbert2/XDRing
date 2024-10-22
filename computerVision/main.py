import cv2
import time
import sys
import os
import json
import numpy as np
import imutils


#This iscript contains all functions for the project, call it by js

def tomarFoto():
    #change the device if you have more than one camera or even another name
    cap = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)

    ret, frame = cap.read()

    cv2.imwrite('./../assets/image.jpg', frame)
    cv2.imwrite('./../assets/image.jpg', cv2.rotate(cv2.imread('./../assets/image.jpg'), cv2.ROTATE_180))

    cap.release()


def grabarVideoConReconocimiento():
    cascade_face = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    width = 640
    height = 480
    takeshoot = cv2.VideoCapture('/dev/video0')
    code = cv2.VideoWriter_fourcc(*'DIVX')
    output = cv2.VideoWriter('./../assets/video.mp4', code, 5, (width, height))
    start = time.time()

    while (takeshoot.isOpened()):
        stop = time.time()
        ret, imagen = takeshoot.read()
        gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        face = cascade_face.detectMultiScale(gray,1.2,5)

        if ret:
            for (x,y,w,h) in face:
                cv2.rectangle(imagen, (x,y), (x+w, y+h), (124,252,0), 2)

            cv2.imshow('video', cv2.rotate(imagen,cv2.ROTATE_180))
            output.write(cv2.rotate(imagen,cv2.ROTATE_180))

            # your code
            stop = time.time()
            print("The time of the run:", stop - start)

            key = cv2.waitKey(1)
            if stop - start > 5:
                break
        else:
            break

    takeshoot.release()
    output.release()
    cv2.destroyAllWindows()


def grabarVideo():
    width = 640
    height = 480
    takeshoot = cv2.VideoCapture('/dev/video0')
    code = cv2.VideoWriter_fourcc(*'DIVX')
    output = cv2.VideoWriter('videoConReconocimiento.mp4', code, 20, (width, height))


    start = time.time()
    while (takeshoot.isOpened()):
        stop = time.time()
        ret, imagen = takeshoot.read()
        if ret:
            cv2.imshow('video', cv2.rotate(imagen,cv2.ROTATE_180))
            output.write(cv2.rotate(imagen,cv2.ROTATE_180))

            # your code
            stop = time.time()
            print("The time of the run:", stop - start)

            key = cv2.waitKey(1)
            if stop - start > 10:
                break
        else:
            break

    takeshoot.release()
    output.release()
    cv2.destroyAllWindows()

def apagar():
    #for linux os (raspbian)
    os.system('sudo shutdown -h now')

def soundRing():
    os.system('sudo omxplayer -o local ./../assets/ring.mp3')

def soundVoice(file):
    os.system('sudo omxplayer -o local ' + file)

def video():
    width = 640
    height = 480
    takeshoot = cv2.VideoCapture('/dev/video0')
    code = cv2.VideoWriter_fourcc(*'DIVX')
    output = cv2.VideoWriter('videoA.mp4', code, 20, (width, height))


    start = time.time()
    while (takeshoot.isOpened()):
        stop = time.time()
        ret, imagen = takeshoot.read()
        if ret:
            cv2.imshow('video', cv2.rotate(imagen,cv2.ROTATE_180))
            output.write(cv2.rotate(imagen,cv2.ROTATE_180))

            stop = time.time()
            print("The time of the run:", stop - start)

            key = cv2.waitKey(1)
            if stop - start > 20:
                break
        else:
            break

    takeshoot.release()
    output.release()
    cv2.destroyAllWindows()

def muestra(nombre):
    personName = nombre
    dataPath = './../Recognition/Data'
    personPath = dataPath + '/' + personName
    if not os.path.exists(personPath):
        print('Carpeta creada: ',personPath)
        os.makedirs(personPath)

    cap = cv2.VideoCapture('./../aseets/videoA.mp4')
    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    count = 0

    while True:
        ret, frame = cap.read()
        if ret == False: break
        frame =  imutils.resize(frame, width=640)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        auxFrame = frame.copy()
        faces = faceClassif.detectMultiScale(gray,1.3,5)

        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)
            rostro = auxFrame[y:y+h,x:x+w]
            rostro = cv2.resize(rostro,(150,150),interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(personPath + '/rostro_{}.jpg'.format(count),rostro)
            count = count + 1
        cv2.imshow('frame',frame)
        k =  cv2.waitKey(1)
        if k == 27 or count >= 400:
            break
    cap.release()
    cv2.destroyAllWindows()
    entrenamiento()

def entrenamiento():
    dataPath = './../Recognition/Data'
    peopleList = os.listdir(dataPath)
    print('Lista de personas: ', peopleList)

    labels = []
    facesData = []
    label = 0
    for nameDir in peopleList:
        personPath = dataPath + '/' + nameDir
        print('Leyendo las imágenes')

        for fileName in os.listdir(personPath):
            print('Rostros: ', nameDir + '/' + fileName)
            labels.append(label)
            facesData.append(cv2.imread(personPath+'/'+fileName,0))

        label = label + 1

    face_recognizer = cv2.face.EigenFaceRecognizer_create()
    print("Entrenando...")

    face_recognizer.train(facesData, np.array(labels))

    face_recognizer.write('modelo.xml')

    print('Modelo Creado')

def reconocimiento():
    dataPath = './../Recognition/Data' #Cambia a la ruta donde hayas almacenado Data
    imagePaths = os.listdir(dataPath)
    print('imagePaths=',imagePaths)
    face_recognizer = cv2.face.EigenFaceRecognizer_create()

# Leyendo el modelo
    face_recognizer.read('modelo.xml')
    takeshoot = cv2.VideoCapture('/dev/video0')
    width = 640
    height = 480
    code = cv2.VideoWriter_fourcc(*'DIVX')
    output = cv2.VideoWriter('./../assets/videoConReconocimiento.mp4', code, 10, (width, height))
    start = time.time()

    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    while True:
        ret,frame = takeshoot.read()
        frame = cv2.rotate(frame,cv2.ROTATE_180)
        if ret == False: break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        auxFrame = gray.copy()
        faces = faceClassif.detectMultiScale(gray,1.3,5)
        for (x,y,w,h) in faces:
            rostro = auxFrame[y:y+h,x:x+w]
            rostro = cv2.resize(rostro,(150,150),interpolation= cv2.INTER_CUBIC)
            result = face_recognizer.predict(rostro)
            cv2.putText(frame,'{}'.format(result),(x,y-5),1,1.3,(255,255,0),1,cv2.LINE_AA)
        
        # EigenFaces
            if result[1] < 3500: #5700
                cv2.putText(frame,'{}'.format(imagePaths[result[0]]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
                cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)
            else:
                cv2.putText(frame,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
                cv2.rectangle(frame, (x,y),(x+w,y+h),(0,0,255),2)

        cv2.imshow('frame',frame)
        output.write(frame)
        stop = time.time()
        key = cv2.waitKey(1)
        if stop - start > 10:
            break

    takeshoot.release()
    output.release()
    cv2.destroyAllWindows()

OPCION = int(sys.argv[1])
PARAMETER = sys.argv[2]
print(OPCION)

if OPCION== 1:
   tomarFoto()
elif OPCION == 4:
   grabarVideo()
elif OPCION == 5:
   reconocimiento()
elif OPCION == 6:
   apagar()
elif OPCION == 7:
    tomarFoto()
    soundRing()
elif OPCION == 8:
   video()
elif OPCION == 9:
   muestra(PARAMETER)
elif OPCION == 10:
   soundVoice(PARAMETER)
