import cv2
import os
import imutils
import numpy as np
import time
#Video graba un video de un minuto.
def video():
    ancho = 640
    alto = 480
    captura = cv2.VideoCapture('/dev/video0')
    codigo = cv2.VideoWriter_fourcc(*'DIVX')
    salida = cv2.VideoWriter('videoA.mp4', codigo, 20, (ancho, alto))

    
    start = time.time()
    while (captura.isOpened()):
        stop = time.time()
        ret, imagen = captura.read()
        if ret:
            cv2.imshow('video', cv2.rotate(imagen,cv2.ROTATE_180))#cv2.rotate(imagen,cv2.ROTATE_180)
            salida.write(cv2.rotate(imagen,cv2.ROTATE_180))#cv2.rotate(imagen,cv2.ROTATE_180)

            # your code
            stop = time.time()
            print("The time of the run:", stop - start)

            key = cv2.waitKey(1)
            if stop - start > 60:
                break
        else: 
            break
        
    captura.release()
    salida.release()     
    cv2.destroyAllWindows()
#Del video de un minuto toma 400 fotos y las pone en una carpeta con el nombre que tu le des
def muestra(nombre):
    
    personName = nombre
    dataPath = '/home/pi/Proyecto/Reconocimiento/Data'
    personPath = dataPath + '/' + personName
    if not os.path.exists(personPath):
        print('Carpeta creada: ',personPath)
        os.makedirs(personPath)

    cap = cv2.VideoCapture('/home/pi/Proyecto/videoA.mp4')
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
#Coge esas 400 fotos y las convierte en un archivo .xml
def entrenamiento():
    dataPath = '/home/pi/Proyecto/Reconocimiento/Data' #Cambia a la ruta donde hayas almacenado Data
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
#Compara los datos del archivo .xml con la cara que se encuentre en cámara en ese momento, si los datos coinciden te aparece el nombre, si los datos no coinciden te aparece desconocido. 
def reconocimiento():
    dataPath = '/home/pi/Proyecto/Reconocimiento/Data' #Cambia a la ruta donde hayas almacenado Data
    imagePaths = os.listdir(dataPath)
    print('imagePaths=',imagePaths)
    face_recognizer = cv2.face.EigenFaceRecognizer_create()

# Leyendo el modelo
    face_recognizer.read('modelo.xml')
    captura = cv2.VideoCapture('/dev/video0')
    ancho = 640
    alto = 480
    codigo = cv2.VideoWriter_fourcc(*'DIVX')
    salida = cv2.VideoWriter('videoConReconocimiento.mp4', codigo, 10, (ancho, alto))
    start = time.time()

    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    while True:
        ret,frame = captura.read()
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
        
        
        cv2.imshow('frame',frame) #cv2.rotate(frame,cv2.ROTATE_180)
        salida.write(frame)
        stop = time.time()
        key = cv2.waitKey(1)
        #if stop - start > 10:
        #   break
        
    captura.release()
    salida.release()     
    cv2.destroyAllWindows()
        

#video()
#muestra(input('Inserte un nombre: '))
#entrenamiento()
reconocimiento()