from kinect import *
from image import *
import cv2, copy, os, shutil
import numpy as np

def pointCloudToFile(points, frame_no):
    with open('pc_cache/pc_{}.csv'.format(str(frame_no).zfill(4)), 'w') as f:
        for i in range(len(points)):
            f.write('{}, {}, {}\n'.format(points[i][0], points[i][1], points[i][2]))

if __name__ == '__main__':

    device = kinectInit.kinectDevice()

    background = None

    frame_no = 0

    shutil.rmtree('pc_cache')
    os.mkdir('pc_cache')

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
            color_mask = np.zeros((i_depth.shape[0], i_depth.shape[1], 3))
            # mask[diff > 0.005] = 255

            for i in range(i_depth.shape[0]):
                for j in range(i_depth.shape[1]):
                    if diff[i][j] > 0.005:
                        color_mask[i][j][0] = 255

            cv2.imshow('mask', color_mask)

            ret, binary = cv2.threshold(i_depth, 0, 255, cv2.THRESH_BINARY)

            cv2.imshow('binary', binary)
        
        diff = np.abs(background - i_depth)
        points = transform.depthToPointCloudWithMask(device, depth, diff > 0.005)

        np.save('pc_cache/pc_{}.npy'.format(str(frame_no).zfill(4)), points)
        pointCloudToFile(points, frame_no)

        cv2.imshow('ir', i_ir)
        cv2.imshow('depth', i_depth)
        cv2.imshow('depth blur', i_depth_blur)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break


        device.releaseFrame()
