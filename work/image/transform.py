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

def depthToPointCloudWithDownSample(device, depth, mask, d):
    points = []
    for i in range(depth.height):
        for j in range(depth.width):
            if mask[i][j] == True and (i + j) % d == 0:
                try:
                    state = True
                    for ii in range(5):
                        for jj in range(5):
                            state = state and mask[i + ii - 2][j + jj - 2]
                    if state:
                        pos = list(device.registration.getPointXYZ(depth, i, j))
                        if (not np.isnan(pos[0])) and (pos[0] ** 2 + pos[1] ** 2 + pos[2] ** 2 <= 2.2):
                            points.append(pos)
                except:
                    pass

    return points

def depthToPointCloudWithDownSampleAndPlane(device, depth, mask, d, plane):
    points = []
    tmp_scale = np.sqrt(plane[0] ** 2 + plane[1] ** 2 + 1)
    for i in range(depth.height):
        for j in range(depth.width):
            if mask[i][j] == True and (i + j) % d == 0:
                try:
                    state = True
                    for ii in range(11):
                        for jj in range(11):
                            state = state and mask[i + ii - 5][j + jj - 5]
                    if state:
                        pos = list(device.registration.getPointXYZ(depth, i, j))
                        if (not np.isnan(pos[0])) and (pos[0] ** 2 + pos[1] ** 2 + pos[2] ** 2 <= 2.2):
                            dist = (pos[0] * plane[0] + pos[1] * plane[1] - (pos[2] - plane[2])) / tmp_scale
                            if abs(dist) > 0.05:
                                points.append(pos)
                except:
                    pass

    return points

def depthToPointCloudWithMask(device, depth, mask):
    points = []
    for i in range(depth.height):
        for j in range(depth.width):
            if mask[i][j] == True:
                pos = list(device.registration.getPointXYZ(depth, i, j))
                if (not np.isnan(pos[0])) and (pos[0] ** 2 + pos[1] ** 2 + pos[2] ** 2 <= 2.2):
                    points.append(pos)
    return points

def depthToPoint(device, depth, x, y):
    min_dist = 2 ** 31
    feature_pos = None
    for i in range(3):
        for j in range(3):
            try:
                pos = list(device.registration.getPointXYZ(depth, x + i, y + j))
                if (j ** 2 + i ** 2 < min_dist) and (not np.isnan(pos[0])):
                    feature_pos = copy.copy(pos)
            except:
                pass
    return feature_pos

def grayToThreeChannels(gray):
    tem = copy.copy(gray)
    tem = np.array([tem])
    tem = np.concatenate((tem, tem, tem), axis = 0)
    return np.moveaxis(tem, 0, -1)
