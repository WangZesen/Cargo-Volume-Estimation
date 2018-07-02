import cv2

# Smooth Depth Frame
def smoothFrame(depth):

    # Simple Median Blurring
    blur_depth = cv2.medianBlur(depth, 5)
    return blur_depth
