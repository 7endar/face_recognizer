import os
import sys
import cv2
import numpy as np
from PIL import Image
import dlib
import json

face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor('../data/shape_predictor_68_face_landmarks.dat')
face_descriptor_extractor = dlib.face_recognition_model_v1('../data/dlib_face_recognition_resnet_model_v1.dat')

index = {}
idx = 0
face_descriptors = None

font = cv2.FONT_HERSHEY_COMPLEX_SMALL
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    result = {
        "success": False,
        "message": "Camera could not be found."
    }
    print(json.dumps(result))
    camera.release()
    exit()

paths = [os.path.join('../data/resized_faces', f) for f in os.listdir('../data/resized_faces')]
for path in paths:
    image = Image.open(path).convert('RGB')
    image_np = np.array(image, 'uint8')

    face_detection = face_detector(image_np, 1)
    for face in face_detection:
        points = shape_predictor(image_np, face)

        face_descriptor = face_descriptor_extractor.compute_face_descriptor(image_np, points)
        face_descriptor = [f for f in face_descriptor]
        face_descriptor = np.asarray(face_descriptor, dtype=np.float64)
        face_descriptor = face_descriptor[np.newaxis, :]

        if face_descriptors is None:
            face_descriptors = face_descriptor
        else:
            face_descriptors = np.concatenate((face_descriptors, face_descriptor), axis=0)

        index[idx] = path
        idx += 1

threshold = float(sys.argv[1])

while (True):
    connected, image = camera.read()

    image_np = np.array(image, 'uint8')
    face_detection = face_detector(image_np, 1)

    for face in face_detection:
        l, t, r, b = face.left(), face.top(), face.right(), face.bottom()
        points = shape_predictor(image_np, face)
        face_descriptor = face_descriptor_extractor.compute_face_descriptor(image_np, points)
        face_descriptor = [f for f in face_descriptor]
        face_descriptor = np.asarray(face_descriptor, dtype=np.float64)
        face_descriptor = face_descriptor[np.newaxis, :]

        distances = np.linalg.norm(face_descriptor - face_descriptors, axis=1)
        min_index = np.argmin(distances)
        min_distance = distances[min_index]
        if min_distance <= threshold:
            predicted_name = os.path.split(index[min_index])[1].split('.')[0]
            prediction = predicted_name.split('_')[0]
        else:
            prediction = "unknown"

        cv2.rectangle(image, (l, t), (r, b), (0, 255, 0), 1)
        cv2.putText(image, str(prediction), (l, b + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)

    cv2.imshow("Face Camera", image)
    if cv2.waitKey(1) == ord('q'):
        print(json.dumps({"success": True, "message": "Camera closed successfully"}))
        break

camera.release()
cv2.destroyAllWindows()
