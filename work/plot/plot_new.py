import numpy as np
import os
import time
import align_cloud
import old_align_cloud
import shape
import convex_hull
import old_convex_hull
from mayavi import mlab
from traits.api import HasTraits, Range, Instance, on_trait_change, Bool, Int, Button, String
# from traits.api import *
from traitsui.api import View, Item, HGroup, Handler, Action, ImageEditor, Group
from tvtk.pyface.scene_editor import SceneEditor
from pyface.image_resource import ImageResource

from mayavi.tools.mlab_scene_model import MlabSceneModel
from mayavi.core.ui.mayavi_scene import MayaviScene
from threading import Thread
from traitsui import menu



# return:  1 - file exist;   -1 - file damage, skip;   0 - file not exist
def check_file_log(idx):
    flag = True
    device = 1
    dict = './../Save_Point_Cloud/' + str(device) + '/'
    filename_log = dict + str(idx).zfill(3) + '_log.txt'
    if not os.path.exists(filename_log):
        return 0
    device = 0
    dict = './../Save_Point_Cloud/' + str(device) + '/'
    filename_log = dict + str(idx).zfill(3) + '_log.txt'
    if not os.path.exists(filename_log):
        return -1
    return 1
    
def visualize_mayavi_output(points, facets):
    triangles = []
    for k in range(len(facets)):
        if facets[k].flag:
            triangles.append((facets[k].a, facets[k].b, facets[k].c))
    return triangles

# return [plt_triangular_mesh, plt_cubic]
def my_plot(plots, scene, idx):
    data = align_cloud.alignPointCloud(idx)
    final_points, facets = convex_hull.ConstructConvexHull(data)
    x0, y0, z0 = np.transpose(final_points)
    triangles0 = visualize_mayavi_output(final_points, facets)
    lengthVec, widthVec = shape.shape_detect_v2(final_points)
    out_points, triangles1, size = shape.cubic_construct(final_points, lengthVec, widthVec)
    x1, y1, z1 = np.transpose(out_points)

    # to plot with old stuff
    # data = old_align_cloud.alignPointCloud(idx)
    # final_points, facets = old_convex_hull.ConstructConvexHull(data)
    # x0, y0, z0 = np.transpose(final_points)
    # triangles0 = visualize_mayavi_output(final_points, facets)
    scene.mlab.clf()
    plt_triangular_mesh = scene.mlab.triangular_mesh(x0, y0, z0, triangles0, scalars=z0)
    plt_cubic = scene.mlab.triangular_mesh(x1, y1, z1, triangles1, scalars=z1, representation='wireframe')
    scene.mlab.view(90, 45)
    scene.reset_zoom()
    # print(size)
    return [plt_triangular_mesh, plt_cubic], size


class TextDisplay(HasTraits):
    string = String()
    view = View(Item('string', show_label=False, springy=True, style='custom'))


class LogDisplay(HasTraits):
    history = String()
    string = String()
    view = View(Item('string', show_label=False, springy=True, style='custom'))

    def update(self, str):
        self.string = str + '--------------------\n' + self.history
        self.history = str + self.history


class ClosingHandler(Handler):
    def object_close_me_changed(self, info):
        info.ui.dispose()


class CheckCargoThread(Thread):
    def __init__(self, arg):
        super(CheckCargoThread, self).__init__()
        self.idx = arg              # idx = [curr_idx, next_idx]

    # Keep the next_idx always updated
    def run(self):
        print "Start checking"
        while not self.wants_abort:
            check_res = check_file_log(self.idx[1])
            if check_res==1:
                print "  Cargo " + str(self.idx[1]) + " checked"
                # time.sleep(0.2)
                self.idx[1] += 1
            elif check_res == -1:
                print "  Cargo " + str(self.idx[1]) + " file ERROR! Skipped"
                self.idx[1] += 1
            time.sleep(.5)
        print "End checking"


