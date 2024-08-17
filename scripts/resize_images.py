import os
import sys
import cv2

faces_path = sys.argv[1]
target_size = int(sys.argv[2])
resized_faces_path = sys.argv[3]

images = os.listdir(faces_path)
if not os.path.exists(resized_faces_path):
    os.makedirs(resized_faces_path)

for picture in images:
    image_path = os.path.join(faces_path, picture)
    image = cv2.imread(image_path)
    resized_image = cv2.resize(image, [target_size, target_size])
    output_image_path = os.path.join(resized_faces_path, picture)
    cv2.imwrite(output_image_path, resized_image)
