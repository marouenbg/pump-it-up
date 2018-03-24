from numpy import linspace, sin
from traits.api import HasTraits, Instance
from traitsui.api import View, Item
from chaco.api import Plot, ArrayPlotData
from enable.api import ComponentEditor

class LinePlot(HasTraits):
    plot = Instance(Plot)

    traits_view = View(
        Item('plot', editor=ComponentEditor(), show_label=False),
        width=1000, height=700, resizable=False, title="Pump It")

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