# import mpl_toolkits.mplot3d as a3
import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.colors as colors
# from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import scipy as sp
import copy, math
from random import randint

class Facet():
    def __init__(self, a, b, c, n, conn):
        conn[a][b] = n
        conn[b][c] = n
        conn[c][a] = n
        self.a = a
        self.b = b
        self.c = c
        self.flag = True

def dist(v):
    return np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)

def normalize(v):
    length = dist(v)
    v = v / length

def onLine(x, y, z):
    if dist(np.cross(x - y, x - z)) > 1e-12:
        return False
    return True

def onPlane(a, b, c, d):
    if abs(np.dot(np.cross(b - a, c - a), d - a)) > 1e-12:
        return False
    return True

def visiblePoint(a, b, c, d):
    if np.dot(np.cross(b - a, c - a), d - a) > 1e-12:
        return True
    return False

def visiblePlane(points, facet, d):
    a = points[facet.b] - points[facet.a]
    b = points[facet.c] - points[facet.a]
    c = points[d] - points[facet.a]
    if np.dot(np.cross(a, b), c) > 1e-12:
        return True
    return False

def visualize(points, facets):
    ax = a3.Axes3D(plt.figure())
    fixed_color = sp.rand(3);
    triangle = []
    for k in range(len(facets)):
        if facets[k].flag:
            ax.scatter(points[facets[k].a][0], points[facets[k].a][1], points[facets[k].a][2], c = 'r')
            ax.scatter(points[facets[k].b][0], points[facets[k].b][1], points[facets[k].b][2], c = 'r')
            ax.scatter(points[facets[k].c][0], points[facets[k].c][1], points[facets[k].c][2], c = 'r')
            triangle.append([(points[facets[k].a][0], points[facets[k].a][1], points[facets[k].a][2]), \
                            (points[facets[k].b][0], points[facets[k].b][1], points[facets[k].b][2]), \
                            (points[facets[k].c][0], points[facets[k].c][1], points[facets[k].c][2])])
        poly = Poly3DCollection(triangle)
        poly.set_edgecolor('k')
        poly.set_alpha(1)

        ax.add_collection3d(poly)

    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.set_zlabel("Z axis")

    ax.set_xlim3d(-0.15, 0.15)
    ax.set_ylim3d(-0.15, 0.15)
    ax.set_zlim3d(-0.15, 0.15)

    plt.show()

def deleteFacets(points, facets, conn, facet_n, n, d):
    facets[n].flag = False

    if facets[conn[facets[n].b][facets[n].a]].flag:
        if (not visiblePlane(points, facets[conn[facets[n].b][facets[n].a]], d)):
            facet_n = deleteFacets(points, facets, conn, facet_n, conn[facets[n].b][facets[n].a], d)
        else:
            new_facet = Facet(facets[n].a, facets[n].b, d, facet_n, conn)
            facet_n += 1
            facets.append(new_facet)
    if facets[conn[facets[n].c][facets[n].b]].flag:
        if (not visiblePlane(points, facets[conn[facets[n].c][facets[n].b]], d)):
            facet_n = deleteFacets(points, facets, conn, facet_n, conn[facets[n].c][facets[n].b], d)
        else:
            new_facet = Facet(facets[n].b, facets[n].c, d, facet_n, conn)
            facet_n += 1
            facets.append(new_facet)
    if facets[conn[facets[n].a][facets[n].c]].flag:
        if (not visiblePlane(points, facets[conn[facets[n].a][facets[n].c]], d)):
            facet_n = deleteFacets(points, facets, conn, facet_n, conn[facets[n].a][facets[n].c], d)
        else:
            new_facet = Facet(facets[n].c, facets[n].a, d, facet_n, conn)
            facet_n += 1
            facets.append(new_facet)
    return facet_n

def convexHull2D(_points):

    points = _points[:, 0:2]

    n = points.shape[0]

    hull = [np.argmin(points[:, 1])]

    def dist(x, y):
        return np.sqrt(np.sum(np.multiply(x - y, x - y)))

    def calAngle(x, y):
        cos_v = (y[0] - x[0]) / dist(x, y)
        return math.acos(cos_v)

        return 1e10

    def cross_prod(x, y, z):
        return np.cross(y - x, z - x) < 0

    angles = []
    for i in range(n):
        if i != hull[0]:
            angles.append(calAngle(points[hull[0]], points[i]))
        else:
            angles.append(1e10)
    angles_arg = np.argsort(angles)

    hull.append(angles_arg[0])

    for i in range(1, n):

        if angles[angles_arg[i]] < 1e5:
            top = len(hull) - 1

            while cross_prod(points[hull[top - 1]], points[hull[top]], points[angles_arg[i]]):
                # print (hull)
                hull.pop()
                # print (hull, '!')
                top -= 1
            hull.append(angles_arg[i])
    hull = np.array(hull)
    return _points[hull, :]



def ConstructConvexHull(points):
    np.random.shuffle(points)

    conv_points = convexHull2D(points)
    # print (points.shape)


    if conv_points.shape[0] <= 500:
        points = np.vstack([conv_points, points[0:500 - conv_points.shape[0], :]])
    else:
        np.random.shuffle(conv_points)
        points = conv_points[0:500, :]
    points = points - np.mean(points, axis=0)
    flag = [True for i in range(points.shape[0])]
    facets = []
    facet_n = 0
    conn = [{} for i in range(points.shape[0])]

    flag[0] = False
    flag[1] = False
    init_points = [0, 1]

    for i in range(2, points.shape[0]):
        if not onLine(points[init_points[0]], points[init_points[1]], i):
            init_points.append(i)
            flag[i] = False
            break

    for i in range(3, points.shape[0]):
        if flag[i] and (not onPlane(points[init_points[0]], points[init_points[1]], points[init_points[2]], i)):
            init_points.append(i)
            flag[i] = False
            break

    for i in range(4):
        a = init_points[i]
        b = init_points[(i + 1) % 4]
        c = init_points[(i + 2) % 4]
        d = init_points[(i + 3) % 4]
        if not visiblePoint(points[a], points[b], points[c], points[d]):
            b, c = c, b
        new_facet = Facet(a, b, c, facet_n, conn)
        facets.append(new_facet)
        facet_n += 1

    for i in range(2, points.shape[0]):
        if flag[i]:
            for j in range(len(facets)):
                if facets[j].flag and (not visiblePlane(points, facets[j], i)):
                    facet_n = deleteFacets(points, facets, conn, facet_n, j, i)
                    break

    return points, facets


if __name__ == '__main__':
    '''
    f = open('Save_Point_Cloud/0/000_log.txt', 'r')
    lines = f.readlines()
    graph_n = int(lines[1])

    points = copy.copy(raw_points[0])
    for i in range(1, graph_n):
        points = np.concatenate([points, raw_points[i]], axis = 0)
    f.close()
    '''

    points = np.load('tmp/final.npy')
    final_points, facets = ConstructConvexHull(points)
    visualize(final_points, facets)
