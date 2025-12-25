from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world import World
    from ....agents import Agent

class WorldObject(ABC):
    """
    The abstract base class for all entities that exist within a :class:`World`.

    A ``WorldObject`` represents a physical or logical entity that can occupy 
    space in the environment and respond to agent interactions. This class 
    serves as the primary extension point for creating environmental features 
    such as food, obstacles, or markers.

    Note:
        Subclasses must implement the :meth:`trigger` method to define how the 
        object responds when an agent interacts with it.

    Attributes:
        world (World): A read-only property returning the :class:`World` 
            instance this object belongs to.
    """
    _world_cls = None

    def __init__(self, world:'World'):
        """
        Initializes the WorldObject and binds it to a specific World.

        Args:
            world (World): The world instance where this object resides.

        Raises:
            TypeError: If the provided ``world`` is not an instance of 
                the expected :class:`World` class.
        """
        if self._world_cls is None:
            from ..world import World
            self._world_cls = World
        
        if not isinstance(world, self._world_cls):
            raise TypeError('world must be an instance of World class')
    
        self._world: 'World' = world
    
    @property
    def world(self) -> 'World':
        """
        The world instance this object is currently associated with.

        Returns:
            World: The associated world.
        """
        return self._world
    
    @abstractmethod
    def trigger(self, agent: 'Agent'):
        """
        Defines the behavior for when an :class:`Agent` interacts with 
        this object.

        This is a mandatory abstract method. In subclasses that also inherit 
        from :class:`~.RewardObjectMixin`, this method is typically where 
        :meth:`~._give_reward` should be invoked.

        Args:
            agent (Agent): The agent instance that triggered the interaction.

        """
        pass