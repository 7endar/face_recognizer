import os
import json
from PIL import Image
import numpy as np
import cv2

def images_to_array():
    paths = [os.path.join('../data/resized_faces', i) for i in os.listdir('../data/resized_faces')]
    faces = []
    names = []

    for path in paths:
        image = Image.open(path).convert('L')
        image_np = np.array(image, 'uint8')
        name = os.path.basename(path).split('_')[0]

        faces.append(image_np)
        names.append(name)

    return names, faces

names, faces = images_to_array()

unique_names = list(set(names))
name_to_id = {name: idx for idx, name in enumerate(unique_names)}

ids = [name_to_id[name] for name in names]

np_ids = np.array(ids)

lbph_classifier = cv2.face.LBPHFaceRecognizer.create()
lbph_classifier.train(faces, np_ids)
lbph_classifier.write('../data/lbph_classifier.yml')

with open('../data/name_to_id.json', 'w') as f:
    json.dump(name_to_id, f)
