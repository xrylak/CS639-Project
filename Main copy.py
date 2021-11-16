import os
import re
import cv2 # opencv library
import numpy as np
from os.path import isfile, join
import matplotlib.pyplot as plt

# sources: 
# https://learnopencv.com/read-write-and-display-a-video-using-opencv-cpp-python/
# https://www.analyticsvidhya.com/blog/2020/04/vehicle-detection-opencv-python/

'''
Method which finds the contours of the provided images and returns them
'''
def getContours(image1, image2):
    # frame differencing
    grayA = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    diff_image = cv2.absdiff(grayB, grayA)
    
    # image thresholding
    ret, thresh = cv2.threshold(diff_image, 30, 255, cv2.THRESH_BINARY)
    
    # image dilation
    kernel = np.ones((4,4),np.uint8)
    dilated = cv2.dilate(thresh,kernel,iterations = 1)
        
    # find contours
    image, contours, hierarchy = cv2.findContours(dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    return contours

'''
Method which cuts out the contours that do not appear in the detection area
TODO maybe pass in contour area instead? May need to change depending on image
'''
def getValidContours (contours, detectionLine, dContours):
    validContours = []
    for cntr in contours:
        x,y,w,h = cv2.boundingRect(cntr)
        if (x <= detectionLine[1][0] - 40) & (y >= detectionLine[1][1]) & (cv2.contourArea(cntr) >= 25):
            if (y >= 10 + detectionLine[0][1]) & (cv2.contourArea(cntr) < 35):
                break
            '''
            for Dcntr in dContours:
                if np.array_equal(Dcntr, cntr):
                    break
            '''
            validContours.append(cntr)
    return validContours        



capture = cv2.VideoCapture('florida-paradise.mp4')

# Check if camera opened successfully
if (capture.isOpened()== False):
    print("Error opening video stream or file")
	 
# Read until video is completed
unproFrames = [] # unprocessed frames
proFrames = [] # processed frames
index = -1 # start at -1 since will be incremented before used
frameDir = '/'
detectionLine = (0, 80),(1000,80) # used to validate contours of interest, may change depending on image
fps = 14.0
vehicleCounts = []
vPerSec = 0 # vehicles per second
frameCount = 1 # number of frames processed

doneContours = []

#TODO could maybe first go through and compute average contour size which could be used as a detection threshold?
while(capture.isOpened()):
	# Capture frame-by-frame
    ret, frame = capture.read()   
    if (ret == True):
        unproFrames.append(frame)
        if (len(unproFrames) > 121):
            #find the contours
            contours = getContours(unproFrames[index], unproFrames[index + 1])
                        
            #grab those only within detection zone
            validContours = getValidContours(contours, detectionLine, doneContours)
            '''
            for cn in validContours:
                doneContours.append(cn)
            '''
            
            #calculate bounding rectangles
            rects = [None]*len(validContours)
            polys = [None]*len(validContours)
            for i, c in enumerate(validContours):
                polys[i] = cv2.approxPolyDP(c, 3, True)
                rects[i] = cv2.boundingRect(polys[i])
            
            #create copy frame to draw on
            processedFrame = frame.copy()
            
            '''
            # add contours to original frames
            cv2.drawContours(processedFrame, validContours, -1, (127,200,0), 2)
            '''
            
            #add bounding rectangles to copy frames
            for i in range(len(validContours)):
                color = (256, 0, 0)
                cv2.rectangle(processedFrame, (int(rects[i][0]), int(rects[i][1])), (int(rects[i][0]+rects[i][2]), int(rects[i][1]+rects[i][3])), color, 2)

            #TODO Need to add more data to display for each frame, such as cars per minute which requires some counting and approximation
            vehicleCounts.append(len(validContours))
            # when a second has passed, compute a new vehicles/second number
            
            if (frameCount % fps == 0):
                vPerSec = sum(vehicleCounts) / frameCount

            cv2.putText(processedFrame, "vehicles detected: " + str(len(validContours)), (20, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(processedFrame, "vehicles/second: " + str(vPerSec), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.line(processedFrame, detectionLine[0],detectionLine[1],(100, 255, 255))
            proFrames.append(processedFrame)
            frameCount += 1
            
    else:
	    break

# When everything is done, release the video capture object
capture.release()

# Closes all the frames
cv2.destroyAllWindows()

# setup video
pathOut = 'vehicle_detection.mp4'
height, width, layers = proFrames[0].shape
size = (width,height)
videoOut = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

# write to video with processed frames
for i in range(len(proFrames)):
    videoOut.write(proFrames[i])

videoOut.release()

