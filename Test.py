import cv2

cap = cv2.VideoCapture('florida-paradise.mp4')

object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=9)

while True:
    ret, frame = cap.read()
    height, width, _ = frame.shape
    # place in video in which to detect vehicles
    #print(height, width)
    roi = frame[90:288,0:432]

    mask = object_detector.apply(roi)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        # remove small elements
        area = cv2.contourArea(cnt)
        if area > 100:
            #cv2.drawContours(roi, [cnt], -1, (0, 255, 0), 2)
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(roi, (x,y), (x+w,y+h), (0,255,0), 3)

    cv2.imshow("roi", roi)  
    #cv2.imshow("frame", frame)
    #cv2.imshow("mask", mask)

    key = cv2.waitKey(30)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()