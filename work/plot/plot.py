import numpy as np
import os
import time
import align_cloud
import shape
import convex_hull
from mayavi import mlab


x0 = np.array([0])
y0 = np.array([0])
z0 = np.array([0])


def read_file(device, idx):
    print "Reading ...   ",
    dict = './../Save_Point_Cloud/'+str(device)+'/'
    filename_log = dict+str(idx).zfill(3)+'_log.txt'
    waiting = False
    while not os.path.exists(filename_log):
        if idx == 0:
            if not waiting:
                print "waiting for new data"
                waiting = True
        else:
            idx -= 1
            filename_log = dict+str(idx).zfill(3)+'_log.txt'
        time.sleep(0.001)
    time.sleep(1)
    #try:
    fp = open(filename_log, 'r')
    cargo_idx = int(fp.readline())
    image_num = int(fp.readline())
    fp.close()
    '''
    data = []
    for i in range(image_num):
        filename = dict+str(idx).zfill(3)+'_pc_offset_'+str(i).zfill(4)+'.npy'
        metaData = np.load(filename)
        print metaData.shape
        data.append(metaData)
    '''
    filename = dict+str(idx).zfill(3)+'_pc_offset.npy'
    data = np.load(filename)
    print "read in (device-cargo) " + str(device) + " - " + str(idx)
    #except:
        #print "failure" + filename_log
    return data, image_num, idx


def check_file_log(idx):            # return:  1 - file exist;   -1 - file damage, skip;   0 - file not exist
    flag = True
    for device in range(2):
        dict = './../Save_Point_Cloud/' + str(device) + '/'
        filename_log = dict + str(idx).zfill(3) + '_log.txt'
        if not os.path.exists(filename_log):
            if flag:
                flag = False
            else:
                return 0
    if flag:
        return 1
    else:
        return -1


def reset_Range(plt):
    x = np.array([-0.5, 0.5])
    y = np.array([-0.5, 0.5])
    z = np.array([0, 1])
    scalars = -y
    plt.mlab_source.reset(x=x, y=y, z=z, scalars=scalars)


