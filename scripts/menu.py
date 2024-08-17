import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import PIL
from PIL import Image, ImageTk
import subprocess
import json
import threading

target_size = 300
is_images_valid = False
is_resized_images_valid = False
threshold = 0.6


def insert_image(text_widget, image_path):
    image = Image.open(image_path)
    image.thumbnail((150, 150))
    photo = ImageTk.PhotoImage(image)
    text_widget.image_create(tk.END, image=photo)
    text_widget.image_refs.append(photo)


def check_images(path_id, size):
    result = subprocess.run(['python', 'check_images.py', str(path_id), str(size)], capture_output=True, text=True)
    output = result.stdout
    data = json.loads(output)
    global is_images_valid
    global is_resized_images_valid

    if not data["success"]:
        if data["show_info"]:
            messagebox.showerror("Error", data["result_message"])
        else:
            result_window = tk.Toplevel(root)
            result_window.title("Image Check Result")
            lbl_message = tk.Label(result_window, text=data["result_message"], anchor='w', justify='left')
            lbl_message.pack(pady=10, padx=10)
            text_output = tk.Text(result_window, height=10, width=50)
            text_output.pack(pady=10, padx=10)

            if "not_square_images" in data and len(data["not_square_images"]) > 0:
                text_output.insert(tk.END, "--- Images that are not square ---\n")
                for image in data["not_square_images"]:
                    text_output.insert(tk.END, image + "\n")

            if "wrong_sized_images" in data and len(data["wrong_sized_images"]) > 0:
                text_output.insert(tk.END, "--- Images that are not in correct size ---\n")
                for image in data["wrong_sized_images"]:
                    text_output.insert(tk.END, image + "\n")

            if "small_images" in data and len(data["small_images"]) > 0:
                text_output.insert(tk.END, f'--- Images smaller than {target_size} x {target_size} ---\n')
                for image in data["small_images"]:
                    text_output.insert(tk.END, image + "\n")

            text_output.config(state=tk.DISABLED)

            btn_close = tk.Button(result_window, text="Close", command=result_window.destroy)
            btn_close.pack(pady=10)

    else:
        if path_id == 0:
            is_images_valid = True
        else:
            is_resized_images_valid = True
        messagebox.showinfo("Success", data["result_message"])


def resize_images():
    if is_images_valid:
        progress_window = tk.Toplevel(root)
        progress_window.title("Resizing Images")

        lbl_progress = tk.Label(progress_window, text="Resizing images, please wait...")
        lbl_progress.pack(pady=10, padx=10)

        progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
        progress_bar.pack(pady=10, padx=10)
        progress_bar.start()

        def run_resize():
            try:
                subprocess.run(
                    ['python', 'resize_images.py', "../data/faces", str(target_size), "../data/resized_faces"])
                progress_bar.stop()
                progress_window.destroy()
                messagebox.showinfo("Resize Complete", "Images have been resized and saved.")

            except SystemError:
                progress_bar.stop()
                progress_window.destroy()
                messagebox.showerror("Error", "An error occurred during resizing.")

        threading.Thread(target=run_resize).start()
    else:
        check_images(0, target_size)
        if is_images_valid:
            resize_images()
        else:
            messagebox.showerror("Error", "There is a problem with your faces folder!")


def set_target_size():
    global target_size
    global is_images_valid
    global is_resized_images_valid

    is_images_valid = False
    is_resized_images_valid = False

    try:
        target_size = int(entry_target_size.get())
        messagebox.showinfo("Success", f"Target size set to {target_size}.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")


def face_recognizer(threshold_value):
    if is_images_valid and is_resized_images_valid:
        progress_window = tk.Toplevel(root)
        progress_window.title("Face Recognizer")

        lbl_progress = tk.Label(progress_window, text="Face recognition is on progress, please wait...")
        lbl_progress.pack(pady=10, padx=10)

        progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
        progress_bar.pack(pady=10, padx=10)
        progress_bar.start()

        def run_recognition():
            try:
                result = subprocess.run(['python', 'face_recognizer.py', str(threshold_value)], capture_output=True,
                                        text=True)
                output = result.stdout
                data = json.loads(output)
                progress_bar.stop()
                progress_window.destroy()
                messagebox.showinfo("Complete", "Face recognition has been completed")

                result_window = tk.Toplevel(root)
                result_window.title("Face Recognition Result")

                text_output = tk.Text(result_window, height=40, width=60)
                text_output.pack(pady=10, padx=10)
                text_output.image_refs = []

                for prediction in data["predictions"]:
                    insert_image(text_output, prediction["path"])
                    text_output.insert(tk.END, f'\n{prediction["prediction"]}\n{prediction["distance"]}\n\n')

                text_output.config(state=tk.DISABLED)

                btn_close = tk.Button(result_window, text="Close", command=result_window.destroy)
                btn_close.pack(pady=10)

            except SystemError:
                progress_bar.stop()
                progress_window.destroy()
                messagebox.showerror("Error", "An error occurred during process.")

        threading.Thread(target=run_recognition).start()
    else:
        if not is_images_valid:
            check_images(0, target_size)
        if not is_resized_images_valid:
            check_images(1, target_size)
        if is_images_valid and is_resized_images_valid:
            face_recognizer(threshold_value)
        else:
            messagebox.showerror("Error", "There is a problem with your images!")


