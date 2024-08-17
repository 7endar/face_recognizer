import os
import cv2
import sys
import json

path_id = int(sys.argv[1])
min_size = int(sys.argv[2])

if path_id == 0:
    path = "../data/faces"
else:
    path = '../data/resized_faces'

if not os.path.exists(path):
    result_data = {
        "success": False,
        "result_message": f"The directory {path} does not exist.",
        "show_info": True
    }
    print(json.dumps(result_data))
    sys.exit(1)

valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
images = [f for f in os.listdir(path) if f.lower().endswith(valid_extensions)]

if not images:
    result_data = {
        "success": False,
        "result_message": "No valid image files found in the directory.",
        "show_info": True
    }
    print(json.dumps(result_data))
    sys.exit(1)

success = True
min_width = float('inf')
min_height = float('inf')

min_image_name = None
not_square_images = []
wrong_sized_images = []
small_images = []
result_message = ""


def check_small_images(image_name, height, width):
    if (height < min_size or width < min_size) and image_name not in small_images:
        small_images.append(f'{image_name} ({width} x {height})')


for picture in images:
    image_path = os.path.join(path, picture)
    image = cv2.imread(image_path)
    height, width = image.shape[:2]

    check_small_images(picture.split(".")[0], height, width)

    if width != height:
        not_square_images.append(picture.split(".")[0])

    if path_id == 1 and (width != min_size or height != min_size):
        wrong_sized_images.append(picture.split(".")[0])

if path_id == 0:
    if len(small_images) > 0:
        result_message += f'There are {len(small_images)} image(s) that are smaller than {min_size} x {min_size}.\n'
        success = False
    else:
        result_message += f'All images are greater than {min_size} x {min_size}.\n'

    if len(not_square_images) > 0:
        result_message += f'There are {len(not_square_images)} image(s) that are not square.\n'
        success = False
    else:
        result_message += "All images are square.\n"

else:
    if len(wrong_sized_images) > 0:
        result_message += f'There are {len(wrong_sized_images)} image(s) that are not in correct size:\n'
        success = False

    else:
        result_message += f'All images are in correct size ({min_size} x {min_size}).'


result_data = {
    "success": success,
    "result_message": result_message,
    "small_images": small_images,
    "wrong_sized_images": wrong_sized_images,
    "not_square_images": not_square_images,
    "show_info": False
}

print(json.dumps(result_data))
