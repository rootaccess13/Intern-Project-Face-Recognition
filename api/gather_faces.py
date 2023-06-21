import cv2
import os

BASE_DIR = "dataset"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

cam = cv2.VideoCapture(0)
cam.set(3, 640)
cam.set(4, 480)

face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

face_id = input('\nEnter user ID and press <return>: ')

print("\n[INFO] Initializing face capture. Look at the camera and wait...")

count = 0

while True:
    ret, img = cam.read()
    img = cv2.flip(img, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        count += 1

        # Create the file path for the saved image using BASE_DIR and os.path.join
        filename = os.path.join(BASE_DIR, f"{face_id}_{count}.jpg")
        cv2.imwrite(filename, gray[y:y+h, x:x+w])

        cv2.imshow('image', img)

    k = cv2.waitKey(100) & 0xff
    if k == 27:
        break
    elif count >= 200:
         break

print("\n[INFO] Exiting program and cleaning up...")
cam.release()
cv2.destroyAllWindows()
