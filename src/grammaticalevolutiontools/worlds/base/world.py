from .layout import WorldLayout
from .objects import WorldObject
from ...agents import Agent

from typing import Self, List

from abc import ABC, abstractmethod


class World[A: Agent, L: WorldLayout, O: WorldObject](ABC):         # generics for type checking only

    # - - Static Assertions - - 

    @staticmethod
    def _assert_layout_locked(layout: L):
        if not layout.locked():
            raise WorldLayout.LayoutNotLockedError(
                "Layout mut be locked before it can be used in a World Object"
                )
        
    # - - Class Methods - -

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        parent = next((b for b in cls.__mro__[1:] if hasattr(b, "_min_agent_class")), None)

        # 3) Enforce narrowing: subclass override must be a subclass of parent's
        if parent is not None:
            for attr, parent_attr in (
                ("_min_agent_class", parent._min_agent_class),
                ("_min_obj_class", parent._min_obj_class),
                ("_layout_class", parent._layout_class),
            ):
                sub_attr = getattr(cls, attr)
                if sub_attr is None:
                    # allow None to mean "not set" (should not normally happen here)
                    continue
                if parent_attr is not None and not issubclass(sub_attr, parent_attr):
                    raise TypeError(
                        f"{cls.__name__}.{attr} = {sub_attr.__name__} "
                        f"must be a subclass of {parent_attr.__name__}"
                    )

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
        if not isinstance(layout, cls._layout_class):
            raise TypeError(f"Layout must be an instance of {cls._min_layout_class.__name__}")
        cls._assert_layout_locked(layout)

    @classmethod
    def base_agent_class(cls):
        return cls._min_agent_class

    @classmethod
    def base_object_class(cls):
        return cls._min_obj_class

    @classmethod
    def layout_class(cls):
        cls._layout_class
        
    
    _min_agent_class = Agent
    _min_obj_class = WorldObject
    _layout_class = WorldLayout
        

    # - - Instance Methods - - 
    
    def __init__(self, layout: L): 
        self._assert_layout_valid(layout)
        self._layout: L = layout

        self._agents: set[A] = set()
        self._objects: set[O] = set()

    def add_agent(self, agent: A) -> Self:
        self._assert_agent_valid(agent)
        self._agents.add(agent)
        agent._set_world(self)
        agent.reset()
        return self

    def add_object(self, object: O) -> Self:
        self._assert_object_valid(object)
        self._objects.add(object)
        return self

    def remove_agent(self, agent: A) -> Self:
        self._agents.remove(agent)
        agent._clear_world()
        return self

    def remove_object(self, object: O) -> Self:
        self._objects.remove(object)
        return self

    def get_all_agents(self):
        return self._agents.copy()
    
    def get_all_objects(self):
        return self._objects.copy()
    
    def clear_agents(self) -> Self:
        for agent in self._agents:
            agent._clear_world()
            agent.reset()
        self._agents.clear()
        return self

    def clear_objects(self) -> Self:
        self._objects.clear()
        return self
    
    def clear_world(self) -> Self:
        self.clear_agents()
        self.clear_objects()
        return self

    @abstractmethod
    def _load_objects_from_layout(self) -> Self:
        return self
    
    @abstractmethod
    def load_new_agents(self, agents: List[A]):
        pass

    @abstractmethod
    def tick(self):
        pass
    