from kinect import *
from image import *
from state import *
import cv2, copy, os, shutil, sys
import numpy as np

def pointCloudToLogFile(points, frame_no):
    with open('log/pc_{}.csv'.format(str(frame_no).zfill(4)), 'w') as f:
        for i in range(len(points)):
            str_points = [str(j) for j in points[i]]
            f.write(','.join(str_points) + '\n')

def pointCloudToFile(points, frame_no):
    with open('pc_cache/pc_{}.csv'.format(str(frame_no).zfill(4)), 'w') as f:
        for i in range(len(points)):
            str_points = [str(j) for j in points[i]]
            f.write(','.join(str_points))

def checkDetectPoint(diff, x, y):
    for i in range(3):
        for j in range(3):
            if diff[x + i - 1][y + j - 1] <= 0.005:
                return 0
    return 1

if __name__ == '__main__':

    # Initialization
    device = kinectInit.kinectDevice()
    frame_no = 0

    # Create Folder for Point Cloud Storage
    try:
        shutil.rmtree('pc_cache')
    except:
        pass
    try:
        shutil.rmtree('log')
    except:
        pass

    os.mkdir('pc_cache')
    os.mkdir('log')

    # Record Background
    depth, color, ir = device.getNewFrame()
    i_depth, _, _ = transform.frameToImage(depth, color, ir)
    background = filter.smoothFrame(i_depth)
    device.releaseFrame()

    # Save Log
    if 'log' in sys.argv:
        logfile = open('log/log.txt', 'w')
        cv2.imwrite('log/background.jpg', background * 256)

    # Select Device Configuration
    device_tag = 'device1'
    if 'device2' in sys.argv:
        device_tag = 'device2'
    detect_region = detectConfig.detect_region[device_tag]
    detect_point = detectConfig.detect_point[device_tag]

    # Create State Machine
    state_machine = stateMachine.Machine()

    while True:

        # Read Frames
        depth, color, ir = device.getNewFrame()
        i_depth, i_color, i_ir = transform.frameToImage(depth, color, ir)
        diff = np.abs(background - i_depth)

        # Save IR Image and Depth Image
        cv2.imwrite('cache/1_ir_{}.jpg'.format(str(frame_no).zfill(4)), i_ir * 256)
        cv2.imwrite('cache/1_depth_{}.jpg'.format(str(frame_no).zfill(4)), i_depth * 256)

        # Check Detect Points
        detect_data = 2 * checkDetectPoint(diff, detect_point[0][0], detect_point[0][1]) + checkDetectPoint(diff, detect_point[1][0], detect_point[1][1])

        # Determine the State
        state_machine.sensorFeed(detect_data)

        # Show Workspace and Log
        i_ir_work = copy.copy(i_ir)
        cv2.line(i_ir_work, (detect_region[0][0], detect_region[0][1]), (detect_region[1][0], detect_region[1][1]), (255, 0, 255), 3)
        cv2.circle(i_ir_work, (detect_point[0][1], detect_point[0][0]), 3, (255, 0, 255))
        cv2.circle(i_ir_work, (detect_point[1][1], detect_point[1][0]), 3, (255, 0, 255))
        cv2.putText(i_ir_work, "state: {}".format(state_machine.cur_state), (200, 50), 5, 1, (255, 0, 255), 2)
        cv2.putText(i_ir_work, "data: {}".format(detect_data), (200, 100), 5, 1, (255, 0, 255), 2)
        cv2.imshow('workspace', i_ir_work)

        # Denoise Depth Image and IR Image
        i_ir = transform.grayToThreeChannels(i_ir)
        i_depth_blur = filter.smoothFrame(i_depth)
        i_ir_blur = filter.smoothFrame(i_ir)

        # Get and Save Transformed Point Cloud
        points = transform.depthToPointCloudWithMask(device, depth, diff > 0.005)
        np.save('pc_cache/pc_{}.npy'.format(str(frame_no).zfill(4)), points)
        pointCloudToFile(points, frame_no)

        # Find the Feature point
        feature_pos = locate.findFeaturePoint(i_ir_blur)
        i_ir_mark = locate.drawFeaturePoint(i_ir_blur, feature_pos)
        cv2.imshow('ir', i_ir_mark)

        # Log File
        if 'log' in sys.argv:
            all_points = transform.depthToPointCloudWithPos(device, depth)
            np.save('log/pc_{}.npy'.format(str(frame_no).zfill(4)), all_points)
            pointCloudToLogFile(all_points, frame_no)
            logfile.write('{} {}\n'.format(feature_pos[0], feature_pos[1]))
            cv2.imwrite('log/depth_{}.jpg'.format(str(frame_no).zfill(4)), i_depth_blur * 256)
            cv2.imwrite('log/ir_{}.jpg'.format(str(frame_no).zfill(4)), i_ir_blur * 256)
            cv2.imwrite('log/ir_mark_{}.jpg'.format(str(frame_no).zfill(4)), i_ir_mark * 256)

        frame_no += 1
        device.releaseFrame()
        key = cv2.waitKey(1)
        if key == ord('q'):
            break



    if 'log' in sys.argv:
        logfile.close()
