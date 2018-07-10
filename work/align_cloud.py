import numpy as np
import math
import scipy.io as sio

strip_length = 0.25
graph_n = [0, 0]
cargo_no = 0

def read_point_cloud(device_no, cargo_no, graph_no):
    filepath = 'Save_Point_Cloud0/{}/{}_pc_offset_{}.npy'.format(device_no, str(cargo_no).zfill(3), str(graph_no).zfill(4))
    return np.load(filepath)

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

def rotatePointAroundZ(point, theta):
    theta = - theta

def rotatePoint(point, theta1, theta2):
    theta1 = -theta1
    theta2 = -theta2
    point[1], point[2] = point[1] * math.cos(theta1) - point[2] * math.sin(theta1), point[1] * math.sin(theta1) + point[2] * math.cos(theta1)
    point[0], point[2] = point[2] * math.sin(theta2) + point[0] * math.cos(theta2), point[2] * math.cos(theta2) - point[0] * math.sin(theta2)


point_cloud = []
features = [None, None]
strip_dir = [None, None]
plane_params = [None, None]
theta = [[None, None], [None, None]]
z_level = [None, None]
for i in range(2):
    point_cloud.append(read_point_cloud(i, cargo_no, 0))
    f = open('Save_Point_Cloud0/{}/{}_log.txt'.format(i, str(cargo_no).zfill(3)), 'r')
    lines = f.readlines()
    graph_n[i] = int(lines[1])

    raw_feature = lines[5].split(', ')
    features[i] = [float(raw_feature[0]), float(raw_feature[1]), float(raw_feature[2])]

    raw_strip_dir = lines[4].split(', ')
    strip_dir[i] = [float(raw_strip_dir[0]), float(raw_strip_dir[1]), float(raw_strip_dir[2])]

    raw_plane_params = lines[2].split(', ')
    plane_params[i] = [float(raw_plane_params[0]), float(raw_plane_params[1]), float(raw_plane_params[2])]

    for j in range(1, graph_n[i]):
        point_cloud[i] = np.concatenate([point_cloud[i], read_point_cloud(i, cargo_no, j)])




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

print (strip_dir)

# Calculate Corresponding Feature Point
offset = [0, 0, 0]
for i in range(3):
    features[0][i] += strip_dir[0][i] * strip_length
    offset[i] = features[0][i] - features[1][i]

'''
for i in range(point_cloud[0].shape[0]):
    for j in range(2):
        point_cloud[0][i][j] = 2 * features[0][j] - point_cloud[0][i][j]
'''

for i in range(point_cloud[1].shape[0]):
    for j in range(3):
        point_cloud[1][i][j] += offset[j]

sio.savemat('tmp/test0.mat', {'matrix1': point_cloud[0].tolist(), 'matrix2': point_cloud[1].tolist()})
# sio.savemat('tmp/test0.mat', {'matrix1': point_cloud[0].tolist(), 'matrix2': [[0, 0, 0]]})
