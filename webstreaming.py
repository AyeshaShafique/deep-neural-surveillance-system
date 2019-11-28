# USAGE
# python webstreaming.py --ip 127.0.0.1 --port 3000

# import the necessary packages
from pyimagesearch.motion_detection import SingleMotionDetector
from coordinateslocationdetector import CoordinatesLocationDetector
#from emailnotify import MailNotify
from livefacedetector import LiveFaceDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
from PIL import Image
import numpy as np
import threading
import argparse
import datetime
import imutils
import time
import cv2
import os


# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()
lock2 = threading.Lock()

# initialize a flask object
app = Flask(__name__)


#initialize the Email Notifier
#emn =MailNotify()

# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream("/dev/video0").start()
time.sleep(2.0)



@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

def detect_face(frame, net):

    
	# grab the frame dimensions and convert it to a blob
    
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
			(300, 300), (104.0, 177.0, 123.0))

	# pass the blob through the network and obtain the detections and
	# predictions
	net.setInput(blob)
	detections = net.forward()

	# loop over the detections
	for i in range(0, detections.shape[2]):
			# extract the confidence (i.e., probability) associated with the
			# prediction
			confidence = detections[0, 0, i, 2]

			# filter out weak detections
			if confidence > 0.5:
					# compute the (x, y)-coordinates of the bounding box for
					# the face and extract the face ROI
					box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
					(startX, startY, endX, endY) = box.astype("int")

					# ensure the detected bounding box does fall outside the
					# dimensions of the frame
					startX = max(0, startX)
					startY = max(0, startY)
					endX = min(w, endX)
					endY = min(h, endY)

				   

					# draw the label and bounding box on the frame
					label = "Face Alter!"
					cv2.putText(frame, label, (startX, startY - 10),
							cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
					cv2.rectangle(frame, (startX, startY), (endX, endY),
							(0, 0, 255), 2)


					#img = Image.fromarray(frame)
					#img.save(os.path.join("E:\\Last days Data\\stream-video-browser\\stream-video-browser\\Results" , str(datetime.datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")) + ".jpg"))
        
                                        
 

def detect_motion(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock, lock2
    
	# initialize the Coordinates detector 
	cld = CoordinatesLocationDetector()
    
    #initialize the live face detector
	lfd =LiveFaceDetector()

	
	# initialize the motion detector and the total number of frames
	# read thus far
	md = SingleMotionDetector(accumWeight=0.1)
	total = 0
    

	# loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		frame = vs.read()
		#print("Hi")
        #frame = imutils.resize(frame, width=600)

		detect_face(frame,lfd.net)
        
       
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    
		gray = cv2.GaussianBlur(gray, (7, 7), 0)
        
		# grab the current timestamp and draw it on the frame
		timestamp = datetime.datetime.now()

		# grab the current location with zip and draw it on the frame
		#location = cld.get_location_coordinates()


		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		cv2.putText(frame, str("Location Coordinates: X, Y: (%.5f , %.5f)" % (24.86242, 67.07256)), (10, frame.shape[0] - 420),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 0, 0), 1)
		                        
		
   

		# if the total number of frames has reached a sufficient
		# number to construct a reasonable background model, then
		# continue to process the frame
		if total > frameCount:
			# detect motion in the image
			motion = md.detect(gray)

			# cehck to see if motion was found in the frame
			if motion is not None:
				# unpack the tuple and draw the box surrounding the
				# "motion area" on the output frame
				(thresh, (minX, minY, maxX, maxY)) = motion
				cv2.putText(frame, "Motion Alert!", (minX, minY - 10),
							cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
				cv2.rectangle(frame, (minX, minY), (maxX, maxY),
					(0, 255, 0), 2)
		
		# update the background model and increment the total number
		# of frames read thus far
		md.update(gray)
		total += 1

		# acquire the lock, set the output frame, and release the
		# lock
		with lock:
			outputFrame = frame.copy()
		
		
def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            
            
            

			# ensure the frame was successfully encoded
			if not flag:
				continue
			
                             
                                

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
        

	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=False, default="0.0.0.0",
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=False, default=5000,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())
    
   

	# start a thread that will perform motion detection
	t1 = threading.Thread(target=detect_motion, args=(
		args["frame_count"],))
	t1.daemon = True
	t1.start()
    
    # start a thread that will perform motion detection
	t2 = threading.Thread(target=emn.send_mail, args=())
	t2.daemon = True
	t2.start()

    
   

	# start the flask app
	app.run(host='172.17.0.2')

# release the video stream pointer
vs.stop()
