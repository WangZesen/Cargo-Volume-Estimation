# import numpy as np
# from mayavi import mlab

'''
n = 10000
x, y, z = np.random.random((3, n))
s = np.sin(x)**2 + np.cos(y)
mlab.points3d(x, y, z, s, colormap="RdYlBu", scale_factor=0.02, scale_mode='none')
# mlab.points3d(x, y, z, s)
mlab.show()
print("finish")
'''

'''
x, y = np.ogrid[-2:2:20j, -2:2:20j]
z = x * np.exp( - x**2 - y**2)
pl = mlab.surf(x, y, z, warp_scale="auto")
mlab.axes(xlabel='x', ylabel='y', zlabel='z')
mlab.outline(pl)
mlab.show()
'''

'''
x, y, z, value = np.random.random((4, 50))
mylab.points3d(x, y, z, value)
mylab.show()
'''

'''
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = Axes3D(fig)
X = np.arange(-4, 4, 0.25)
Y = np.arange(-4, 4, 0.25)
X, Y = np.meshgrid(X, Y)
R = np.sqrt(X**2 + Y**2)
Z = np.sin(R)
ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='rainbow')
plt.show()
'''

'''
x, y = np.mgrid[0:3:1,0:3:1]
s = mlab.surf(x, y, np.asarray(x*0.1, 'd'))

@mlab.animate(delay=100)
def anim():
	for i in range(10):
		s.mlab_source.scalars = np.asarray(x*0.1*(i+1), 'd')
		yield

anim()
mlab.show()
'''

'''
x, y = np.mgrid[0:3:1,0:3:1]
s = mlab.surf(x, y, np.asarray(x*0.1, 'd'), representation='wireframe')

# Animate the data.
fig = mlab.gcf()
ms = s.mlab_source
@mlab.animate(delay=100)
def anim():
	for i in range(5):
		x, y = np.mgrid[0:3:1.0/(i+2),0:3:1.0/(i+2)]
		print(x.shape)
		sc = np.asarray(x*x*0.05*(i+1), 'd')
		ms.reset(x=x, y=y, scalars=sc)
		fig.scene.reset_zoom()
		yield

anim()
mlab.show(stop=True)
'''
'''
n_mer, n_long = 6, 11
pi = np.pi
dphi = pi/1000.0
phi = np.arange(0.0, 2*pi + 0.5*dphi, dphi, 'd')
mu = phi*n_mer
x = np.cos(mu)*(1+np.cos(n_long*mu/n_mer)*0.5)
y = np.sin(mu)*(1+np.cos(n_long*mu/n_mer)*0.5)
z = np.sin(n_long*mu/n_mer)*0.5

# View it.
l = mlab.plot3d(x, y, z, np.sin(mu), tube_radius=0.025, colormap='Spectral')

# Now animate the data.
ms = l.mlab_source

@mlab.animate(delay=100)
def anim():
	for i in range(10):
		x = np.cos(mu)*(1+np.cos(n_long*mu/n_mer + np.pi*(i+1)/5.)*0.5)
		#scalars = np.sin(mu + np.pi*(i+1)/5)
		print x.shape
		l.mlab_source.trait_set(x=x)
		yield
	
anim()
mlab.show(stop=True)
'''

'''
n = 8
t = np.linspace(-np.pi, np.pi, n)
z = np.exp(1j * t)
x = z.real.copy()
y = z.imag.copy()
z = np.zeros_like(x)

triangles = [(0, i, i + 1) for i in range(1, n)]
x = np.r_[0, x]
y = np.r_[0, y]
z = np.r_[1, z]
t = np.r_[0, t]

# print x
# print y
# print z
# print triangles

mlab.triangular_mesh(x, y, z, triangles, scalars=t, representation='wireframe')
mlab.show()
'''


