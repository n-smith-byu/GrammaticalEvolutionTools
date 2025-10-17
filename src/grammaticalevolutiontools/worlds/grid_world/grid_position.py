from .._base.position import WorldPosition


class GridPosition(WorldPosition):

    __array_priority__ = 10     # for predence with __eq__ with numpy arrays on the left side of ==
    _required_length = 2

    def _coords_valid(self, obj):
        return super()._coords_valid(obj) and all(isinstance(x, int) for x in obj)
    
