# import the necessary packages
import cv2
import os

class LiveFaceDetector:
    
     def __init__(self, path="face_detector"):
         self.path = path
         self.net = None
         
         protoPath = os.path.sep.join([self.path, "deploy.prototxt"])
         modelPath = os.path.sep.join([self.path,
	     "res10_300x300_ssd_iter_140000.caffemodel"])
    
         self.net = cv2.dnn.readNetFromCaffe(protoPath, modelPath)
         
     
        
                        
         
