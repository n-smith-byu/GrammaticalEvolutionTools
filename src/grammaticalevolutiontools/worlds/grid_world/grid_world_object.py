from .._base.object import WorldObject
from .grid_position import GridPosition

from abc import abstractmethod
from enum import Enum

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .grid_world import GridWorld


class GridWorldObject(WorldObject):

    @classmethod
    @abstractmethod
    def is_passable(self) -> bool:
        return NotImplemented

    def __init__(self, world: 'GridWorld', pos = None):

        super(GridWorldObject, self).__init__(world)
        self._assert_world_is_grid_world(world)

        self._world: 'GridWorld' = world
        self._is_passable: bool = type(self).is_passable()
        self._ignore_passability: bool = False
        self._pos = None

    # -- Assertions --
    def _assert_world_is_grid_world(self, world):
        from .grid_world import GridWorld
        if not isinstance(world, GridWorld):
                raise TypeError('world must be an instance of GridWorld')

    def is_passable(self) -> bool:
        return self._is_passable

    def _set_pos(self, pos: GridPosition):
        self._pos = pos

    @property
    def pos(self):
        return self._pos
    
