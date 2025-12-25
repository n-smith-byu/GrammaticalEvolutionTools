from ..base.layout import WorldPosition

from numbers import Integral

# Coordinates for a standard 2D Grid World
class GridPosition(WorldPosition):
    _required_length = 2
    _dtype = Integral