# from traits.api import HasTraits, Range, Instance, on_trait_change, Bool, String, Button, Int
# from traitsui.api import View, Item, HGroup, Handler, Action
# from tvtk.pyface.scene_editor import SceneEditor
# from mayavi.tools.mlab_scene_model import MlabSceneModel
# from mayavi.core.ui.mayavi_scene import MayaviScene
# from numpy import linspace, pi, cos, sin
# import time
# from threading import Thread
#
# from traitsui import menu
#
# def curve(n_mer, n_long):
#     phi = linspace(0, 2*pi, 2000)
#     return [ cos(phi*n_mer) * (1 + 0.5*cos(n_long*phi)),
#             sin(phi*n_mer) * (1 + 0.5*cos(n_long*phi)),
#             0.5*sin(n_long*phi),
#             sin(phi*n_mer)]
#
#
# # meridional = Range(1, 30,  6)
# # transverse = Range(0, 30, 11)
#
# tmp0 = Int(0)
#
# # class TC_Handler(Handler):
# #
# #     def setattr(self, info, object, name, value):
# #         Handler.setattr(self, info, object, name, value)
# #         # value.object._updated = True
# #         info.object._updated = True
# #
# #     def object_meridional_changed(self, info):
# #         if info.initialized:
# #             info.ui.title += '*'
#
# class Visualization(HasTraits):
#     # global meridional, transverse
#     global tmp0
#     tmp = Int(0)
#     meridional = Range(1, 30,  6)
#     transverse = Range(0, 30, 11)
#     scene      = Instance(MlabSceneModel, ())
#
#     # start_stop_capture = Button()
#     # display = Instance(AddMeridional)
#     # capture_thread = Instance(myThread)
#
#     def __init__(self):
#         # Do not forget to call the parent's __init__
#         HasTraits.__init__(self)
#         # global meridional, transverse
#         x, y, z, t = curve(self.meridional, self.transverse)
#         # x, y, z, t = curve(meridional, transverse)
#         self.plot = self.scene.mlab.plot3d(x, y, z, t, colormap='Spectral')
#         # self.
#
#     @on_trait_change('meridional, transverse')
#     def update_plot(self):
#         # global meridional, transverse
#         x, y, z, t = curve(self.meridional, self.transverse)
#         print x.shape
#         # x, y, z, t = curve(meridional, transverse)
#         self.plot.remove()
#         # self.plot.mlab_source.trait_set(x=x, y=y, z=z, scalars=t)
#         self.plot = self.scene.mlab.plot3d(x, y, z, t, colormap='Spectral')
#         self.scene.mlab.view(90, 45)
#         self.scene.reset_zoom()
#         # global tmp0
#         # print tmp0
#
#     @on_trait_change('tmp')
#     def printTmp(self):
#         # print self.tmp
#         global tmp0
#         tmp0 = self.tmp
#         # print tmp0
#
#     def do_recalc(self):
#         # global meridional
#         if self.meridional < 30:
#             self.meridional += 1
#         else:
#             self.meridional = 1
#         print self.meridional
#
#     def do_addTmp(self):
#         # global tmp0
#         self.tmp += 1
#         # self.view.title='aaa'
#
#     recalc = Action(name="Recalculate", action="do_recalc")
#     addTmp = Action(name="AddTmp", action="do_addTmp")
#
#     # the layout of the dialog created
#     view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene), height=250, width=300, show_label=False),
#                 HGroup( '_', 'meridional', 'transverse',),
#                 buttons = [menu.OKButton, recalc, addTmp],
#                 # handler=TC_Handler(),
#                 title='AAAA'
#                 )
#
# # class MainWindow(HasTraits):
# #     display = Instance(AddMeridional, ())
# #
# #     vis = Instance(Visualization)
# #
# #     def _camera_default(self):
# #         return Visualization(display=self.display)
# #
# #     view = View('display', 'vis', style="custom", resizable=True)
#
#
#
# visualization = Visualization()
# visualization.configure_traits()








from threading import Thread
from time import sleep
from traits.api import *
from traitsui.api import View, Item, ButtonEditor
from traitsui import menu

# n_img = 0

'''

class TextDisplay(HasTraits):
    string =  String()
    view= View( Item('string',show_label=False, springy=True, style='custom' ))


class CaptureThread(Thread):
    def __init__(self):
        super(CaptureThread, self).__init__()
        # print arg
        # self.n_img = arg[0]
        # print self.n_img

    def run(self):
        self.display.string = 'Camera started\n' + self.display.string
        # n_img = 0
        # global n_img
        while not self.wants_abort:
            sleep(.5)
            # print
            self.n_img[0] += 1
            self.display.string = '%d image captured\n' % self.n_img[0] + self.display.string
        self.display.string = 'Camera stopped\n' + self.display.string


class Camera(HasTraits):
    start_stop_capture = Button()
    display = Instance(TextDisplay)
    tmp = Int(0)
    local_asd = [tmp]
    capture_thread = Instance(CaptureThread)

    view = View( Item('start_stop_capture', show_label=False ))

    def _start_stop_capture_fired(self):
        # print self.local_asd
        if self.capture_thread and self.capture_thread.isAlive():
            self.capture_thread.wants_abort = True
        else:
            self.capture_thread = CaptureThread()
            self.capture_thread.n_img = self.local_asd
            self.capture_thread.wants_abort = False
            self.capture_thread.display = self.display
            self.capture_thread.start()

    @on_trait_change('tmp')
    def flag(self):
        print "AAAAAAAAAA"

    def __del__(self):
        print "END"
        if self.capture_thread:
            self.capture_thread.wants_abort = True


class MainWindow(HasTraits):
    display = Instance(TextDisplay, ())

    camera = Instance(Camera)

    def _camera_default(self):
        return Camera(display=self.display)

    view = View('display', 'camera', style="custom", resizable=True)


if __name__ == '__main__':
    MainWindow().configure_traits()
'''


