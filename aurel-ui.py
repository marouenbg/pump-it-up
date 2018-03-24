from numpy import linspace, sin
from traits.api import HasTraits, Instance
from traitsui.api import View, Item
from chaco.api import Plot, ArrayPlotData
from enable.api import ComponentEditor

# unthemed.py -- Example of a TraitsUI without themes
from traits.api import HasTraits, Str, Range, Float, Enum
from traitsui.api import View, Group, Item, Label
class Test ( HasTraits ):

    name   = Str
    age    = Range( 1, 100 )
    weight = Float
    gender = Enum( 'Male', 'Female' )

    view = View(
        Group(
            Label( 'An Unthemed Label' ),
            Item( 'name' ),
            Item( 'age' ),
            Item( 'weight' ),
            Item( 'gender' )
        ),
        title   = 'Unthemed TraitsUI',
    )

Test().configure_traits()