class UpdateSceneThread(Thread):
    def __init__(self, arg):
        super(UpdateSceneThread, self).__init__()
        self.idx = arg              # idx = [curr_idx, next_idx]

    def run(self):
        while not self.wants_abort:
            time.sleep(.5)
            if self.idx[1] == 0:
                continue
            if self.idx[0] != self.idx[1] - 1:
                self.idx[0] = self.idx[1] - 1
                if check_file_log(self.idx[0]) == -1:
                    self.log.update('Cargo ' + str(self.idx[0]) + ' file ERROR! Skipped\n')
                    continue
                self.log.string = 'Cargo ' + str(
                    self.idx[0]) + ' ploting ...\n----------------------------------------\n' + self.log.history
                self.plots, size = my_plot(self.plots, self.scene, self.idx[0])
                # print str(round(size[0], 4))
                # print str(round(size[1], 4))
                # print str(round(size[2], 4))
                volume = round(size[0], 4) * round(size[1], 4) * round(size[2], 4)
                self.display.string = 'Cargo ' + str(self.idx[0]) + \
                                    '\nLength: '+ str(round(size[0], 4)) + \
                                    '\nWidth:  '+ str(round(size[1], 4)) + \
                                    '\nHeight: '+ str(round(size[2], 4)) + \
                                    '\nVolume: ' + str(volume) + '\n'
                self.log.update('Cargo ' + str(self.idx[0]) + ' ploting ...  Finished!\n')
            else:
                pass
        # self.idx[0] = self.idx[1] - 1

    def updateOne(self):
        if check_file_log(self.idx[0]) == -1:
            self.log.update('Cargo ' + str(self.idx[0]) + 'file ERROR! Skipped\n')
            return
        # self.update_display('Cargo ' + str(self.idx[0]) + ' ploting ...\n')
        self.log.string = 'Cargo ' + str(self.idx[0]) + ' ploting ...\n' + self.log.history
        self.plots, size = my_plot(self.plots, self.scene, self.idx[0])
        volume = round(size[0], 4) * round(size[1], 4) * round(size[2], 4)
        self.display.string = 'Cargo ' + str(self.idx[0]) + " (" + str(self.idx[1]-1) + ")" + \
                              '\nLength: ' + str(round(size[0], 4)) + \
                              '\nWidth:  ' + str(round(size[1], 4)) + \
                              '\nHeight: ' + str(round(size[2], 4)) + \
                              '\nVolume: ' + str(volume) + '\n'
        self.log.update('Cargo ' + str(self.idx[0]) + ' ploting ...  Finished!\n')


# class UpdateDisplayThread(Thread):
#     def run(self):
#         self.display.string = self.text


