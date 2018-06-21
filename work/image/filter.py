import cv2

# Smooth Depth Frame
def smoothDepthFrame(depth):

    # Simple Median Blurring
    blur_depth = cv2.medianBlur(depth, 5)
    return blur_depth
