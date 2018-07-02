import cv2, copy
import numpy as np
def frameToImage(depth, color, ir):
    i_depth = depth.asarray() / 4500.
    i_color = cv2.resize(color.asarray(), (int(1920 / 3), int(1080 / 3)))
    i_ir = ir.asarray() / 65535.
    return i_depth, i_color, i_ir

def depthToPointCloudWithPos(device, depth):
    points = []
    for i in range(depth.height):
        for j in range(depth.width):
            pos = list(device.registration.getPointXYZ(depth, i, j))
            if not np.isnan(pos[0]):
                points.append([pos[0], pos[1], pos[2], i, j])
    return points


def depthToPointCloud(device, depth):
    points = []
    for i in range(depth.height):
        for j in range(depth.width):
            pos = list(device.registration.getPointXYZ(depth, i, j))
            if not np.isnan(pos[0]):
                points.append(pos)
    return points

def depthToPointCloudWithMask(device, depth, mask):
    points = []
    for i in range(depth.height):
        for j in range(depth.width):
            if mask[i][j] == True:
                pos = list(device.registration.getPointXYZ(depth, i, j))
                if not np.isnan(pos[0]):
                    points.append(pos)
    return points

def grayToThreeChannels(gray):
    tem = copy.copy(gray)
    tem = np.array([tem])
    tem = np.concatenate((tem, tem, tem), axis = 0)
    return np.moveaxis(tem, 0, -1)