class Visualization(HasTraits):
    logo = []
    # start_pause_update = Button()
    check_cargo_thread = Instance(CheckCargoThread)
    # active_update = False
    update_scene_thread = Instance(UpdateSceneThread)
    # update_display_thread = Instance(UpdateDisplayThread)
    scene = Instance(MlabSceneModel, ())
    display = Instance(TextDisplay, ())
    log = Instance(LogDisplay, ())

    plots = []
    idx = [-1, 0]                   # idx = [curr_idx, next_idx]

    def __init__(self, display=None):
        # Do not forget to call the parent's __init__
        HasTraits.__init__(self)
        if display:
            self.display = display
        self.check_cargo_thread = CheckCargoThread(self.idx)
        # self.check_cargo_thread.idx = self.idx
        # self.check_cargo_thread.scene = self.scene
        # self.check_cargo_thread.plots = self.plots
        self.check_cargo_thread.wants_abort = False
        self.check_cargo_thread.start()

        self.update_scene_thread = UpdateSceneThread(self.idx)
        self.update_scene_thread.wants_abort = False
        self.update_scene_thread.scene = self.scene
        self.update_scene_thread.plots = self.plots
        self.update_scene_thread.display = self.display
        self.update_scene_thread.log = self.log
        self.update_scene_thread.start()
        # self.active_update = True


    # def update_scene(self):
    #     if check_file_log(self.idx[0]) == -1:
    #         self.log.string = 'Cargo ' + str(self.idx[0]) + 'file ERROR! Skipped\n' + self.log.string
    #         return
    #     # self.update_display('Cargo ' + str(self.idx[0]) + ' ploting ...\n')
    #     str_tmp = self.log.string
    #     self.log.string = 'Cargo ' + str(self.idx[0]) + ' ploting ...\n' + str_tmp
    #     self.update_scene_thread.plots, size = my_plot(self.update_scene_thread.plots, self.scene, self.idx[0])
    #     volume = round(size[0], 4) * round(size[1], 4) * round(size[2], 4)
    #     self.display.string = 'Cargo ' + str(self.idx[0]) + " (" + str(self.idx[1]-1) + ")" + \
    #                           '\nLength: ' + str(round(size[0], 4)) + \
    #                           '\nWidth:  ' + str(round(size[1], 4)) + \
    #                           '\nHeight: ' + str(round(size[2], 4)) + \
    #                           '\nVolume: ' + str(volume) + '\n'
    #     self.log.string = 'Cargo ' + str(self.idx[0]) + ' ploting ...  Finished!\n' + str_tmp

    def do_start_pause_update(self):
        if self.check_cargo_thread and not self.check_cargo_thread.isAlive():
            return
        if self.update_scene_thread and self.update_scene_thread.isAlive():
            self.plots = self.update_scene_thread.plots
            self.update_scene_thread.wants_abort = True
            self.log.update('Active update is off!\n')
        else:
            self.update_scene_thread = UpdateSceneThread(self.idx)
            self.update_scene_thread.wants_abort = False
            self.update_scene_thread.scene = self.scene
            self.update_scene_thread.plots = self.plots
            self.update_scene_thread.display = self.display
            self.update_scene_thread.log = self.log
            self.update_scene_thread.start()
            self.log.update('Active update is on!\n')

    def do_stop_all_threading(self):
        if self.check_cargo_thread:
            self.check_cargo_thread.wants_abort = True
        if self.update_scene_thread:
            self.update_scene_thread.wants_abort = True
        self.log.update('All threading stopped!\n')


    def do_prev_cargo(self):
        if self.check_cargo_thread and not self.check_cargo_thread.isAlive():
            return
        if self.update_scene_thread.isAlive():
            self.log.update('Still in Active!  Please pause first!\n')
            return
        else:
            if self.idx[0] == 0:
                self.log.update('Have reached the first cargo!\n')
                return
            else:
                self.idx[0] -= 1
        # self.update_scene()
        self.log.update('Change to Cargo ' + str(self.idx[0]) + " (" + str(
            self.idx[1]-1) + "). \nClick 'Refresh' to start plot\n")
        # self.update_scene_thread.updateOne()
        return

    def do_next_cargo(self):
        if self.check_cargo_thread and not self.check_cargo_thread.isAlive():
            return
        if self.update_scene_thread.isAlive():
            self.log.update('Still in Active!  Please pause first!\n')
            return
        else:
            if self.idx[0] == self.idx[1]-1:
                self.log.update('Have reached the last cargo!\n')
                return
            else:
                self.idx[0] += 1
        # self.update_scene()
        self.log.update('Change to Cargo ' + str(self.idx[0]) + " (" + str(
            self.idx[1] - 1) + "). \nClick 'Refresh' to start plot\n")
        # self.update_scene_thread.updateOne()
        return

    def do_refresh_scene(self):
        if self.check_cargo_thread and not self.check_cargo_thread.isAlive():
            return
        if self.update_scene_thread.isAlive():
            self.log.update('Still in Active!  Please pause first!\n')
            return
        self.update_scene_thread.updateOne()
        return

    def do_prev_cargo_show(self):
        if self.check_cargo_thread and not self.check_cargo_thread.isAlive():
            return
        if self.update_scene_thread.isAlive():
            self.log.update('Still in Active!  Please pause first!\n')
            return
        else:
            if self.idx[0] == 0:
                self.log.update('Have reached the first cargo!\n')
                return
            else:
                self.idx[0] -= 1
        # self.update_scene()
        self.do_refresh_scene()
        return

    def do_next_cargo_show(self):
        if self.check_cargo_thread and not self.check_cargo_thread.isAlive():
            return
        if self.update_scene_thread.isAlive():
            self.log.update('Still in Active!  Please pause first!\n')
            return
        else:
            if self.idx[0] == 0:
                self.log.update('Have reached the first cargo!\n')
                return
            else:
                self.idx[0] += 1
        # self.update_scene()
        self.do_refresh_scene()
        return


    start_pause_update = Action(name="Start/Pause", action="do_start_pause_update")
    stop_all_threading = Action(name="Terminate", action="do_stop_all_threading")
    prev_cargo = Action(name="Prev", action="do_prev_cargo")
    next_cargo = Action(name="Next", action="do_next_cargo")
    refresh_scene = Action(name="Refresh", action="do_refresh_scene")
    prev_cargo_show = Action(name="Prev & Show", action="do_prev_cargo_show")
    next_cargo_show = Action(name="Next & Show", action="do_next_cargo_show")
    close_button = Action(name="Close", action="do_close")

    view = View(
        Group(
            HGroup(
                Item('logo',
                     editor=ImageEditor(scale=True, image=ImageResource('panasonic-logo-small', search_path=['./res'])),
                     show_label=False),
                Item('logo', editor=ImageEditor(scale=True, image=ImageResource('umsjtu-logo', search_path=['./res'])),
                     show_label=False),
                # orientation='horizontal'
            ),
            HGroup(
                Item('scene', editor=SceneEditor(scene_class=MayaviScene), height=500, width=500, show_label=False),
                Group(
                    Item('log', style='custom', height=60, show_label=False),
                    Item('display', style='custom', height=60, show_label=False),
                ),

                # orientation='horizontal'
                # Item('start_pause_update', show_label=False),
                # Item('last_cargo', show_label=False),
                # Item('next_cargo', show_label=False),
                # Item('text', show_label=False, springy=True, height=100, style='custom'),
            ),
            orientation='vertical'
        ),
        buttons=[refresh_scene, prev_cargo, next_cargo, prev_cargo_show, next_cargo_show, start_pause_update, stop_all_threading],
        )

    def __del__(self):
        # print "END"
        if self.check_cargo_thread:
            self.check_cargo_thread.wants_abort = True
        if self.update_scene_thread:
            self.update_scene_thread.wants_abort = True


# class MainWindow(HasTraits):
#     display = Instance(TextDisplay, ())
#     visualization = Instance(Visualization)
#
#     def _visualization_default(self):
#         return Visualization(display=self.display)
#
#     view = View(Item('visualization', style="custom", resizable=False, show_label=False))
#
#     def __del__(self):
#         self.visualization.__del__()


if __name__ == '__main__':
    try:
        visualization = Visualization()
        visualization.configure_traits()
    except (KeyboardInterrupt, SystemExit):
        pass
        # cleanup_stop_thread()
        # sys.exit()
    # mainWindow = MainWindow()
    # mainWindow.configure_traits()
