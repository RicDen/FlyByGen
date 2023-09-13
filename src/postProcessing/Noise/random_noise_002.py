import numpy as np
import cv2
from PIL import Image
# Load the image
image = cv2.imread('Rotation_X60_MappedJets2000_close_HQ.png')

# cv2.imshow('Original Image', image)
# Generate random dark noise with the same dimensions as the image
noise = np.random.randint(0, 20, size=image.shape, dtype=np.uint8)

# Add the noise to the image
noisy_array = cv2.add(image, noise)

# Display the original and noisy images
cv2.imshow('Original Image', image)
noisy_image = Image.fromarray(noisy_array.astype('uint8'))

noisy_image.save('LowNoisy_Rotation_X60_MappedJets2000_close_HQ.png')
cv2.imshow('Noisy Image', noisy_array)

cv2.waitKey(0)
cv2.destroyAllWindows()
