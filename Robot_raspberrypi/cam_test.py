import cv2

camera = cv2.VideoCapture('/dev/video0')  # Replace with your correct device
if camera.isOpened():
    ret, frame = camera.read()
    if ret:
        print("Camera works!")
        cv2.imwrite("test_image.jpg", frame)
    else:
        print("Failed to capture frame")
camera.release()
