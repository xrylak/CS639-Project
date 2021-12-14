import os
import re
import cv2 # opencv library
import numpy as np
import math
import copy
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
    contours, hierarchy = cv2.findContours(dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours

'''
Method which cuts out the contours that do not appear in the detection area
'''
def getValidContours (contours, detectionArea):
    validContours = []
    for cntr in contours:
        x,y,w,h = cv2.boundingRect(cntr)
        if (y >= ((detectionArea[1][1]-detectionArea[0][1])/(detectionArea[1][0]-detectionArea[0][0]))*(x-detectionArea[0][0])+detectionArea[0][1] and \
        y >= ((detectionArea[3][1]-detectionArea[1][1])/(detectionArea[3][0]-detectionArea[1][0]))*(x-detectionArea[1][0])+detectionArea[1][1] and \
        y >= ((detectionArea[2][1]-detectionArea[3][1])/(detectionArea[2][0]-detectionArea[3][0]))*(x-detectionArea[3][0])+detectionArea[3][1] and \
        y <= ((detectionArea[0][1]-detectionArea[2][1])/(detectionArea[0][0]-detectionArea[2][0]))*(x-detectionArea[2][0])+detectionArea[2][1]):
            validContours.append(cntr)
        # if (x <= detectionLine[1][0] - 40) & (y >= detectionLine[1][1]) & (cv2.contourArea(cntr) >= 25):
        #     if (y >= 10 + detectionLine[0][1]) & (cv2.contourArea(cntr) < 35):
        #         break
            
        #     validContours.append(cntr)

    #Next iterate through contours to make sure none are inside of eachother
    validContoursCopy = validContours.copy()
    for i in range(len(validContours)):
        for j in range(i + 1,len(validContours)):
            x1,y1,w1,h1 = cv2.boundingRect(validContours[i])
            x2,y2,w2,h2 = cv2.boundingRect(validContours[j])
            
            # determine if contour 1 is within contour 2
            if ((x1 > x2) & (x1+w1 < x2+w2) & (y1 + h1 < y2 + h2) & (y1 > y2)):
                # remove it
                index = 0
                for cntr in validContoursCopy:
                    if (validContours[i] is cntr):
                        validContoursCopy.pop(index)
                        break
                    index += 1
            # determine if contour 2 is within contour 1
            elif ((x2 > x1) & (x2+w2 < x1+w1) & (y2 + h2 < y1 + h1) & (y2 > y1)):
                index = 0
                for cntr in validContoursCopy:
                    if (validContours[j] is cntr):
                        validContoursCopy.pop(index)
                        break
                    index += 1
#cv2.matchShapes(cnt1,cnt2,cv2.cv.CV_CONTOURS_MATCH_I1, 0.0)
    
    validContours = validContoursCopy
    
    return validContours      
   
'''
Finds very similar bounding rectangles. Used here to compare rectangles from one frame ago
with current rectangles. In this way, a vehicle's general direction and speed may be computed.
'''
def findRelatedRects(curr_rects, past_rects):
   
    '''
    IMPORTANT: thresshold is the standard by which rectangles are gauged to be similar.
    making it higher reduces direction accuracy, but allows it to be displayed more frequently
    making it lower increases accuracy, but reduces how often direction is displayed.
    37 is a pretty good balance
    '''
    threshhold = 37
   
    related_Rect_Ctrs = [None] * (len(curr_rects) * len(past_rects))
    RR_Dists = [None] * (len(curr_rects) * len(past_rects))
    i = 0
    #compare past rects to current ones. If any are close enough, connect em!
    for P_rect in past_rects:
        for C_rect in curr_rects:
           
            ''' MAYBE use area difference between rectangles to reduce direction error further?
            #find difference in area between rectangles
            PR_area = P_rect[2] * P_rect[3]
            CR_area = C_rect[2] * C_rect[3]
            area_Diff = abs(PR_area - CR_area)
            '''

            #find distance between rectangle centers
            PR_ctr = [P_rect[0] + (P_rect[2]/2), P_rect[1] + (P_rect[3]/2)]
            CR_ctr = [C_rect[0] + (C_rect[2]/2), C_rect[1] + (C_rect[3]/2)]
            sumSq = (abs(PR_ctr[0] - CR_ctr[0]) ** 2 ) + ((abs(PR_ctr[1] - CR_ctr[1])) ** 2)
            dist = math.sqrt(sumSq)
           
            #print('dist = ' + str(dist) + ', PA = ' + str(perc_Diff_A) + ', PB = ' + str(perc_Diff_B) + '\n')
            #print('dist = ' + str(dist) + ' uwu\n')
            #check whether rectangles are closely related
            if ((dist < threshhold) & (dist > 0)):
                related_Rect_Ctrs[i] = [PR_ctr, CR_ctr]
                RR_Dists[i] = dist
                i = i + 1
                #print('found a match uwu\n')
           
    return i, related_Rect_Ctrs, RR_Dists

'''
Method which, given an array of two arrays of contours, returns the average pixel
speed of the contours by comparing similar enough contours.
TODO Possibly track individual contour speed.  Would need an array which stores each
seen contour with every contour being updated every frame with its newest position, and storing its speed also.  
If the contour isn't seen on the next frame, remove it from the array.  This may be
tricky since contours might not be consistently detected which would lead to incorrect speeds.
'''
def calculateSpeed(diffContours):
    averageSpeed = 0
    contourMatches = 0
    for contourA in diffContours[0]:
        for contourB in diffContours[1]:
           
            # compare the contour centers to determine if they are similar enough (hopefully the same car)
            MA = cv2.moments(contourA)
            xA = int(MA["m10"] / MA["m00"])
            yA = int(MA["m01"] / MA["m00"])

            MB = cv2.moments(contourB)
            xB = int(MB["m10"] / MB["m00"])
            yB = int(MB["m01"] / MB["m00"])
           
            sumSq = ( abs(xA - xB)  ^ 2 ) + ( abs(yA - yB) ^ 2)
            distance = math.sqrt(sumSq)
            if (distance <= 5):
                averageSpeed += distance
                contourMatches += 1
    if (contourMatches > 0):
        averageSpeed /= contourMatches
    return averageSpeed

def rescale_frame(frame, percent=30):
    width = int(frame.shape[1] * percent/100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

capture = cv2.VideoCapture('japan_intersection.mp4')
#capture = cv2.VideoCapture('florida-paradise.mp4')

# Check if camera opened successfully
if (capture.isOpened()== False):
    print("Error opening video stream or file")
     
# Read until video is completed
unproFrames = [] # unprocessed frames
proFrames = [] # processed frames
index = -1 # start at -1 since will be incremented before used
detectionLine = (0, 80),(1000,80) # used to validate contours of interest, may change depending on image
detectionAreaRoad = [[217, 270], [441,103], [768,530], [767,178]] # vertices of quad area on road to detect valid contours
detectionAreaCrosswalk = [[]]
fps = 60.0
vehicleCounts = []
vPerSec = 0 # vehicles per second
frameCount = 1 # number of frames processed
diffContours = [None] * 2 # this  will be used to store two arrays of contours for computing the difference in positions of related contours
speedSum = 0 # the sum of vehicle speeds in pixels/second
avgSpeed = 0 # the average of vehicle speeds in pixels/second
currSpeed = 0 # the current speed of vehicles in pixels/second
rects = []
xCoords = [] # the x coordinates of the contours
yCoords = [] # the y coordinates of the contours


while(capture.isOpened()):

    # Capture frame-by-frame
    ret, frame = capture.read()  
    if (ret == True):
        # Scale down size of input video
        frame = rescale_frame(frame)
        unproFrames.append(frame)
        if (len(unproFrames) > 1):
            #find the contours
            contours = getContours(unproFrames[index], unproFrames[index + 1])
            
            # clear old unproFrames to save space
            unproFrames = [unproFrames[index+1]]

            #grab those only within detection zone
            validContours = getValidContours(contours, detectionAreaRoad)
           
            # compute the speed of contours
            diffContours[frameCount % 2] = validContours
            speed = 0
            if (diffContours[0] != None):
                speed = calculateSpeed(diffContours) * fps
                speedSum += speed

            #creating a deep copy of old bounding rectangless (needed later)
            pastRects = copy.deepcopy(rects)
           
            #calculate new bounding rectangles
            rects = [None]*len(validContours)
            polys = [None]*len(validContours)
            for i, c in enumerate(validContours):
                polys[i] = cv2.approxPolyDP(c, 3, True)
                rects[i] = cv2.boundingRect(polys[i])
               
            #find related past/new rectangles
            num_related, related_Rects, RR_Dists = findRelatedRects(rects, pastRects)
           
           
            #create copy frame to draw on
            processedFrame = frame.copy()
           
            '''
            # add contours to original frames
            cv2.drawContours(processedFrame, validContours, -1, (127,200,0), 2)
            '''
           
            #add bounding rectangles to copy frames and retrieve current xCoords and yCoords from contours
            for i in range(len(validContours)):
                color = (256, 0, 0)
                cv2.rectangle(processedFrame, (int(rects[i][0]), int(rects[i][1])), (int(rects[i][0]+rects[i][2]), int(rects[i][1]+rects[i][3])), color, 2)
               
                M = cv2.moments(validContours[i])
                x = int(M["m10"] / M["m00"])
                y = int(M["m01"] / M["m00"])
                xCoords.append(x)
                yCoords.append(y)

            #add vectors indicating direction to bounding rects (if such a direction was found)
            for i in range(num_related):                
                #grab info on related bounding rects
                pair = related_Rects[i]
                past_ctr = pair[0]
                curr_ctr = pair[1]
                dist = RR_Dists[i]
               
                #calculate rounded relative vehicle speed
                rel_spd = dist * fps
                rel_spd = round(rel_spd, 2)
               
                #find point on line 10 units away from current rect to draw direction
                Future_dist = dist + 30
                Dist_ratio = Future_dist/dist
                future_x = (((1-Dist_ratio)*past_ctr[0]) + (Dist_ratio * curr_ctr[0]))
                future_y = (((1-Dist_ratio)*past_ctr[1]) + (Dist_ratio * curr_ctr[1]))
                future_pt = [future_x, future_y]
               
                #draw line and speed
                cv2.line(processedFrame, (int(curr_ctr[0]), int(curr_ctr[1])), (int(future_pt[0]), int(future_pt[1])), (0,0,255), 2)
                cv2.putText(processedFrame, str(rel_spd), (int(curr_ctr[0]), (int(curr_ctr[1]) - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
               
            vehicleCounts.append(len(validContours))

            # when a second has passed, update per second data
            if (frameCount % fps == 0):
                vPerSec = sum(vehicleCounts) / frameCount
                currSpeed = speed
                avgSpeed = speedSum / frameCount
                print(math.floor(frameCount/fps), " seconds of video processed")
               


            cv2.putText(processedFrame, "vehicles detected: " + str(len(validContours)), (20, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(processedFrame, "vehicles/second: " + str(vPerSec), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            cv2.putText(processedFrame, "pixels/second: " + str(currSpeed), (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(processedFrame, "average pixels/second: " + str(avgSpeed), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            #cv2.line(processedFrame, detectionLine[0],detectionLine[1],(100, 255, 255))

            # display average direction line (best fit line)
            if(frameCount > 1 and len(xCoords) > 0 and len(yCoords) > 0):
                a, b = np.polyfit(xCoords,yCoords,1)
                directionLine = (0, int(b)),(1000, int((1000*a)+b))
                cv2.line(processedFrame, directionLine[0],directionLine[1],(100, 255, 255))

            proFrames.append(processedFrame)
            cv2.imshow("frame", processedFrame)
            key = cv2.waitKey(30)
            if key == 27:
                break
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
