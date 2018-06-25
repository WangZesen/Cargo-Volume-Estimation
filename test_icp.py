import numpy as np
import time
import icp
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics.pairwise import paired_distances
import rmsd

# Constants
N = 5000                                    # number of random points in the dataset
num_tests = 10                             # number of test iterations
dim = 3                                     # number of dimensions of the points
noise_sigma = .01                           # standard deviation error to be added
translation = 1                            # max translation of the test set
rotation = np.pi / 3                         # max rotation (radians) of the test set

def squared_distance(A, B):
    return np.sum(paired_distances(A, B) ** 2)

def rotation_matrix(axis, theta):
    axis = axis/np.sqrt(np.dot(axis, axis))
    a = np.cos(theta/2.)
    b, c, d = -axis*np.sin(theta/2.)

    return np.array([[a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)],
                  [2*(b*c+a*d), a*a+c*c-b*b-d*d, 2*(c*d-a*b)],
                  [2*(b*d-a*c), 2*(c*d+a*b), a*a+d*d-b*b-c*c]])

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
    plt.ion()

    plt.pause(1)  #显示秒数
    plt.close()
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

def test_best_fit(A):

    # Generate a random dataset

    for i in range(num_tests):
        print('test', i)
        B = np.copy(A)

        # Translate
        t = np.random.rand(dim)*translation
        B += t

        # Rotate
        R = rotation_matrix(np.random.rand(dim), np.random.rand()*rotation)
        B = np.dot(R, B.T).T

        # Add noise
        B += np.random.randn(N, dim) * noise_sigma
        
        # Shuffle to disrupt correspondence
        np.random.shuffle(B)

        plot3d(A, B)
        print("Normal squared_distance", squared_distance(A, B))

        # Find best fit transform
        A -= rmsd.centroid(A)
        B -= rmsd.centroid(B)
        T, R1, t1 = icp.best_fit_transform(B, A)

        # Make C a homogeneous representation of B
        C = np.ones((N, 4))
        C[:,0:3] = B

        # Transform C
        C = np.dot(T, C.T).T

        C = C[:, 0:3]
        plot3d(A, C)
        
        print("Rotated squared_distance", squared_distance(A, C))

        #assert np.allclose(C[:,0:3], A, atol=6*noise_sigma) # T should transform B (or C) to A
        #assert np.allclose(-t1, t, atol=6*noise_sigma)      # t and t1 should be inverses
        #assert np.allclose(R1.T, R, atol=6*noise_sigma)     # R and R1 should be inverses

    return


def test_icp(A):

    # Generate a random dataset
    
    for i in range(num_tests):
        print('test', i)
        B = np.copy(A)

        # Translate
        t = np.random.rand(dim)*translation
        B += t

        # Rotate
        R = rotation_matrix(np.random.rand(dim), np.random.rand() * rotation)
        B = np.dot(R, B.T).T

        # Add noise
        B += np.random.randn(N, dim) * noise_sigma

        # Shuffle to disrupt correspondence
        np.random.shuffle(B)

        plot3d(A, B)
        print("Normal squared_distance", squared_distance(A, B))

        # Run ICP
        A -= rmsd.centroid(A)
        B -= rmsd.centroid(B)
        T, distances, iterations = icp.icp(B, A, tolerance=0.000001)

        # Make C a homogeneous representation of B
        C = np.ones((N, 4))
        C[:,0:3] = np.copy(B)

        # Transform C
        C = np.dot(T, C.T).T
        C = C[:, 0:3]

        plot3d(A, C)
        print("Rotated squared_distance", squared_distance(A, C))

        #assert np.mean(distances) < 6*noise_sigma                   # mean error should be small
        #assert np.allclose(T[0:3,0:3].T, R, atol=6*noise_sigma)     # T and R should be inverses
        #assert np.allclose(-T[0:3,3], t, atol=6*noise_sigma)        # T and t should be inverses
    
    return 


if __name__ == "__main__":
    A = np.random.rand(N, dim)
    print('===test best fit===')
    test_best_fit(A)
    print('===test icp===')
    test_icp(A)