from pylibfreenect2 import Freenect2, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame
from pylibfreenect2 import createConsoleLogger, setGlobalLogger
from pylibfreenect2 import LoggerLevel
import cameraParams
import sys, copy
import cv2

class kinectDevice:
    def __init__(self):
        # Package Pipeline
        try:
            from pylibfreenect2 import OpenGLPacketPipeline
            self.pipeline = OpenGLPacketPipeline()
        except:
            try:
                from pylibfreenect2 import OpenCLPacketPipeline
                self.pipeline = OpenCLPacketPipeline()
            except:
                from pylibfreenect2 import CpuPacketPipeline
                self.pipeline = CpuPacketPipeline()
        print "Packet pipeline: {}".format(type(self.pipeline).__name__)

        # Create and set logger
        logger = createConsoleLogger(LoggerLevel.Error)
        setGlobalLogger(logger)

        # Detect Kinect Devices
        self.fn = Freenect2()
        num_devices = self.fn.enumerateDevices()
        if num_devices == 0:
            print("No device connected!")
            self.device = None
            sys.exit(1)

        # Create Device and Frame Listeners
        self.serial = self.fn.getDeviceSerialNumber(0)
        self.device = self.fn.openDevice(self.serial, pipeline = self.pipeline)
        self.listener = SyncMultiFrameListener(FrameType.Color | FrameType.Ir | FrameType.Depth)

        # Register Listeners
        self.device.setColorFrameListener(self.listener)
        self.device.setIrAndDepthFrameListener(self.listener)

        # Start Device
        self.device.start()

        # Set Camera Parameters
        self._ir_params = self.device.getIrCameraParams()
        self._color_params = self.device.getColorCameraParams()

        self._ir_params.fx = cameraParams.params['ir_fx']
        self._ir_params.fy = cameraParams.params['ir_fy']
        self._ir_params.cx = cameraParams.params['ir_cx']
        self._ir_params.cy = cameraParams.params['ir_cy']

        self._color_params.fx = cameraParams.params['col_fx']
        self._color_params.fy = cameraParams.params['col_fy']
        self._color_params.cx = cameraParams.params['col_cx']
        self._color_params.cy = cameraParams.params['col_cy']

        # Registration
        self.registration = Registration(self._ir_params, self._color_params)

        print '[Info] Initialization Finished!'

    # Get New Frame (in "Frame" type)
    def getNewFrame(self):
        # Get Raw Data from Listener
        self.frames = self.listener.waitForNewFrame()

        # Get Depth Frame and Color Frame
        depth = self.frames['depth']
        color = self.frames['color']

        return depth, color

    # Release Frame
    def releaseFrame(self):
        self.listener.release(self.frames)


    def __del__(self):
        # Stop and Close Device
        if self.device != None:
            self.device.stop()
            self.device.close()

    #
    # Get Parameters of KinectDevice
    #

    # Infrared Camera
    @property
    def ir_params(self):
        return self._ir_params

    # Color Camera
    @property
    def color_params(self):
        return self._color_params

if __name__ == '__main__':

    # For Testing
    test_device = kinectDevice()

    while True:
        depth, color = test_device.getNewFrame()
        cv2.imshow('depth', depth)
        cv2.imshow('color', color)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
