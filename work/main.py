from kinect import *
from image import *
from state import *
from space import *
import cv2, copy, os, shutil, sys
import numpy as np
import threading, socket

def pointCloudToFileNumpy(points, frame_no):
    with open('Save_Point_Cloud/pc_offset_{}.csv'.format(str(frame_no).zfill(4)), 'w') as f:
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

def checkDetectPoint(diff, x, y):
    for i in range(3):
        for j in range(3):
            if diff[x + i - 1][y + j - 1] <= 0.005:
                return 0
    return 1

def socket_client():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 6666))
    except socket.error as msg:
        print (msg)
        sys.exit(1)

    print (s.recv(1024))

    while 1:
        filepath = input(str.encode('please input file path: '))
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
        s.close()
        break

def deal_data():
    print ('Accept new connection from {0}'.format(addr))
    #conn.settimeout(500)

    while 1:
        fileinfo_size = struct.calcsize('128sl')
        buf = conn.recv(fileinfo_size)
        if buf:
            filename, filesize = struct.unpack('128sl', buf)
            fn = filename.strip(str.encode('\00'))
            new_filename = os.path.join('./', 'new_' + str(fn, 'utf-8'))
            print ('file new name is {0}, filesize if {1}'.format(new_filename,
                                                                 filesize))
            recvd_size = 0
            fp = open(new_filename, 'wb')
            print ('start receiving...')

            while not recvd_size == filesize:
                if filesize - recvd_size > 1024:
                    data = conn.recv(1024)
                    recvd_size += len(data)
                else:
                    data = conn.recv(filesize - recvd_size)
                    recvd_size = filesize
                fp.write(data)
            fp.close()
            print ('end receive...')
        conn.close()
        break

def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 6666))
        s.listen(10)
    except socket.error as msg:
        print (msg)
        sys.exit(1)

    global recv_cargo

    while 1:
        conn, addr = s.accept()
        deal_data(conn, addr)
        recv_cargo += 1

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

    # Create State Machine
    state_machine = stateMachine.Machine()

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

        '''
        # Get and Save Transformed Point Cloud
        points = transform.depthToPointCloudWithMask(device, depth, diff > 0.005)
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
            points = transform.depthToPointCloudWithDownSample(device, depth, diff > 0.005, 4)
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

            plane_params = fit.fitPlane(surface_points)
            direction = locate.fitMoveDirection(valid_feature)
            strip_direction = fit.getReflectiveDirection(plane_params, direction)
            valid_point_clouds = np.array(valid_point_clouds)

            total_n = 0
            for i in range(valid_count):
                valid_point_clouds[i] = np.array(valid_point_clouds[i])
                total_n += valid_point_clouds[i].shape[0]
            print ('total point N: {}'.format(total_n))
            pointCloudToFileNumpy(valid_point_clouds[0], 0)
            for i in range(1, valid_count):
                offset = locate.calOffset(valid_feature[0], valid_feature[i], direction)
                valid_point_clouds[i] += offset
                pointCloudToFileNumpy(valid_point_clouds[i], i)

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



    if 'log' in sys.argv:
        logfile.close()
