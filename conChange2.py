import imgaug.augmenters as iaa
import cv2
import glob
import os
import random

# 1. Load Dataset
images = []
images_path = glob.glob("C:/Users/henry/Desktop/cansat_code/data/*.jpg")
for img_path in images_path:
    img = cv2.imread(img_path)
    images.append(img)

# 2. Image Augmentation and Save Augmented Images
output_dir = "augmented_images"
os.makedirs(output_dir, exist_ok=True)

num_images_to_generate = 5

for i, img in enumerate(images):
    for j in range(num_images_to_generate):
        # Random contrast level between 0.6 and 1.4
        contrast_factor = random.uniform(0.6, 1.4)
        augmentation = iaa.LinearContrast(contrast_factor)
        augmented_img = augmentation(image=img)

        output_path = os.path.join(output_dir, f"augmented_{i}_{j}.jpg")
        cv2.imwrite(output_path, augmented_img)

        # Display the augmented image (optional)
        # cv2.imshow("Augmented Image", augmented_img)
        # cv2.waitKey(0)

cv2.destroyAllWindows()
