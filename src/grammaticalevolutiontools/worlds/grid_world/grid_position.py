from .._base.position import WorldPosition

from numbers import Integral


class GridPosition(WorldPosition):
    _required_length = 2
    _dtype = Integral
