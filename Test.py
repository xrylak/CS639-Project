import cv2

cap = cv2.VideoCapture('japan_intersection.mp4')

object_detector = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=20)

def rescale_frame(frame, percent=30):
    width = int(frame.shape[1] * percent/100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

# processed frames
pro_frames = []
frames_to_proc = 2000

for i in range(frames_to_proc):
    ret, frame = cap.read()
    frame = rescale_frame(frame)
    height, width, _ = frame.shape
    # place in video in which to detect vehicles
    #print(height, width)
    #frame = frame[0:200,0:400]

    mask = object_detector.apply(frame)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        # remove small elements
        area = cv2.contourArea(cnt)
        if area > 200:
            cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
            x, y, w, h = cv2.boundingRect(cnt)
            #cv2.rectangle(roi, (x,y), (x+w,y+h), (0,255,0), 3)
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3)
    pro_frames.append(frame)

    #cv2.imshow("roi", roi)  
    cv2.imshow("frame", frame)
    #cv2.imshow("mask", mask)
    key = cv2.waitKey(30)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()

# setup video
fps = 60.0
pathOut = 'vehicle_detection_japan.mp4'
height, width, layers = pro_frames[0].shape
size = (width,height)
videoOut = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

# write to video with processed frames
for i in range(len(pro_frames)):
    videoOut.write(pro_frames[i])

videoOut.release()