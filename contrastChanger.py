import imgaug.augmenters as iaa
import cv2
import glob
import os

# 1. Load Dataset
images = []
images_path = glob.glob("C:/Users/henry/Desktop/cansat_code/data/*.jpg")
for img_path in images_path:
    img = cv2.imread(img_path)
    images.append(img)

# 2. Image Augmentation
augmentation = iaa.Sequential([
    # 1. Flip
    iaa.Fliplr(0.5),
    iaa.Flipud(0.5),
    # 2. Affine
    iaa.Affine(translate_percent={"x": (-0.2, 0.2), "y": (-0.2, 0.2)},
               rotate=(-30, 30),
               scale=(0.5, 1.5)),
    # 3. Multiply
    iaa.Multiply((0.8, 1.2)),
    # 4. Linearcontrast
    iaa.LinearContrast((0.6, 1.4)),
    # Perform methods below only sometimes
    iaa.Sometimes(0.5,
                  # 5. GaussianBlur
                  iaa.GaussianBlur((0.0, 3.0))
                  )
])

# 3. Save Augmented Images
output_dir = "augmented_images"
os.makedirs(output_dir, exist_ok=True)

for i, img in enumerate(images):
    augmented_images = augmentation(images=[img])
    for j, augmented_img in enumerate(augmented_images):
        output_path = os.path.join(output_dir, f"augmented_{i}_{j}.jpg")
        cv2.imwrite(output_path, augmented_img)

        # Display the augmented image (optional)
        # cv2.imshow("Augmented Image", augmented_img)
        # cv2.waitKey(0)

cv2.destroyAllWindows()
