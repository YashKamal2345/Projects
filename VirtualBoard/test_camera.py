import cv2

# Test camera access
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
else:
    print("Camera opened successfully")
    ret, frame = cap.read()
    if ret:
        print("Frame captured successfully")
        cv2.imshow('Test Frame', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Failed to capture frame")
    
    cap.release()
