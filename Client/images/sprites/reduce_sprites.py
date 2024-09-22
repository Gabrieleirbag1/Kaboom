import os
from PIL import Image

def resize_images_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.png'):
                file_path = os.path.join(root, file)
                resize_image(file_path)

def resize_image(file_path):
    with Image.open(file_path) as img:
        # Calculate the new size
        new_size = (img.width // 2, img.height // 2)
        # Resize the image
        resized_img = img.resize(new_size, Image.ANTIALIAS)
        # Save the resized image
        resized_img.save(file_path)
        print(f"Resized {file_path} to {new_size}")

# Example usage
folder_path = '/home/frigiel/Bureau/avatars/'  # Replace with the path to your folder
resize_images_in_folder(folder_path)