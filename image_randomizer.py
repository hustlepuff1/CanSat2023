import os
import random
from PIL import Image, ImageEnhance


def change_contrast(image, factor):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def random_rotate(image):
    angle = random.randint(0, 360)
    return image.rotate(angle)


def process_images(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(directory, filename)

            # Open the image using Pillow
            image = Image.open(image_path)

            # Change contrast
            contrast_factor = random.uniform(0.5, 1.5)
            image = change_contrast(image, contrast_factor)

            # Rotate randomly
            image = random_rotate(image)

            # Save the modified image
            new_filename = f"modified_{filename}"
            new_image_path = os.path.join(directory, new_filename)
            image.save(new_image_path)

            print(f"Processed: {image_path} -> {new_image_path}")


if __name__ == "__main__":
    input_directory = "C:/Users/henry/Desktop/cansat_code/data"
    process_images(input_directory)
