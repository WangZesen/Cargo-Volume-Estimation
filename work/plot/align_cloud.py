import numpy as np
import math
import scipy.io as sio
import scipy.spatial as spatial

def voxelGridFilter(points):
    part = 110
    grid = [[[[] for i in range(part)] for j in range(part)] for k in range(part)]
    xmin = -1.3
    xmax = 1.3
    ymin = -1
    ymax = 1
    zmin = 0.5
    zmax = 1.8

    for i in range(points.shape[0]):
        x_grid = int((points[i][0] - xmin) / (xmax - xmin) * part)
        y_grid = int((points[i][1] - ymin) / (ymax - ymin) * part)
        z_grid = int((points[i][2] - zmin) / (zmax - zmin) * part)
        grid[x_grid][y_grid][z_grid].append(i)

    for i in range(part):
        for j in range(part):
            for k in range(part):
                if not (len(grid[i][j][k]) == 0):
                    points[np.array(grid[i][j][k]), :] = np.mean(points[np.array(grid[i][j][k]), :], axis = 0)

def getRotateToXYPlane(plane_params):
    new_plane_params = [plane_params[0], plane_params[1], plane_params[2]]
    theta1 = math.atan(plane_params[1])

    a = new_plane_params[0] / (new_plane_params[1] * math.sin(theta1) + math.cos(theta1))
    b = 0
    c = new_plane_params[2] / (new_plane_params[1] * math.sin(theta1) + math.cos(theta1))

    new_plane_params = [a, b, c]
    theta2 = math.atan(- new_plane_params[0])
    a = 0
    b = 0
    c = new_plane_params[2] / (math.cos(theta2) - math.sin(theta2) * new_plane_params[0])
    new_plane_params = [a, b, c]
    return theta1, theta2, new_plane_params[2]

def rotateAroundX(points, theta):
    theta = - theta
    for i in range(points.shape[0]):
        points[i][1], points[i][2] = points[i][1] * math.cos(theta) - points[i][2] * math.sin(theta), points[i][1] * math.sin(theta) + points[i][2] * math.cos(theta)

def rotateAroundY(points, theta):
    theta = - theta
    for i in range(points.shape[0]):
        points[i][0], points[i][2] = points[i][2] * math.sin(theta) + points[i][0] * math.cos(theta), points[i][2] * math.cos(theta) - points[i][0] * math.sin(theta)

def rotateAroundZ(points, theta):
    theta = - theta
    for i in range(points.shape[0]):
        points[i][0], points[i][1] = points[i][0] * math.cos(theta) - points[i][1] * math.sin(theta), points[i][0] * math.sin(theta) + points[i][1] * math.cos(theta)

def rotatePointAroundZ(point, theta):
    theta = - theta
    point[0], point[1] = point[0] * math.cos(theta) - point[1] * math.sin(theta), point[0] * math.sin(theta) + point[1] * math.cos(theta)

def rotatePoint(point, theta1, theta2):
    theta1 = -theta1
    theta2 = -theta2
    point[1], point[2] = point[1] * math.cos(theta1) - point[2] * math.sin(theta1), point[1] * math.sin(theta1) + point[2] * math.cos(theta1)
    point[0], point[2] = point[2] * math.sin(theta2) + point[0] * math.cos(theta2), point[2] * math.cos(theta2) - point[0] * math.sin(theta2)

