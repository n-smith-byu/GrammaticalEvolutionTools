from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import World
    from ...agents import Agent

class WorldObject(ABC):
    def __init__(self, world:'World'):

        from .. import World
        
        if not isinstance(world, World):
            raise TypeError('world must be an instance of World class')
    
        self._world: 'World' = world
    
    @property
    def world(self) -> 'World':
        return self._world
    
    @abstractmethod
    def trigger(self, agent: 'Agent'):
        """
        Callable Function. Defines behavior for when an agent interacts with this object. 
        """
        return NotImplemented