if __name__ == '__main__':
    x = np.array([-0.5, 0.5])
    y = np.array([-0.5, 0.5])
    z = np.array([0, 1])
    scalars = -y
    f = mlab.figure(size=(600,600))
    plt_pointCloud = mlab.points3d(x, y, z, scalars, colormap="RdYlBu", scale_factor=0.005, scale_mode='none', figure=f)
    fig = mlab.gcf()
    
    @mlab.animate(delay=100)
    def anim_full(idx=0):
        time.sleep(2)
        yield
        count_cargo = 0
        while True:
            #cam.zoom(1)
            mlab.view(180, 180)
            
            for device in range(2):
                reset_Range(plt_pointCloud)
                #yield
                fig.scene.reset_zoom()
                rawData, image_num, idx = read_file(1-device, idx)
                #mlab.title('device '+str(device) + '   cargo '+str(idx))
                text = mlab.text(0.1, 0.1, 'device '+str(device) + '   cargo '+str(idx))
                x, y, z = np.array([[],[],[]])
                for j, data in enumerate(rawData):
                    if not data.shape[0] == 0:
                        x_new, y_new, z_new = np.transpose(data)
                        x = np.hstack([x, x_new])
                        y = np.hstack([y, y_new])
                        z = np.hstack([z, z_new])
                        scalars = -y
                        plt_pointCloud.mlab_source.reset(x=x, y=y, z=z, scalars=scalars)
                        yield
                    ##mlab.savefig('./figure/f_'+str(idx).zfill(3)+'_'+str(device)+'_'+str(j).zfill(4)+'.png')
                #print "pending ..."
                time.sleep(0.5)
                yield
                text.remove()
                
            data = align_cloud.alignPointCloud(idx)
            text = mlab.text(0.1, 0.1, 'aligned device   cargo ' + str(idx))
            # x, y, z = np.transpose(data)
            # scalars = -y
            # plt_pointCloud.mlab_source.reset(x=x, y=y, z=z, scalars=scalars)
            # yield

            plt_pointCloud.mlab_source.reset(x=x0, y=y0, z=z0, scalars=-y0)

            final_points, facets = convex_hull.ConstructConvexHull(data)
            x, y, z = np.transpose(final_points)
            triangles = convex_hull.visualize_mayavi_output(final_points, facets)
            plt_triangular_mesh = mlab.triangular_mesh(x, y, z, triangles, scalars=z)
            # plt_pointCloud.mlab_source.reset(x=x, y=y, z=z, scalars=-y)

            # yield
            # fig.scene.reset_zoom()

            #title = mlab.title('aligned device   cargo '+str(idx))
            #mlab.savefig('./figure/f_'+str(idx).zfill(3)+'_aligned_device.png')
            #yield
            
            lengthVec, widthVec = shape.shape_detect_v2(final_points)
            out_points, triangles, _ = shape.cubic_construct(final_points, lengthVec, widthVec)

            # lengthVec, widthVec = shape.shape_detect_v2(data)
            # out_points, triangles, _ = shape.cubic_construct(data, lengthVec, widthVec)

            x, y, z = np.transpose(out_points)
            plt_cubic = mlab.triangular_mesh(x, y, z, triangles, scalars=z, representation='wireframe')
            mlab.view(90, 45)
            fig.scene.reset_zoom()

            yield
            print "pending ..."
            time.sleep(1)
            yield
            text.remove()

            # plt_lengthVec.remove()
            # plt_widthVec.remove()
            plt_triangular_mesh.remove()
            plt_cubic.remove()

            #title.remove()
            #time.sleep(2)
            #mlab.clf(shapePlt)
            
            idx += 1
            count_cargo += 1
            print "pass " + str(count_cargo)


    @mlab.animate(delay=100)
    def anim_output(idx=0):
        plt_pointCloud.mlab_source.reset(x=x0, y=y0, z=z0, scalars=-y0)
        count_cargo = 0
        waiting = False
        text = None
        while True:
            # cam.zoom(1)

            flag = check_file_log(idx)
            if flag == 0:
                if not waiting:
                    waiting = True
                    print "Waiting for new data"
                yield
                continue
            elif flag == -1:
                print "File readIn ERROR: skip cargo "+str(idx)
                idx += 1
                yield
                continue

            waiting = False

            if text:
                text.remove()
                for tt in text_size:
                    tt.remove()

                plt_triangular_mesh.remove()
                plt_cubic.remove()

            data = align_cloud.alignPointCloud(idx)
            text = mlab.text(0.1, 0.05, 'cargo ' + str(idx), width=0.3)

            final_points, facets = convex_hull.ConstructConvexHull(data)
            x, y, z = np.transpose(final_points)
            triangles = convex_hull.visualize_mayavi_output(final_points, facets)
            plt_triangular_mesh = mlab.triangular_mesh(x, y, z, triangles, scalars=z)

            lengthVec, widthVec = shape.shape_detect_v2(final_points)
            out_points, triangles, size = shape.cubic_construct(final_points, lengthVec, widthVec)

            x, y, z = np.transpose(out_points)
            plt_cubic = mlab.triangular_mesh(x, y, z, triangles, scalars=z, representation='wireframe')
            mlab.view(90, 45)
            fig.scene.reset_zoom()
            text_size = []
            text_size.append(mlab.text(0.05, 0.90, 'length ' + str(round(size[0], 4)), width=0.2))
            text_size.append(mlab.text(0.05, 0.85, 'width ' + str(round(size[1], 4)), width=0.2))
            text_size.append(mlab.text(0.05, 0.80, 'height ' + str(round(size[2], 4)), width=0.2))

            print "length " + str(size[0])
            print "width " + str(size[1])
            print "height " + str(size[2])

            yield
            print "pending ..."
            for i in range(10):  # 1 sec
                yield
            yield

            idx += 1
            count_cargo += 1
            print "pass " + str(count_cargo)

    print "Start ploting ..."
    # anim_full()
    anim_output()
    # mlab.view(180, 180)
    #mlab.axes()
    mlab.show(stop=True)
    #mlab.show()
