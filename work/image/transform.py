import cv2
import numpy as np
def frameToImage(depth, color):
    i_depth = depth.asarray() / 4500.
    i_color = cv2.resize(color.asarray(), (int(1920 / 3), int(1080 / 3)))
    return i_depth, i_color


def depthToPointCloud(device, depth):
    points = []
    for i in range(depth.height):
        for j in range(depth.width):
            pos = device.registration.getPointXYZ(depth, i, j)
            if not np.isnan(pos[0]):
                points.append(pos)
    return points
