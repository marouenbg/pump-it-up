from numpy import linspace, sin
from traits.api import HasTraits, Str, Range, Float, Enum, Instance
from traitsui.api import View, Group, Item, Label
from chaco.api import Plot, ArrayPlotData
from enable.api import ComponentEditor

class PumpIt(HasTraits):
    plot = Instance(Plot)

    traits_view = View(
        Item('plot', editor=ComponentEditor(), show_label=False),
        width=1000, height=650, resizable=False, title="Pump It")

    def _plot_default(self):
        x = linspace(-100, 100, 1000)
        y = sin(x)

        plotdata = ArrayPlotData(x=x, y=y)

        plot = Plot(plotdata)

        plot.plot(("x", "y"), type="line", color="blue")
        plot.title = "sin(x)"

        return plot

if __name__ == "__main__":
    PumpIt().configure_traits()