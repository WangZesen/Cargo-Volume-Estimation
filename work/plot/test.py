import numpy as np
import threading
from mayavi import mlab
import time

class myPlot:
    def __init__(self):
        self.threads = []
        self.run = False
        self.firstRound = True
        self.dataUpdate = False
        self.data = None
        self.plt = None


    def PPlot(self):
        while not self.dataUpdate:
            time.sleep(0.01)
        x, y, z = np.transpose(self.data)
        self.plt = mlab.points3d(x, y, z, -y, colormap="RdYlBu", scale_factor=0.01, scale_mode='none')
        self.dataUpdate = False

        @mlab.animate(delay=10)
        def anim():
            while self.run:
                while not self.dataUpdate:
                    time.sleep(0.01)
                x, y, z = np.transpose(self.data)
                self.plt.mlab_source.reset(x=x, y=y, z=z, scalars=-y)
                self.dataUpdate = False
                yield

        self.anim()
        mlab.show()


    def startPlot(self):
        self.run = True
        print "start"
        t = threading.Thread(target=self.PPlot, args=())
        self.threads.append(t)
        t.setDaemon(True)
        t.start()


    def endPlot(self):
        print "end"
        self.run = False


    def setData(self, data):
        while self.dataUpdate:      # last time update hasn't been shown in animation
            time.sleep(0.01)
        self.data = data
        self.dataUpdate = True


if __name__ == '__main__':
    a = myPlot()
    a.startPlot()

    dict = "./pc_data/"
    for i in range(50):
        path = dict + "pc_00" + str(i) + ".npy"
        data = np.load(path)
        a.setData(data)

    a.endPlot()
