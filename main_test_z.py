# Simple demo of of the ADXL345 accelerometer library.  Will print the X, Y, Z
# axis acceleration values every half second.
# Author: Tony DiCola
# License: Public Domain
import time
import smbus

# Import the ADXL345 module.
import Adafruit_ADXL345
# Major library imports
import numpy as np
from numpy import linspace, sin
from traits.api import HasTraits, Instance
from traitsui.api import Item, View
from chaco.api import ArrayPlotData, HPlotContainer, Plot
from enable.api import ComponentEditor

# Enthought imports
from traits.api import (Array, Callable, Enum, Float, HasTraits, Instance, Int,
                        Trait)
from traitsui.api import Group, HGroup, Item, View, spring, Handler
from pyface.timer.api import Timer

# Chaco imports
from chaco.chaco_plot_editor import ChacoPlotItem


from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


# Create an ADXL345 instance.
accel = Adafruit_ADXL345.ADXL345()

# Get I2C bus
bus = smbus.SMBus(1)
    
    
# Alternatively you can specify the device address and I2C bus with parameters:
#accel = Adafruit_ADXL345.ADXL345(address=0x54, busnum=2)

# You can optionally change the range to one of:
#  - ADXL345_RANGE_2_G   = +/-2G (default)
#  - ADXL345_RANGE_4_G   = +/-4G
#  - ADXL345_RANGE_8_G   = +/-8G
#  - ADXL345_RANGE_16_G  = +/-16G
# For example to set to +/- 16G:
#accel.set_range(Adafruit_ADXL345.ADXL345_RANGE_16_G)

# Or change the data rate to one of:
#  - ADXL345_DATARATE_0_10_HZ = 0.1 hz
#  - ADXL345_DATARATE_0_20_HZ = 0.2 hz
#  - ADXL345_DATARATE_0_39_HZ = 0.39 hz
#  - ADXL345_DATARATE_0_78_HZ = 0.78 hz
#  - ADXL345_DATARATE_1_56_HZ = 1.56 hz
#  - ADXL345_DATARATE_3_13_HZ = 3.13 hz
#  - ADXL345_DATARATE_6_25HZ  = 6.25 hz
#  - ADXL345_DATARATE_12_5_HZ = 12.5 hz
#  - ADXL345_DATARATE_25_HZ   = 25 hz
#  - ADXL345_DATARATE_50_HZ   = 50 hz
#  - ADXL345_DATARATE_100_HZ  = 100 hz (default)
#  - ADXL345_DATARATE_200_HZ  = 200 hz
#  - ADXL345_DATARATE_400_HZ  = 400 hz
#  - ADXL345_DATARATE_800_HZ  = 800 hz
#  - ADXL345_DATARATE_1600_HZ = 1600 hz
#  - ADXL345_DATARATE_3200_HZ = 3200 hz
# For example to set to 6.25 hz:
#accel.set_data_rate(Adafruit_ADXL345.ADXL345_DATARATE_6_25HZ)

print('Printing X, Y, Z axis values, press Ctrl-C to quit...')



"""
Visualization of simulated live data stream
Shows how Chaco and Traits can be used to easily build a data
acquisition and visualization system.
Two frames are opened: one has the plot and allows configuration of
various plot properties, and one which simulates controls for the hardware
device from which the data is being acquired; in this case, it is a mockup
random number generator whose mean and standard deviation can be controlled
by the user.
"""



class Viewer(HasTraits):
    """ This class just contains the two data arrays that will be updated
    by the Controller.  The visualization/editor for this class is a
    Chaco plot.
    """
    index = Array

    data = Array

    plot_type = Enum("line", "scatter")

    view = View(ChacoPlotItem("index", "data",
                              type_trait="plot_type",
                              resizable=True,
                              x_label="Time",
                              y_label="Z_Tremblements",
                              color="red",
                              bgcolor="white",
                              border_visible=True,
                              border_width=1,
                              padding_bg_color="lightgray",
                              width=800,
                              height=380,
                              marker_size=5,
                              show_label=False),
                HGroup(spring, Item("plot_type", style='custom'), spring),
                resizable = True,
                buttons = ["OK"],
                width=800, height=500)


