# -*- coding: utf-8 -*-
"""
Created on Sun Jun 24 14:04:53 2018

@author: yier_
"""

import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D
from transforms3d.euler import euler2mat, mat2euler
import rmsd

def plot3d(A, B):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    Ax = A[:,0]
    Ay = A[:,1]
    Az = A[:,2]

    Bx = B[:,0]
    By = B[:,1]
    Bz = B[:,2]

    ax.plot(Ax, Ay, Az, c = 'r', marker = 'o', label='parametric curve')
    ax.plot(Bx, By, Bz, c = 'b', marker = '^', label='parametric curve')
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()
    return

def generate_set(A, B):
    Asize = A.shape[0]
    Bsize = B.shape[0]
    temp = np.zeros((max(Asize, Bsize), 3))
    if (Asize < Bsize):
        temp += rmsd.centroid(A)
        temp[0:Asize] = A
        A = temp
    else:
        temp += rmsd.centroid(B)
        temp[0:Bsize] = B
        B = temp
    return A, B

x_angle = np.pi / 3
y_angle = np.pi / 4
z_angle = np.pi / 5
R = euler2mat(x_angle, y_angle, z_angle, 'sxyz')
'''
a = np.array([0, 0, 0])
b = np.array([10, 10, 0])
c = np.array([20, 0, 0])
'''
A = 10 * np.random.rand(50, 3)
B = np.dot(A, R)
extra = 10*np.random.rand(10, 3)
#B = np.append(B, extra, axis = 0)
B += random.uniform(-10, 10)
#np.random.shuffle(B)
#A, B = generate_set(A, B)
plot3d(A, B)
print("Normal RMSD", rmsd.rmsd(A, B))

# Manipulate
A -= rmsd.centroid(A)
B -= rmsd.centroid(B)
plot3d(A, B)
print("Translated RMSD", rmsd.rmsd(A, B))

markA = A[0:3, :]
markB = B[0:3, :]
U = rmsd.kabsch(markA, markB)
A = np.dot(A, U)

plot3d(A, B)
print("Rotated RMSD", rmsd.rmsd(A, B))

#data projection
d = 12
unit = 0.01
maxindex = int(d / unit)
Aindex = np.floor(A / unit)
Bindex = np.floor(B / unit)
Aindex -= np.min(Aindex)
Bindex -= np.min(Bindex)
Axy = Aindex[:, 0:2]
Bxy = Bindex[:, 0:2]

forward = []
for point in Aindex:
    for i in range(maxindex):
        if (point[2] + i > maxindex):
            break
        temp = point
        temp[2] += i
        forward.append(temp)
        
for point in Bindex:
    for i in range(maxindex):
        if (point[2] + i > maxindex):
            break
        temp = point
        temp[2] += i
        forward.append(temp)
        
forward = np.asarray(forward)

back = []
for point in Aindex:
    for i in range(maxindex):
        if (point[2] - i <= 0):
            break
        temp = point
        temp[2] -= i
        back.append(temp)
        
for point in Bindex:
    for i in range(maxindex):
        if (point[2] - i <= 0):
            break
        temp = point
        temp[2] -= i
        back.append(temp)
back = np.asarray(back)


'''
A = np.array([[0, 0, 0],
              [0, 0, 1],
              [0, 1, 0],
              [0, 1, 1],
              [1, 0, 0],
              [1, 0, 1],
              [1, 1, 0],
              [1, 1, 1],
              [0.5, 0, 0],
              [0.5, 0, 1],
              [0.5, 1, 0],
              [0.5, 1, 1],
              [0, 0.5, 0],
              [0, 0.5, 1],
              [1, 0.5, 0],
              [1, 0.5, 1],
              [0, 0, 0.5],
              [0, 1, 0.5],
              [1, 0, 0.5],
              [1, 1, 0.5],
              [0.5, 0.5, 0],
              [0.5, 0.5, 1],
              [0.5, 0, 0.5],
              [0.5, 1, 0.5],
              [0, 0.5, 0.5],
              [1, 0.5, 0.5],
              [0.5, 0.5, 0.5]])
#A = A - 0.5
A = np.array([[-0.98353,        1.81095,       -0.03140],
              [ 0.12683,        1.80418,       -0.03242],
              [-1.48991,        3.22740,        0.18102],
              [-1.35042,        1.15351,        0.78475],
              [-1.35043,        1.42183,       -1.00450],
              [-1.12302,        3.61652,        1.15412],
              [-2.60028,        3.23418,        0.18203],
              [-1.12302,        3.88485,       -0.63514]])

B = A
B = B + 1
B = np.dot(B, R)

#plot
fig = plt.figure()
ax = fig.gca(projection='3d')

Ax = A[:,0]
Ay = A[:,1]
Az = A[:,2]

Bx = B[:,0]
By = B[:,1]
Bz = B[:,2]

plot3d(A, B)
print("Normal RMSD", rmsd.rmsd(A, B))

# Manipulate
A -= rmsd.centroid(A)
B -= rmsd.centroid(B)

plot3d(A, B)
print("Translated RMSD", rmsd.rmsd(A, B))

U = rmsd.kabsch(A, B)
A = np.dot(A, U)

plot3d(A, B)
print("Rotated RMSD", rmsd.rmsd(A, B))
'''