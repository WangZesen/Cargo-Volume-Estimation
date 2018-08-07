import numpy as np
import cv2
from math import sin, cos, pi, atan

def shape_detect_v1(data3D):
    dataXY = data3D[:, 0:2]
    #print dataXY.shape
    lengthLine = cv2.fitLine(dataXY, cv2.DIST_L2, 0, 0, 0.01)
    lengthNorm = np.sqrt(lengthLine[0][0] ** 2 + lengthLine[1][0] ** 2)
    lengthVector = np.array([lengthLine[0][0]/lengthNorm, lengthLine[1][0]/lengthNorm])
    widthVector = np.array([-lengthVector[1], lengthVector[0]])
    lenMax = None
    lenMin = None
    widMax = None
    widMin = None
    for point in dataXY:
        lenVal = np.dot(point, lengthVector)
        widVal = np.dot(point, widthVector)
        if lenVal>lenMax or not lenMax:
            lenMax = lenVal
        if lenVal<lenMin or not lenMin:
            lenMin = lenVal
        if widVal>widMax or not widMax:
            widMax = widVal
        if widVal<widMin or not widMin:
            widMin = widVal
    #return np.array([lengthVector, widthVector]), np.array([lenMax, lenMin]), np.array([widMax, widMin])
    return [lengthVector, widthVector], [[lenMax, lenMin], [widMax, widMin]]
    

def normalize_vector(vector):
    length = 0
    for i in vector:
        length+=vector[i]**2
    return vector/length, length


def find_rad(vector2D):
    if vector2D[0]==0:
        return vector2D[1] * pi/2
    else:
        return atan(vector2D[1]/vector2D[0])


def rotate_vector2D(vector2D, rot_rad):
    old_rad = find_rad(vector2D)
    new_rad = old_rad + rot_rad
    newVector = np.array([cos(new_rad), sin(new_rad)])
    return newVector


def shape_detect_v2(data3D):
    # X_mean = np.mean(data3D[:, 0])
    # Y_mean = np.mean(data3D[:, 1])
    # Z_mean = np.mean(data3D[:, 2])
    # meanXY = np.array([X_mean, Y_mean])
    widthVec = np.array([0, -1])
    tmpVec = np.array([0, -1])

    n = 6
    min_rad = pi/n          # 30 deg
    length = None
    for i in range(n):
        len_max = None
        # print find_rad(tmpVec) * (180 / pi),
        for point in data3D:
            # len_val = np.dot(point[0:2]-meanXY, tmpVec)
            len_val = np.dot(point[0:2], tmpVec)
            if not len_max or len_val>len_max:
                len_max = len_val
        # print len_max
        if not length or len_max<length:
            startVec = tmpVec
            length = len_max
        tmpVec = rotate_vector2D(tmpVec, min_rad)

    tmpVec = rotate_vector2D(startVec, -min_rad)
    n = 36
    min_rad = pi / n        # 5 deg
    length = None
    for i in range(int(2*(n/6))+1):
        len_max = None
        # print find_rad(tmpVec) * (180 / pi),
        for point in data3D:
            # len_val = np.dot(point[0:2] - meanXY, tmpVec)
            len_val = np.dot(point[0:2], tmpVec)
            if not len_max or len_val > len_max:
                len_max = len_val
        # print len_max
        if not length or len_max < length:
            startVec = tmpVec
            length = len_max
        tmpVec = rotate_vector2D(tmpVec, min_rad)

    tmpVec = rotate_vector2D(startVec, -min_rad)
    n = 180
    min_rad = pi / n
    length = None
    for i in range(int(2 * (n / 36)) + 1):
        len_max = None
        # print find_rad(tmpVec) * (180 / pi),
        for point in data3D:
            # len_val = np.dot(point[0:2] - meanXY, tmpVec)
            len_val = np.dot(point[0:2], tmpVec)
            if not len_max or len_val > len_max:
                len_max = len_val
        # print len_max
        if not length or len_max < length:
            widthVec = tmpVec
            length = len_max
        tmpVec = rotate_vector2D(tmpVec, min_rad)

    # print find_rad(widthVec) * (180 / pi)
    lengthVec = np.array([-widthVec[1], widthVec[0]])

    return lengthVec, widthVec
    

def cubic_construct(data3D, lengthVec, widthVec):
    x_range = np.array([None, None])
    y_range = np.array([None, None])
    z_range = np.array([None, None])
    # X_mean = np.mean(data3D[:, 0])
    # Y_mean = np.mean(data3D[:, 1])
    # Z_mean = np.mean(data3D[:, 2])
    # meanXY = np.array([X_mean, Y_mean])
    for data in data3D:
        length_val = np.dot(data[0:2], lengthVec)
        width_val = np.dot(data[0:2], widthVec)
        height_val = data[2]
        if not x_range[0] or x_range[0]>length_val:
            x_range[0] = length_val
        if not x_range[1] or x_range[1]<length_val:
            x_range[1] = length_val
        if not y_range[0] or y_range[0]>width_val:
            y_range[0] = width_val
        if not y_range[1] or y_range[1]<width_val:
            y_range[1] = width_val
        if not z_range[0] or z_range[0]>height_val:
            z_range[0] = height_val
        if not z_range[1] or z_range[1]<height_val:
            z_range[1] = height_val
    z_range[0] -= 0.02
    out_points = np.zeros([8, 3])
    count = 0

    for i in range(2):
        for j in range(2):
            for k in range(2):
                xx = x_range[i]*lengthVec
                yy = y_range[j]*widthVec
                # print(xx, yy)
                out_points[count, 0:2] = xx+yy
                # out_points[count, 0] = x_range[i]*lengthVec
                # out_points[count, 1] = y_range[j]*widthVec
                out_points[count, 2] = z_range[k]
                count += 1

    triangles = [(0, 1, 2), (2, 1, 3),
                 (0, 4, 5), (0, 1, 5),
                 (4, 6, 7), (4, 5, 7),
                 (2, 6, 3), (6, 7, 3),
                 (0, 4, 6), (0, 2, 6),
                 (1, 5, 7), (1, 3, 7)]

    length = x_range[1] - x_range[0]
    width = y_range[1] - y_range[0]
    height = z_range[1] - z_range[0]

    return out_points, triangles, [length-0.005, width-0.005, height]