'''
class TC_Handler(Handler):

    def setattr(self, info, object, name, value):
        Handler.setattr(self, info, object, name, value)
        info.object._updated = True

    def object__updated_changed(self, info):
        if info.initialized:
            info.ui.title += "*"

    def do_recalc(self):
        print "aa"
        pass

recalc = Action(name="Recalculate",
                    action="do_recalc")

class TestClass(HasTraits):
    b1 = Bool
    b2 = Bool
    b3 = Bool
    _updated = Bool(False)

view1 = View('b1', 'b2', 'b3',
             title="Alter Title",
             handler=TC_Handler(),
             buttons = ['OK', 'Cancel', recalc])

tc = TestClass()
tc.configure_traits(view=view1)
'''

#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of an ImageEnumEditor demo plugin for the Traits UI demo program.
This demo shows each of the four styles of the ImageEnumEditor.
"""

'''
# Imports:
from traits.api \
    import HasTraits, Str, Trait

from traitsui.api \
    import Item, Group, View, ImageEnumEditor

# This list of image names (with the standard suffix "_origin") is used to
# construct an image enumeration trait to demonstrate the ImageEnumEditor:
image_list = ['top left', 'top right', 'bottom left', 'bottom right']


class Dummy(HasTraits):
    """ Dummy class for ImageEnumEditor
    """
    x = Str

    view = View()


class ImageEnumEditorDemo(HasTraits):
    """ Defines the ImageEnumEditor demo class.
    """

    # Define a trait to view:
    image_from_list = Trait(editor=ImageEnumEditor(values=image_list,
                                                   prefix='@icons:',
                                                   suffix='_origin',
                                                   cols=4,
                                                   klass=Dummy),
                            *image_list)

    # Items are used to define the demo display, one Item per editor style:
    img_group = Group(
        Item('image_from_list', style='simple', label='Simple'),
        Item('_'),
        Item('image_from_list', style='custom', label='Custom'),
        Item('_'),
        Item('image_from_list', style='text', label='Text'),
        Item('_'),
        Item('image_from_list', style='readonly', label='ReadOnly')
    )

    # Demo view:
    view = View(
        img_group,
        title='ImageEnumEditor',
        buttons=['OK'],
        resizable=True
    )

# Create the demo:
demo = ImageEnumEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
'''

#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
A simple demonstration of how to use the ImageEditor to add a graphic element
to a Traits UI View.
"""

import traits

# Imports:
from os.path \
    import join, dirname

'''
from traits.api \
    import HasTraits, Str

from traitsui.api \
    import View, VGroup, Item

from traitsui.api \
    import ImageEditor

from pyface.image_resource \
    import ImageResource

# Constants:

# Necessary because of the dynamic way in which the demos are loaded:
# search_path = [join(dirname(traits.api.__file__),
#                     '..', '..', 'examples', 'demo', 'Extras')]
search_path = ['./res']

print search_path
# Define the demo class:


class Employee(HasTraits):

    # Define the traits:
    name = Str
    dept = Str
    email = Str

    # Define the view:
    view = View(
        VGroup(
            VGroup(
                Item('name',
                     show_label=False,
                     editor=ImageEditor(
                         image=ImageResource('info',
                                             search_path=search_path)))
            ),
            VGroup(
                Item('name'),
                Item('dept'),
                Item('email'),
                Item('picture',
                     editor=ImageEditor(
                         scale=True,
                         # preserve_aspect_ratio=True,
                         # allow_upscaling=True
                     ),
                     springy=True),
            )
        ),
        resizable=True
    )

# Create the demo:
popup = Employee(name='William Murchison',
                 dept='Receiving',
                 email='wmurchison@acme.com',
                 picture=ImageResource('e-logo-rev',
                                       search_path=search_path))

# Run the demo (if invoked form the command line):
if __name__ == '__main__':
    popup.configure_traits()
'''

