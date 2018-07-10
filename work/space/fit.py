import numpy as np

def fitPlane(points):
    np_points = np.array(points)

    mean = np.mean(np_points, 0)
    np_points = np_points - mean

    x = np_points[:, 0]
    y = np_points[:, 1]
    z = np_points[:, 2]

    xx = np.dot(x, x)
    xy = np.dot(x, y)
    xz = np.dot(x, z)
    yy = np.dot(y, y)
    yz = np.dot(y, z)

    A = (xz * yy - yz * xy) / (xx * yy - xy ** 2)
    B = (yz * xx - xz * xy) / (xx * yy - xy ** 2)
    C = mean[2] - A * mean[0] - B * mean[1]

    return (A, B, C)

def getPointsOnPlane(params):
    points = []
    scale = 10

    for i in range(scale):
        for j in range(scale):
            points.append([2. * i / scale, 2. * j / scale, 2. * i / scale * params[0] + 2. * j / scale * params[1] + params[2]])
    return points


def getReflectiveDirection(plane_params, direction):
    plane_n = np.array([plane_params[0], plane_params[1], -1])
    line_n = np.array([direction[0], direction[1], direction[2]])
    strip_n = np.cross(plane_n, line_n)
    # Normalize
    strip_n = strip_n / np.sqrt(np.dot(strip_n, strip_n))
    return strip_n
