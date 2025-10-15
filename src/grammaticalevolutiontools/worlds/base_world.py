from .layouts import WorldLayout
from .objects import WorldObject
from ..agents import Agent

from typing import Type, Generic, TypeVar, ClassVar, get_origin, get_args

from abc import ABC, abstractmethod


class World[A: Agent, L: WorldLayout, O: WorldObject](ABC):

    _min_agent_class: ClassVar[Type[A]]
    _min_layout_class: ClassVar[Type[L]]
    _min_obj_class: ClassVar[Type[O]]

    # - - Static Assertions - - 

    @staticmethod
    def _assert_layout_locked(layout: L):
        if not layout.locked():
            raise WorldLayout.LayoutNotLockedError(
                "Layout mut be locked before it can be used in a World Object"
                )
        
    # - - Class Methods - -

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs) 

        # 1. Start by inheriting parent's types (safer MRO check)
        parent: Type[World] | None = next(
            (b for b in cls.__mro__[1:] if hasattr(b, "_min_agent_class")), 
             None)
        
        if parent:
            cls._min_agent_class = parent._min_agent_class
            cls._min_layout_class = parent._min_layout_class
            cls._min_obj_class = parent._min_obj_class
        else:
            # Fallback to the explicit base bounds
            cls._min_agent_class = Agent
            cls._min_layout_class = WorldLayout
            cls._min_obj_class = WorldObject

        # 2. Override based on explicit generic specialization
        for base in getattr(cls, "__orig_bases__", []):
            if get_origin(base) is World:
                args = get_args(base)
                if len(args) != 3:
                    raise TypeError(
                        f"{cls.__name__} must specify either all three type parameters or none"
                    )
                
                # CORRECTION 3: Compare arguments to the concrete bound classes (Agent, WorldLayout, WorldObject)
                if args[0] is not Agent:
                    cls._min_agent_class = args[0]
                if args[1] is not WorldLayout:
                    cls._min_layout_class = args[1]
                if args[2] is not WorldObject: # Assuming WorldObject is the bound/default
                    cls._min_obj_class = args[2]
                break

    @classmethod
    def _assert_agent_valid(cls, agent):
        if not isinstance(agent, cls._min_agent_class):
            raise TypeError(f"Agent must be an instance of {cls._min_agent_class.__name__}")
        
    @classmethod
    def _assert_object_valid(cls, object):
        if not isinstance(object, cls._min_obj_class):
            raise TypeError(f"Object must be an instance of {cls._min_obj_class.__name__}")
        
    @classmethod
    def _assert_layout_valid(cls, layout):
        if not isinstance(object, cls._min_layout_class):
            raise TypeError(f"Layout must be an instance of {cls._min_layout_class.__name__}")
        cls._assert_layout_locked(layout)
        

    # - - Instance Methods - - 
    
    def __init__(self, layout: L): 
        self._assert_layout_valid()
        self._layout: L = layout

        self._agents: set[A] = {}
        self._objects: set[O] = {}

    def add_agent(self, agent: A):
        self._assert_agent_valid(agent)
        self._agents.add(agent)
        agent._set_world(self)
        agent.reset()

    def add_object(self, object: O):
        self._assert_object_valid(object)
        self._objects.add(object)

    def remove_agent(self, agent: A):
        self._agents.remove(agent)
        agent._clear_world()

    def remove_object(self, object: O):
        self._objects.remove(object)

    def get_all_agents(self):
        return self._agents.copy()
    
    def get_all_objects(self):
        return self._objects.copy()
    
    def clear_agents(self):
        for agent in self._agents:
            agent._clear_world()
            agent.reset()

        self._agents.clear()

    def clear_objects(self):
        self._objects.clear()

    @abstractmethod
    def _load_objects_from_layout(self):
        pass

    @abstractmethod
    def _load_agents(self):
        """
        Loads a new batch of agnts into the world.
        """
        pass

    @abstractmethod
    def tick(self):
        pass
    