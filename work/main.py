from kinect import *
from image import *
import cv2, copy
import numpy as np

if __name__ == '__main__':

    device = kinectInit.kinectDevice()

    background = None

    frame_no = 0

    while True:

        depth, color, ir = device.getNewFrame()

        i_depth, i_color, i_ir = transform.frameToImage(depth, color, ir)

        cv2.imwrite('cache/1_ir_{}.jpg'.format(str(frame_no).zfill(4)), i_ir * 256)
        cv2.imwrite('cache/1_depth_{}.jpg'.format(str(frame_no).zfill(4)), i_depth * 256)
        frame_no += 1


        i_depth_blur = filter.smoothDepthFrame(i_depth)

        # print (np.max(i_ir))

        if type(background) == type(None):
            # Save Background
            background = copy.copy(i_depth)
        else:

            diff = np.abs(background - i_depth)
            mask = np.zeros((i_depth.shape[0], i_depth.shape[1], 3))
            # mask[diff > 0.005] = 255

            for i in range(i_depth.shape[0]):
                for j in range(i_depth.shape[1]):
                    if diff[i][j] > 0.005:
                        mask[i][j][0] = 255

            cv2.imshow('mask', mask)


            ret, binary = cv2.threshold(i_depth, 0, 255, cv2.THRESH_BINARY)

            #_,contours, hierarchy = cv2.findContours(ret, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            #cv2.drawContours(img, contours, -1, (0,0,255), 3)
            #cv2.imshow("result", img)

            cv2.imshow('binary', binary)

        points = transform.depthToPointCloud(device, depth)

        cv2.imshow('ir', i_ir)
        cv2.imshow('depth', i_depth)
        cv2.imshow('depth blur', i_depth_blur)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break


        device.releaseFrame()
