from kinect import *
from image import *
import cv2, copy
import numpy as np

if __name__ == '__main__':

    device = kinectInit.kinectDevice()

    background = None

    while True:

        depth, color = device.getNewFrame()

        i_depth, i_color = transform.frameToImage(depth, color)
        i_depth = filter.smoothDepthFrame(i_depth)

        if type(background) == type(None):
            # Save Background
            background = copy.copy(i_depth)
        else:
            diff = np.abs(background - i_depth)
            mask = np.zeros((i_depth.shape[0], i_depth.shape[1], 3))
            for i in range(i_depth.shape[0]):
                for j in range(i_depth.shape[1]):
                    if diff[i][j] > 0.1:
                        mask[i][j][0] = 255
            cv2.imshow('mask', mask)

        points = transform.depthToPointCloud(device, depth)

        cv2.imshow('depth', i_depth)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break


        device.releaseFrame()
