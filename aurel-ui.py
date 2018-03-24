from numpy import linspace, sin
from traits.api import HasTraits, Str, Range, Float, Enum, Instance
from traitsui.api import View, Group, Item, Label
from chaco.api import Plot, ArrayPlotData
from enable.api import ComponentEditor

class LinePlot(HasTraits):
    plot = Instance(Plot)
    plot2 = Instance(Plot)
    plot3 = Instance(Plot)

    traits_view = View(
        Item('plot', editor=ComponentEditor(), show_label=False),
        Item('plot2', editor=ComponentEditor(), show_label=False),
        Item('plot3', editor=ComponentEditor(), show_label=False),
        width=1000, height=650, resizable=False, title="Pump It")

    def _plot_default(self):
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x=x, y=y)

        plot = Plot(plotdata)
        plot.plot(("x", "y"), type="line", color="blue")
        plot.title = "sin(x) * x^3"
        return plot

if __name__ == "__main__":
    LinePlot().configure_traits()