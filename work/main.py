from kinect import *
from image import *
from state import *
from space import *
import cv2, copy, os, shutil, sys
import numpy as np
import threading, socket
import struct

def saveFinalPointCloud(points, frame_no, device_tag, recv_cargo):
    if device_tag == 'device1':
        np.save('Save_Point_Cloud/0/{}_pc_offset.npy'.format(str(recv_cargo).zfill(3)), points)
    if device_tag == 'device2':
        np.save('Save_Point_Cloud/1/{}_pc_offset.npy'.format(str(recv_cargo).zfill(3)), points)

def pointCloudToFileNumpy(points, frame_no, device_tag, recv_cargo):
    if device_tag == 'device1':
        np.save('Save_Point_Cloud/0/{}_pc_offset_{}.npy'.format(str(recv_cargo).zfill(3), str(frame_no).zfill(4)), points)
        with open('Save_Point_Cloud/0/{}_pc_offset_{}.csv'.format(str(recv_cargo).zfill(3), str(frame_no).zfill(4)), 'w') as f:
            points_list = points.tolist()
            for i in range(len(points_list)):
                str_points = [str(j) for j in points_list[i]]
                f.write(','.join(str_points) + '\n')
    else:
        np.save('Save_Point_Cloud/1/{}_pc_offset_{}.npy'.format(str(recv_cargo).zfill(3), str(frame_no).zfill(4)), points)
        with open('Save_Point_Cloud/1/{}_pc_offset_{}.csv'.format(str(recv_cargo).zfill(3), str(frame_no).zfill(4)), 'w') as f:
            points_list = points.tolist()
            for i in range(len(points_list)):
                str_points = [str(j) for j in points_list[i]]
                f.write(','.join(str_points) + '\n')

def pointCloudToLogFile(points, frame_no):
    with open('Save_Log/pc_{}.csv'.format(str(frame_no).zfill(4)), 'w') as f:
        for i in range(len(points)):
            str_points = [str(j) for j in points[i]]
            f.write(','.join(str_points) + '\n')

def pointCloudToFile(points, frame_no):
    with open('Save_Point_Cloud/pc_{}.csv'.format(str(frame_no).zfill(4)), 'w') as f:
        for i in range(len(points)):
            str_points = [str(j) for j in points[i]]
            f.write(','.join(str_points) + '\n')

def checkDetectPointWithPlane(diff, sensor, plane, depth, device):
    state = 0

    for k in range(len(sensor)):
        cur_state = 1
        max_diff = 0
        for i in range(3):
            for j in range(3):
                max_diff = max(max_diff, diff[sensor[k][0] + i - 1][sensor[k][0] + j - 1])
                if diff[sensor[k][0] + i - 1][sensor[k][0] + j - 1] <= 0.005:
                    cur_state = 0
        # if cur_state == 1:

        state = state | cur_state
    return state

def checkDetectPoint(diff, sensor):
    state = 0

    for k in range(len(sensor)):
        cur_state = 1
        max_diff = 0
        for i in range(3):
            for j in range(3):
                max_diff = max(max_diff, diff[sensor[k][1] + i - 1][sensor[k][0] + j - 1])
                if diff[sensor[k][1] + i - 1][sensor[k][0] + j - 1] <= 0.005 or diff[sensor[k][1] + i - 1][sensor[k][0] + j - 1] > 0.2:
                    cur_state = 0

        state = state | cur_state
    return state

def socket_client(filepath):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.1.100', 6666))
        # s.connect(('127.0.0.1', 6666))
    except socket.error as msg:
        print (msg)
        return

    print (s.recv(1024))

    while 1:

        if os.path.isfile(filepath):
            fileinfo_size = struct.calcsize('128sl')
            print (type(os.path.basename(filepath)))
            print (type(os.stat(filepath).st_size))
            fhead = struct.pack('128sl', str.encode(os.path.basename(filepath)), os.stat(filepath).st_size)
            s.send(fhead)
            print ('client filepath: {0}'.format(filepath))

            fp = open(filepath, 'rb')
            while 1:
                data = fp.read(1024)
                if not data:
                    print ('{0} file send over...'.format(filepath))
                    break
                s.send(data)
        else:
            print 'lalala'
        s.close()
        break

