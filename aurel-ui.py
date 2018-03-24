from numpy import linspace, sin
from traits.api import HasTraits, Str, Range, Float, Enum, Instance
from traitsui.api import View, Group, Item, Label
from chaco.api import Plot, ArrayPlotData
from enable.api import ComponentEditor

class PumpIt(HasTraits):
    plot1 = Instance(Plot)
    plot2 = Instance(Plot)
    plot3 = Instance(Plot)

    traits_view = View(
        Item('plot1', editor=ComponentEditor(), show_label=False),
        Item('plot2', editor=ComponentEditor(), show_label=False),
        Item('plot3', editor=ComponentEditor(), show_label=False),
        width=1000, height=650, resizable=False, title="Pump It")

    def _plot_default(self):
        x = linspace(-100, 100, 1000)
        y1 = sin(x)
        y2 = cos(x)
        y3 = log(x)

        plotdata1 = ArrayPlotData(x=x, y=y1)
        plotdata2 = ArrayPlotData(x=x, y=y2)
        plotdata3 = ArrayPlotData(x=x, y=y3)

        plot1 = Plot(plotdata1)
        plot2 = Plot(plotdata2)
        plot3 = Plot(plotdata3)

        plot1.plot(("x", "y1"), type="line", color="blue")
        plot1.title = "sin(x)"

        plot2.plot(("x", "y2"), type="line", color="red")
        plot2.title = "cos(x)"

        plot3.plot(("x", "y3"), type="line", color="red")
        plot3.title = "log(x)"
        return true

if __name__ == "__main__":
    PumpIt().configure_traits()