def set_threshold():
    global threshold

    try:
        threshold = float(entry_threshold_value.get())
        messagebox.showinfo("Success", f"Threshold set to {threshold}.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid value.")


def open_camera():
    if is_images_valid and is_resized_images_valid:
        progress_window = tk.Toplevel(root)
        progress_window.title("Face Recognizer with Camera")

        lbl_progress = tk.Label(progress_window, text="Your camera is opening, please wait...")
        lbl_progress.pack(pady=10, padx=10)

        progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
        progress_bar.pack(pady=10, padx=10)
        progress_bar.start()

        lbl_status = tk.Label(progress_window, text="Camera is now open and will be running...")
        lbl_status.pack(pady=10)

        def run_recognition():
            try:
                result = subprocess.run(['python', 'camera.py', str(threshold)], capture_output=True, text=True)
                output = result.stdout
                data = json.loads(output)

                progress_bar.stop()
                progress_window.destroy()

                if not data["success"]:
                    messagebox.showerror("Error", data["message"])

            except Exception as e:
                progress_bar.stop()
                lbl_status.config(text=f"Error: {str(e)}")

        threading.Thread(target=run_recognition).start()

    else:
        if not is_images_valid:
            check_images(0, target_size)
        if not is_resized_images_valid:
            check_images(1, target_size)
        if is_images_valid and is_resized_images_valid:
            open_camera()
        else:
            messagebox.showerror("Error", "There is a problem with your images!")


root = tk.Tk()

root.title("Face Recognizer by 7endar")
root.geometry("400x300")
root.minsize(400, 300)
root.maxsize(400, 300)

frame_target_size = tk.Frame(root)
frame_target_size.pack(pady=10, padx=10, fill='x')

lbl_size = tk.Label(frame_target_size, text="Target Size:")
lbl_size.grid(row=0, column=0, padx=(0, 10), sticky='w')

entry_target_size = tk.Entry(frame_target_size, width=5)
entry_target_size.grid(row=0, column=1, padx=(0, 10))
entry_target_size.insert(0, str(target_size))

btn_set_size = tk.Button(frame_target_size, text="Set Size", command=set_target_size)
btn_set_size.grid(row=0, column=2)

separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
separator.pack(fill='x', pady=10)

frame_controls = tk.Frame(root)
frame_controls.pack(pady=10, padx=10, fill='x')

btn_check_faces = tk.Button(frame_controls, text="Check Faces Folder", command=lambda: check_images(0, target_size))
btn_check_faces.grid(row=0, column=0, padx=5)

btn_resize_images = tk.Button(frame_controls, text="Resize Images", command=resize_images)
btn_resize_images.grid(row=0, column=1, padx=5)

btn_check_resized_faces = tk.Button(frame_controls, text="Check Resized Faces Folder", command=lambda: check_images(1, target_size))
btn_check_resized_faces.grid(row=0, column=2, padx=5)

separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
separator.pack(fill='x', pady=10)

frame_threshold = tk.Frame(root)
frame_threshold.pack(pady=10, padx=10, fill='x')

lbl_threshold = tk.Label(frame_threshold, text="Threshold:")
lbl_threshold.grid(row=0, column=0, padx=(0, 10), sticky='w')

entry_threshold_value = tk.Entry(frame_threshold, width=5)
entry_threshold_value.grid(row=0, column=1, padx=(0, 10))
entry_threshold_value.insert(0, str(threshold))

btn_set_threshold = tk.Button(frame_threshold, text="Set Threshold", command=set_threshold)
btn_set_threshold.grid(row=0, column=2)

separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
separator.pack(fill='x', pady=10)

frame_recognition = tk.Frame(root)
frame_recognition.pack(pady=10, padx=10, fill='x')

frame_recognition.columnconfigure(0, weight=1)
frame_recognition.columnconfigure(1, weight=1)

btn_face_recognizer = tk.Button(frame_recognition, text="Face Recognizer From Folder", command=lambda: face_recognizer(threshold))
btn_face_recognizer.grid(row=0, column=0, padx=5)

btn_open_camera = tk.Button(frame_recognition, text="Face Recognizer From Camera", command=open_camera)
btn_open_camera.grid(row=0, column=1, padx=5)

btn_close = tk.Button(root, text="Close", command=root.destroy)
btn_close.pack(pady=10)

root.mainloop()
