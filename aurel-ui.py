from numpy import linspace, sin
from traits.api import HasTraits, Str, Range, Float, Enum, Instance
from traitsui.api import View, Group, Item, Label
from chaco.api import Plot, ArrayPlotData
from enable.api import ComponentEditor

class PumpIt(HasTraits):
    name = Str
    age = Range(1, 100)
    weight = Float
    gender = Enum('Male', 'Female')

    view = View(
        Group(
            Label('An Unthemed Label'),
            Item('name'),
            Item('age'),
            Item('weight'),
            Item('gender')
        ),
        title='Unthemed TraitsUI',
    )

PumpIt().configure_traits()