if __name__ == '__main__':

    # Initialization
    device = kinectInit.kinectDevice()
    frame_no = 0
    valid_count = 0
    valid_point_clouds = []
    valid_feature = []
    surface_points = []
    recv_cargo = 0

    # Create Folder for Point Cloud Storage, Log and Image
    try:
        shutil.rmtree('Save_Point_Cloud')
    except:
        pass
    try:
        shutil.rmtree('Save_Log')
    except:
        pass
    try:
        shutil.rmtree('Save_Image')
    except:
        pass
    try:
        shutil.rmtree('Save_Temp')
    except:
        pass
    os.mkdir('Save_Point_Cloud')
    os.mkdir('Save_Point_Cloud/0')
    os.mkdir('Save_Point_Cloud/1')
    os.mkdir('Save_Log')
    os.mkdir('Save_Image')
    os.mkdir('Save_Temp')

    # Record Background
    depth, color, ir = device.getNewFrame()
    i_depth, _, _ = transform.frameToImage(depth, color, ir)
    background = filter.smoothFrame(i_depth)
    device.releaseFrame()

    # Save Log
    if 'log' in sys.argv:
        logfile = open('Save_Log/log.txt', 'w')
        cv2.imwrite('Save_Log/background.jpg', background * 255)

    # Select Device Configuration
    device_tag = 'device1'
    if 'device2' in sys.argv:
        device_tag = 'device2'
    detect_region = detectConfig.detect_region[device_tag]
    detect_point = detectConfig.detect_point[device_tag]

    bg_points = []
    for i in range(len(detect_point[0])):
        bg_points.append(transform.depthToPoint(device, depth, detect_point[0][i][0], detect_point[0][i][1]))
        bg_points.append(transform.depthToPoint(device, depth, detect_point[1][i][0], detect_point[1][i][1]))
    bg_plane = fit.fitPlane(bg_points)
    # tmp_scale = np.sqrt(bg_plane[0] ** 2 + bg_plane[1] ** 2 + 1)
    # bg_plane = bg_plane / tmp_scale

    print (bg_plane)

    # Create State Machine
    state_machine = stateMachine.Machine()

    i_diff = np.zeros((424, 512, 3))

    while True:

        # Read Frames
        depth, color, ir = device.getNewFrame()
        i_depth, i_color, i_ir = transform.frameToImage(depth, color, ir)
        diff = background - i_depth

        # Save IR Image and Depth Image
        if 'image' in sys.argv:
            cv2.imwrite('Save_Image/{}_ir_{}.jpg'.format(device_tag, str(frame_no).zfill(4)), i_ir * 255)
            cv2.imwrite('Save_Image/{}_depth_{}.jpg'.format(device_tag, str(frame_no).zfill(4)), i_depth * 255)

        # Check Detect Points
        detect_data = 2 * checkDetectPoint(diff, detect_point[0]) + checkDetectPoint(diff, detect_point[1])

        # Determine the State
        state_machine.sensorFeed(detect_data)

        # Show Workspace and Log
        i_ir_work = copy.copy(i_ir)
        cv2.line(i_ir_work, (detect_region[0][0], detect_region[0][1]), (detect_region[1][0], detect_region[1][1]), (255, 0, 255), 3)
        for i in range(len(detect_point[0])):
            cv2.circle(i_ir_work, (detect_point[0][i][1], detect_point[0][i][0]), 3, (255, 0, 255))
            cv2.circle(i_ir_work, (detect_point[1][i][1], detect_point[1][i][0]), 3, (255, 0, 255))
        cv2.putText(i_ir_work, "state: {}".format(state_machine.cur_state), (200, 50), 5, 1, (255, 0, 255), 2)
        cv2.putText(i_ir_work, "data: {}".format(detect_data), (200, 100), 5, 1, (255, 0, 255), 2)
        cv2.imshow('workspace', i_ir_work)

        # Denoise Depth Image and IR Image
        i_ir = transform.grayToThreeChannels(i_ir)
        i_depth_blur = filter.smoothFrame(i_depth)
        cv2.imshow('i_depth', i_depth)
        i_ir_blur = filter.smoothFrame(i_ir)

        '''
        # Show Mask
        i_diff *= 0
        i_diff[np.logical_and(diff > 0.005, diff < 0.2)] = [255, 0, 0]
        cv2.imshow('diff', i_diff)
        '''

        '''
        # Get and Save Transformed Point Cloud
        points = np.array(transform.depthToPointCloudWithMask(device, depth, np.logical_and(diff > 0.005, diff < 0.2)))
        print (points.shape)
        np.save('Save_Point_Cloud/pc_{}.npy'.format(str(frame_no).zfill(4)), points)
        pointCloudToFile(points, frame_no)
        '''

        # Find the Feature point
        feature_pos = locate.findFeaturePoint(i_ir_blur, device_tag)
        i_ir_mark = locate.drawFeaturePoint(i_ir_blur, feature_pos)
        feature_pos_neighbor = (feature_pos[0] + detectConfig.feature_offset[device_tag][0], feature_pos[1] + detectConfig.feature_offset[device_tag][1])
        i_ir_mark = locate.drawFeaturePoint(i_ir_mark, feature_pos_neighbor)
        cv2.imshow('ir', i_ir_mark)

        #
        # State Machine
        #
        if state_machine.cur_state == 'wait': # wait: Do Nothing
            valid_count = 0
            valid_point_clouds = []
            valid_feature = []
            surface_points = []
        elif state_machine.cur_state == 'on': # on: record image
            points = transform.depthToPointCloudWithDownSampleAndPlane(device, depth, np.logical_and(diff > 0.005, diff < 0.2), 4, bg_plane)
            valid_point_clouds.append(points)

            feature_2d = locate.findFeaturePoint(i_ir_blur, device_tag)
            feature_2d_neighbor = (feature_2d[0] + detectConfig.feature_offset[device_tag][0], feature_2d[1] + detectConfig.feature_offset[device_tag][1])
            feature_3d = transform.depthToPoint(device, depth, feature_2d[0], feature_2d[1])
            feature_3d_neighbor = transform.depthToPoint(device, depth, feature_2d_neighbor[0], feature_2d_neighbor[1])
            valid_feature.append(feature_3d)
            surface_points.append(feature_3d)
            surface_points.append(feature_3d_neighbor)
            valid_count += 1

        elif state_machine.cur_state == 'analyze': # analyze: align point cloud

            try:
                plane_params = copy.copy(bg_plane)
                direction = locate.fitMoveDirection(valid_feature)
                strip_direction = fit.getReflectiveDirection(plane_params, direction)
                # valid_point_clouds = np.array(valid_point_clouds)

                total_n = 0
                for i in range(valid_count):
                    valid_point_clouds[i] = np.array(valid_point_clouds[i])
                    total_n += valid_point_clouds[i].shape[0]
                print ('total point N: {}'.format(total_n))
                # pointCloudToFileNumpy(valid_point_clouds[0], 0, device_tag, recv_cargo)
                for i in range(1, valid_count):
                    if valid_point_clouds[i].shape[0] > 0:
                        offset = locate.calOffset(valid_feature[0], valid_feature[i], direction)
                        valid_point_clouds[i] += offset
                        # pointCloudToFileNumpy(valid_point_clouds[i], i, device_tag, recv_cargo)
                    else:
                        valid_point_clouds[i] = np.zeros((0, 3))

                saveFinalPointCloud(valid_point_clouds, 0, device_tag, recv_cargo)

                if device_tag == 'device1':
                    with open('Save_Point_Cloud/0/{}_log.txt'.format(str(recv_cargo).zfill(3)), 'w') as f:
                        f.write(str(recv_cargo) + '\n')
                        f.write(str(valid_count) + '\n')
                        # f.write('3\n')
                        f.write('{}, {}, {}\n'.format(bg_plane[0], bg_plane[1], bg_plane[2]))
                        f.write('{}, {}, {}\n'.format(direction[0], direction[1], direction[2]))
                        f.write('{}, {}, {}\n'.format(strip_direction[0], strip_direction[1], strip_direction[2]))
                        f.write('{}, {}, {}\n'.format(valid_feature[0][0], valid_feature[0][1], valid_feature[0][2]))

                    try:
                        socket_client('Save_Point_Cloud/0/{}_pc_offset.npy'.format(str(recv_cargo).zfill(3), str(i).zfill(4)))
                    except:
                        pass
                    try:
                        socket_client('Save_Point_Cloud/0/{}_log.txt'.format(str(recv_cargo).zfill(3)))
                    except:
                        pass

                else:
                    with open('Save_Point_Cloud/1/{}_log.txt'.format(str(recv_cargo).zfill(3)), 'w') as f:
                        f.write(str(recv_cargo) + '\n')
                        f.write(str(valid_count) + '\n')
                        f.write('{}, {}, {}\n'.format(plane_params[0], plane_params[1], plane_params[2]))
                        f.write('{}, {}, {}\n'.format(direction[0], direction[1], direction[2]))
                        f.write('{}, {}, {}\n'.format(strip_direction[0], strip_direction[1], strip_direction[2]))
                        f.write('{}, {}, {}\n'.format(valid_feature[0][0], valid_feature[0][1], valid_feature[0][2]))
                recv_cargo += 1
            except:
                print 'Error Occurs in Analyze! (N_Cargo = {})'.format(cargo_no)
                print 'Reseting...'
                cargo_no = 0
                state_machine.cur_state = 'wait'
            # Test Plane Formula
            '''
            test_point = []
            for i in range(100):
                for j in range(100):
                    test_point.append([(i - 50) / 25., (j - 50) / 25., plane_params[0] * (i - 50) / 25. + plane_params[1] * (j - 50) / 25. + plane_params[2]])
            test_point = np.array(test_point)
            pointCloudToFileNumpy(test_point, valid_count)
            '''

        elif state_machine.cur_state == 'out':
            valid_count = 0
            valid_feature = []
            valid_point_clouds = []
            surface_points = []

        elif state_machine.cur_state == 'err': # err: clear data
            pass


        # Log File
        if 'log' in sys.argv:
            all_points = transform.depthToPointCloudWithPos(device, depth)
            np.save('Save_Log/pc_{}.npy'.format(str(frame_no).zfill(4)), all_points)
            pointCloudToLogFile(all_points, frame_no)
            logfile.write('{} {}\n'.format(feature_pos[0], feature_pos[1]))
            cv2.imwrite('Save_Log/depth_{}.jpg'.format(str(frame_no).zfill(4)), i_depth_blur * 255)
            cv2.imwrite('Save_Log/ir_{}.jpg'.format(str(frame_no).zfill(4)), i_ir_blur * 255)
            cv2.imwrite('Save_Log/ir_mark_{}.jpg'.format(str(frame_no).zfill(4)), i_ir_mark * 255)

        frame_no += 1
        device.releaseFrame()
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        if key == ord('r'):
            print ('Reseting...')
            cargo_no = 0
            state_machine.cur_state = 'wait'



    if 'log' in sys.argv:
        logfile.close()