def alignPointCloud(cargo_no):
    strip_length = 0.30

    point_cloud = [None, None]
    features = [None, None]
    strip_dir = [None, None]
    plane_params = [None, None]
    theta = [[None, None], [None, None]]
    z_level = [None, None]
    graph_n = [None, None]

    for i in range(2):
        # point_cloud.append(read_point_cloud(i, cargo_no, 0))

        f = open('./../Save_Point_Cloud/{}/{}_log.txt'.format(i, str(cargo_no).zfill(3)), 'r')

        lines = f.readlines()
        graph_n[i] = int(lines[1])

        raw_feature = lines[5].split(', ')
        features[i] = [float(raw_feature[0]), float(raw_feature[1]), float(raw_feature[2])]

        raw_strip_dir = lines[4].split(', ')
        strip_dir[i] = [float(raw_strip_dir[0]), float(raw_strip_dir[1]), float(raw_strip_dir[2])]

        raw_plane_params = lines[2].split(', ')
        plane_params[i] = [float(raw_plane_params[0]), float(raw_plane_params[1]), float(raw_plane_params[2])]

        raw_point_cloud = np.load('./../Save_Point_Cloud/{}/{}_pc_offset.npy'.format(i, str(cargo_no).zfill(3)))

        point_cloud[i] = raw_point_cloud[0]

        for j in range(1, graph_n[i]):
            point_cloud[i] = np.concatenate([point_cloud[i], raw_point_cloud[j]])

    voxelGridFilter(point_cloud[0])
    voxelGridFilter(point_cloud[1])

    theta[0][0], theta[0][1], z_level[0] = getRotateToXYPlane(plane_params[0])
    rotateAroundX(point_cloud[0], theta[0][0])
    rotateAroundY(point_cloud[0], theta[0][1])
    rotatePoint(features[0], theta[0][0], theta[0][1])
    rotatePoint(strip_dir[0], theta[0][0], theta[0][1])

    theta[1][0], theta[1][1], z_level[1] = getRotateToXYPlane(plane_params[1])
    rotateAroundX(point_cloud[1], theta[1][0])
    rotateAroundY(point_cloud[1], theta[1][1])
    rotatePoint(features[1], theta[1][0], theta[1][1])
    rotatePoint(strip_dir[1], theta[1][0], theta[1][1])

    k = strip_dir[0][0] / strip_dir[0][1]
    align_theta = math.atan((strip_dir[1][0] - k * strip_dir[1][1]) / (k * strip_dir[1][0] + strip_dir[1][1]))

    rotateAroundZ(point_cloud[1], - align_theta)
    rotatePointAroundZ(features[1], - align_theta)
    rotatePointAroundZ(strip_dir[1], - align_theta)


    # Calculate Corresponding Feature Point
    offset = [0, 0, 0]
    for i in range(3):
        features[0][i] += strip_dir[0][i] * strip_length
        offset[i] = features[0][i] - features[1][i]

    for i in range(point_cloud[0].shape[0]):
        for j in range(2):
            point_cloud[0][i][j] = 2 * features[0][j] - point_cloud[0][i][j]

    for i in range(point_cloud[1].shape[0]):
        for j in range(3):
            point_cloud[1][i][j] += offset[j]

    final_point_cloud = np.concatenate([point_cloud[0], point_cloud[1]], axis = 0)

    mean = np.mean(final_point_cloud, axis = 0)

    final_point_cloud = final_point_cloud - mean
    dist = np.multiply(final_point_cloud[:, 0], final_point_cloud[:, 0]) + np.multiply(final_point_cloud[:, 1], final_point_cloud[:, 1]) \
            + np.multiply(final_point_cloud[:, 2], final_point_cloud[:, 2])
    arg = np.argsort(dist)

    filtered_point_cloud = []

    mean_dist = dist[arg[0]]

    for i in range(1, final_point_cloud.shape[0]):
        if dist[arg[i]] > mean_dist * 3:
            break
        else:
            mean_dist = (mean_dist * i + dist[arg[i]]) / (i + 1)
            filtered_point_cloud.append(final_point_cloud[arg[i]])
    filtered_point_cloud = np.array(filtered_point_cloud)
    filtered_point_cloud = filtered_point_cloud - np.mean(filtered_point_cloud, axis = 0)
    return filtered_point_cloud

if __name__ == '__main__':
    points = alignPointCloud(0)

    print (points.shape)

    sio.savemat('tmp/final.mat', {'matrix1': points})
    np.save('tmp/final.npy', points)
