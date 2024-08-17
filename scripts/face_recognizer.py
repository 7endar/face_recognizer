import cv2
import os
import json
import numpy as np
from PIL import Image
import dlib
import sys

threshold = float(sys.argv[1])

face_detector = dlib.get_frontal_face_detector()
points_detector = dlib.shape_predictor('../data/shape_predictor_68_face_landmarks.dat')
face_descriptor_extractor = dlib.face_recognition_model_v1('../data/dlib_face_recognition_resnet_model_v1.dat')

index = {}
idx = 0
face_descriptors = None

paths = [os.path.join('../data/resized_faces', i) for i in os.listdir('../data/resized_faces')]

for path in paths:
    image = Image.open(path).convert('RGB')
    image_np = np.array(image, 'uint8')
    face_detection = face_detector(image_np, 1)

    for face in face_detection:
        points = points_detector(image_np, face)
        face_descriptor = face_descriptor_extractor.compute_face_descriptor(image_np, points)
        face_descriptor = np.asarray(face_descriptor, dtype=np.float64)[np.newaxis, :]

        if face_descriptors is None:
            face_descriptors = face_descriptor
        else:
            face_descriptors = np.concatenate((face_descriptors, face_descriptor), axis=0)

        index[idx] = path
        idx += 1

test_paths = [os.path.join('../data/test_faces', i) for i in os.listdir('../data/test_faces')]
predictions = []

for path in test_paths:
    test_image = Image.open(path).convert('RGB')
    test_image_np = np.array(test_image, 'uint8')
    test_face_detection = face_detector(test_image_np, 1)

    for face in test_face_detection:
        points = points_detector(test_image_np, face)
        test_face_descriptor = face_descriptor_extractor.compute_face_descriptor(test_image_np, points)
        test_face_descriptor = np.asarray(test_face_descriptor, dtype=np.float64)[np.newaxis, :]

        distances = np.linalg.norm(face_descriptors - test_face_descriptor, axis=1)
        min_distance_idx = np.argmin(distances)
        closest_distance = distances[min_distance_idx]

        closest_name = os.path.basename(index[min_distance_idx]).split('_')[0]

        if closest_distance < threshold:
            prediction = closest_name
        else:
            prediction = "unknown"

    new_prediction = {"path": path, "prediction": f'prediction: {prediction}', "distance": f'distance = {closest_distance}'}
    predictions.append(new_prediction)

result_data = {
    "predictions": predictions
}

print(json.dumps(result_data))
