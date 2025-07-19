from .layouts import WorldLayout
from .objects import WorldObject
from ..agents import Agent

from typing import Type

from abc import ABC, abstractmethod

class World(ABC):

    _LAYOUT_CLASS = WorldLayout

    # - - Static Assertions - - 

    @staticmethod
    def _assert_layout_locked(layout: WorldLayout):
        if not layout.locked():
            raise WorldLayout.LayoutNotLockedError(
                "Layout mut be locked before it can be used in a World Object"
                )
        
    @staticmethod
    def _assert_agent_class_valid(agent_class: Type[Agent]):
        if not isinstance(agent_class, type) or not issubclass(agent_class, Agent):
            raise TypeError(
                "agent_class must be a subclass of GrammaticalEvolutionTools.Agents.Agent"
                )
        
    @staticmethod
    def _assert_obj_class_valid(obj_class: Type[WorldObject]):
        if not isinstance(obj_class, type) or not issubclass(obj_class, WorldObject):
            raise TypeError(
                "obj_class must be a subclass of GrammaticalEvolutionTools.World.Objects.WorldObject"
                )
        
    # - - Local Assertions - - 

    def _assert_valid_layout(self, layout: WorldLayout):
        if not isinstance(layout, self._LAYOUT_CLASS):
            raise TypeError(
                f"Layout must be an instance of {self._LAYOUT_CLASS.__name__}. "
                )
        self._assert_layout_locked(layout)

    def _assert_agent_valid(self, agent_or_class):
        agent_class = agent_or_class if isinstance(agent_or_class, type) else type(agent_or_class)

        if agent_class not in self._valid_agent_classes:
            raise TypeError("Agent type not in Agent classes specified for this World. " + \
                            f"Valid classes include the following types: {tuple(cl for cl in self._valid_agent_classes)}. ")
            
    def _assert_obj_valid(self, obj_or_class):
        obj_class = obj_or_class if isinstance(obj_or_class, type) else type(obj_or_class)
        if obj_class not in self._valid_object_classes:
            raise TypeError("'obj_class' must be a valid Worldbject class specified for this World. " + \
                            f"Valid classes include the following types: {tuple(cl.__name__ for cl in self._valid_object_classes)}. ")
        

    # - - Initialization - - 

    def __init__(self, agent_classes:list[Type[Agent]], obj_types:list[Type[WorldObject]],
                 world_layout: WorldLayout):
        
        self._valid_agent_classes: set[Type[Agent]] = set()
        self._valid_object_classes: set[Type[WorldObject]] = set()
    
        for cl in agent_classes:
            World._assert_agent_class_valid(cl)
            self._valid_agent_classes.add(cl)

        for cl in obj_types:
            World._assert_obj_class_valid(cl)
            self._valid_object_classes.add(cl)
        
        self._assert_valid_layout(world_layout)
        self._layout: WorldLayout = world_layout

        self._agents: set[Agent] = set()
        self._objects: set[WorldObject] = set()

        self._agent_trace: list = []
        self._obj_trace: list = []

        self._recording: bool = False


    # - - - -

    def get_valid_agent_classes(self) -> set[Type[Agent]]:
        return self._valid_agent_classes.copy()
    
    def get_valid_obj_classes(self) -> set[Type[WorldObject]]:
        return self._valid_object_classes.copy()

    def get_all_agents(self):
        return self._agents.copy()
    
    def get_all_objects(self):
        return self._objects.copy()
    
    @abstractmethod
    def tick(self):
        pass

    @abstractmethod
    def load_new_agents(self):
        """
        Resets the world with a new batch of agents.
        """
        pass
    