class Controller(HasTraits):

    # A reference to the plot viewer object
    viewer = Instance(Viewer)

    # Some parameters controller the random signal that will be generated
    distribution_type = Enum("normal")
    mean = Float(0.0)
    stddev = Float(1.0)

    # The max number of data points to accumulate and show in the plot
    max_num_points = Int(100)

    # The number of data points we have received; we need to keep track of
    # this in order to generate the correct x axis data series.
    num_ticks = Int(0)

    # private reference to the random number generator.  this syntax
    # just means that self._generator should be initialized to
    # random.normal, which is a random number function, and in the future
    # it can be set to any callable object.
    _generator = Trait(np.random.normal, Callable)

    view = View(Group('distribution_type',
                      'mean',
                      'stddev',
                      'max_num_points',
                      orientation="vertical"),
                      buttons=["OK", "Cancel"])

    def timer_tick(self, *args):
        """
        Callback function that should get called based on a timer tick.  This
        will generate a new random data point and set it on the `.data` array
        of our viewer object.
        """
        # Generate a new number and increment the tick count
	    #x, y, z=accel.read()

        # ADXL345 address, 0x53(83)
        # Select bandwidth rate register, 0x2C(44)
        #		0x0A(10)	Normal mode, Output data rate = 100 Hz
        bus.write_byte_data(0x53, 0x2C, 0x0A)

        # ADXL345 address, 0x53(83)
        # Select power control register, 0x2D(45)
        #		0x08(08)	Auto Sleep disable
        bus.write_byte_data(0x53, 0x2D, 0x08)

        # ADXL345 address, 0x53(83)
        # Select data format register, 0x31(49)
        #		0x08(08)	Self test disabled, 4-wire interface
        #					Full resolution, Range = +/-2g

        bus.write_byte_data(0x53, 0x31, 0x08)
        # time.sleep(0.5)
        # ADXL345 address, 0x53(83)
        # Read data back from 0x32(50), 2 bytes
        # X-Axis LSB, X-Axis MSB

        data0 = bus.read_byte_data(0x53, 0x32)
        data1 = bus.read_byte_data(0x53, 0x33)

        # Convert the data to 10-bits
        xAccl = ((data1 & 0x03) * 256) + data0

        if xAccl > 511:
            xAccl -= 1024
        # ADXL345 address, 0x53(83)
        # Read data back from 0x34(52), 2 bytes
        # Y-Axis LSB, Y-Axis MSB
        data0 = bus.read_byte_data(0x53, 0x34)
        data1 = bus.read_byte_data(0x53, 0x35)

        # Convert the data to 10-bits
        yAccl = ((data1 & 0x03) * 256) + data0

        if yAccl > 511:
            yAccl -= 1024

        # ADXL345 address, 0x53(83)
        # Read data back from 0x36(54), 2 bytes
        # Z-Axis LSB, Z-Axis MSB
        data0 = bus.read_byte_data(0x53, 0x36)
        data1 = bus.read_byte_data(0x53, 0x37)

        # Convert the data to 10-bits
        zAccl = ((data1 & 0x03) * 256) + data0
        if zAccl > 511:
            zAccl -= 1024

        # Output data to screen
        # print "Acceleration in X-Axis : %d" %xAccl
        # print "Acceleration in Y-Axis : %d" %yAccl
        # print "Acceleration in Z-Axis : %d" %zAccl
        new_val = zAccl
        self.num_ticks += 1

        # grab the existing data, truncate it, and append the new point.
        # This isn't the most efficient thing in the world but it works.
        cur_data = self.viewer.data
        new_data = np.hstack((cur_data[-self.max_num_points+1:], [new_val]))
        new_index = np.arange(self.num_ticks - len(new_data) + 1,
                              self.num_ticks + 0.01)

        self.viewer.index = new_index
        self.viewer.data = new_data
        return

    def _distribution_type_changed(self):
        # This listens for a change in the type of distribution to use.
            while True:
                # Read the X, Y, Z axis acceleration values and print them.
                x, y, z = accel.read()
                print('X={0}, Y={1}, Z={2}'.format(x, y, z))
                # Wait half a second and repeat.
                time.sleep(0.1)
            self._generator = x


class DemoHandler(Handler):

    def closed(self, info, is_ok):
        """ Handles a dialog-based user interface being closed by the user.
        Overridden here to stop the timer once the window is destroyed.
        """

        info.object.timer.Stop()
        return


class Demo(HasTraits):
    controller = Instance(Controller)
    viewer = Instance(Viewer, ())
    timer = Instance(Timer)
    view = View(Item('controller', style='custom', show_label=False),
                Item('viewer', style='custom', show_label=False),
                handler=DemoHandler,
                resizable=True)

    def edit_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer=Timer(100, self.controller.timer_tick)
        return super(Demo, self).edit_traits(*args, **kws)

    def configure_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer=Timer(100, self.controller.timer_tick)
        return super(Demo, self).configure_traits(*args, **kws)

    def _controller_default(self):
        return Controller(viewer=self.viewer)


# NOTE: examples/demo/demo.py looks for a 'demo' or 'popup' or 'modal popup'
# keyword when it executes this file, and displays a view for it.
popup=Demo()


if __name__ == "__main__":
    popup.configure_traits()



