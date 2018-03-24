import time
import sys
import smbus
import Adafruit_ADXL345

from chaco.default_colormaps import hot
from numpy import zeros, linspace, short, fromstring, hstack, transpose, sin
from traits.api import (Array, Callable, Enum, Float, HasTraits, Instance, Int,
                        Trait)
from traitsui.api import Item, Group, View, Handler
from chaco.api import Plot, ArrayPlotData, HPlotContainer
from enable.api import Component, ComponentEditor
from pyface.timer.api import Timer

NUM_SAMPLES = 1024
SAMPLING_RATE = 11025
SPECTROGRAM_LENGTH = 100

# Create an ADXL345 instance.
accel = Adafruit_ADXL345.ADXL345()

# Get I2C bus
bus = smbus.SMBus(1)

def _create_plot_component(obj):
    # Setup the xaxis plot
    frequencies = linspace(0.0, float(SAMPLING_RATE)/2, num=NUM_SAMPLES/2)
    obj.spectrum_data = ArrayPlotData(frequency=frequencies)
    empty_amplitude = zeros(NUM_SAMPLES/2)
    obj.spectrum_data.set_data('amplitude', empty_amplitude)

    obj.spectrum_plot = Plot(obj.spectrum_data)
    obj.spectrum_plot.plot(("frequency", "amplitude"), name="Spectrum",
                           color="red")
    obj.spectrum_plot.padding = 50
    obj.spectrum_plot.title = "Spectrum"
    spec_range = obj.spectrum_plot.plots.values()[0][0].value_mapper.range
    spec_range.low = 0.0
    spec_range.high = 5.0
    obj.spectrum_plot.index_axis.title = 'Frequency (Hz)'
    obj.spectrum_plot.value_axis.title = 'Amplitude'

    yaxis = linspace(0.0, float(SAMPLING_RATE) / 2, num=NUM_SAMPLES / 2)
    obj.yaxis_data = ArrayPlotData(frequency=yaxis)
    empty_amplitude = zeros(NUM_SAMPLES / 2)
    obj.yaxis_data.set_data('amplitude', empty_amplitude)

    obj.yaxis_plot = Plot(obj.spectrum_data)
    obj.yaxis_plot.plot(("frequency", "amplitude"), name="yaxis",
                        color="red")
    obj.yaxis_plot.padding = 50
    obj.yaxis_plot.title = "Spectrum"
    spec_range = obj.yaxis_plot.plots.values()[0][0].value_mapper.range
    spec_range.low = 0.0
    spec_range.high = 5.0
    obj.yaxis_plot.index_axis.title = 'Frequency (Hz)'
    obj.yaxis_plot.value_axis.title = 'Amplitude'

    container = HPlotContainer()
    container.add(obj.spectrum_plot)
    container.add(obj.yaxis)

    return container

class DemoHandler(Handler):

    def closed(self, info, is_ok):
        """ Handles a dialog-based user interface being closed by the user.
        Overridden here to stop the timer once the window is destroyed.
        """

        info.object.timer.Stop()
        return


class Controller(HasTraits):
    # A reference to the plot viewer object

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
        # x, y, z=accel.read()

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
        new_val = xAccl
        self.num_ticks += 1

        # grab the existing data, truncate it, and append the new point.
        # This isn't the most efficient thing in the world but it works.
        cur_data = self.viewer.data
        new_data = np.hstack((cur_data[-self.max_num_points + 1:], [new_val]))
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


size = (900, 500)
title = "Audio Spectrum"


class Demo(HasTraits):

    plot = Instance(Component)

    controller = Instance(Controller, ())

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        orientation="vertical"),
                    resizable=True, title=title,
                    width=size[0], height=size[1],
                    handler=DemoHandler
                    )

    def __init__(self, **traits):
        super(Demo, self).__init__(**traits)
        self.plot = _create_plot_component(self.controller)

    def edit_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(20, self.controller.onTimer)
        return super(Demo, self).edit_traits(*args, **kws)

    def configure_traits(self, *args, **kws):
        # type: (object, object) -> object
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(20, self.controller.onTimer)
        return super(Demo, self).configure_traits(*args, **kws)


popup = Demo()

if __name__ == "__main__":
    popup.configure_traits()