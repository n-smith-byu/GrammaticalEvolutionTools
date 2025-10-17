from ...agents import Agent, AgentProgramTree
from .grid_world_object import GridWorldObject
from .grid_position import GridPosition

import numpy as np

from typing import TYPE_CHECKING
from numbers import Integral
from enum import Enum

if TYPE_CHECKING:
    from .grid_world import GridWorld

class GridBasedAgent(Agent):

    ######################################
    # -- Class Properties and Methods -- #
    ######################################

    class Direction(Enum):
        RIGHT = 0
        DOWN = 1
        LEFT = 2
        UP = 3

        # Override subtraction to wrap around
        def __add__(self, value):
            if not isinstance(value, Integral):
                raise TypeError(f"Unsupported operand type(s) for +=: 'Direction' and '{type(value).__name__}'")
            
            return GridBasedAgent.Direction((self.value + value) % 4) 
        
        # Override subtraction to wrap around
        def __sub__(self, value):
            if not isinstance(value, Integral):
                raise TypeError(f"Unsupported operand type(s) for +=: 'Direction' and '{type(value).__name__}'")
            
            return GridBasedAgent.Direction((self.value - value) % 4) 
        
        def __eq__(self, value):
            return self.value == value
        
        def __index__(self):
            return self.value

    _DIRECTIONS = [(0,1),          # Right
                   (1,0),          # Down
                   (0,-1),         # Left
                   (-1,0)]         # Up
    
    @classmethod
    def direction_to_vec(cls, dir: Direction):
        return np.array(cls._DIRECTIONS[dir])
    
    @classmethod
    def valid_world_classes(cls):
        if not cls._world_class:
            from .grid_world import GridWorld
            cls._world_class = GridWorld

        return [cls._world_class]


    ###############################
    # - - Instance Definition - - #
    ###############################

    def __init__(self, program: AgentProgramTree = None, autogen=True):
        super(GridBasedAgent, self).__init__(program, autogen)

        self._world: 'GridWorld'
        self._pos: GridPosition = None
        self._curr_dir: GridBasedAgent.Direction = GridBasedAgent.Direction.RIGHT

    def _set_world(self, world: 'GridWorld'):
        from .grid_world import GridWorld

        if not isinstance(world, GridWorld):
            raise TypeError(f"Agent must be bound to an instance of GridWorld to function properly. Instead found object of type {type(world)}")
            
        return super()._set_world(world)
    
    def _clear_world(self):
        super()._clear_world()
        self._pos = None

    def _set_position(self, pos: GridPosition):
        """
            Sets the world and position of an agent in the world. 
            Reserved for use by World class to add agents internally.

            Parameters:
            world (GridWorld): the instance of GridWorld to which this agent is being added
            pos (GridPosition): the position of this agent in the world to start. 

        """     
        if self._requires_world and self._world is None:
            raise Agent.WorldNotSetError("Cannot set position of agent in world when world is not set")
        
        self._pos = GridPosition(pos)


    # -- Assertions --

    # -- Listeners --

    def _on_changed_pos(self, old_pos):
        self._world.update_agent_position(agent=self, old_pos=old_pos)
        
    def _on_action_taken(self):
        super()._on_action_taken()
        self._trigger_obj_on_curr_space()

    def _on_changed_direction(self):
        self._world.flag_agent_change()

    # - - Helpers - -

    def _trigger_obj_on_curr_space(self):
        objs_at_pos: list[GridWorldObject] = self._world.get_objects_at_position(self._pos)       # get the object on top
        if len(objs_at_pos) > 0:
            objs_at_pos[-1].trigger(agent=self)

    # - - Operations - -

    def give_reward(self, amount):
        super().give_reward(amount)

    def wait(self):
        self._on_action_taken()

    def turn_left(self):
        self._curr_dir -= 1
        self._on_action_taken()
        self._on_changed_direction()

    def turn_right(self):
        self._curr_dir += 1
        self._on_action_taken()
        self._on_changed_direction()

    def turn_around(self):
        self._curr_dir += 2
        self._on_action_taken()
        self._on_changed_direction()

    def move_forward(self, ignore_other_agents=False):
        _old_pos = self._pos
        new_pos = self._pos + GridBasedAgent._DIRECTIONS[self._curr_dir]
        
        if self._world.space_valid_and_open(new_pos):
            if ignore_other_agents or not self._world.position_occupied(new_pos):
                self._pos = new_pos
                self._on_changed_pos(_old_pos)

        self._on_action_taken()
            
    # - - Getters - -
    
    @property
    def position(self):
        return self._pos
    
    @property
    def direction(self) -> Direction:
        return self._curr_dir
    
    # - - Magic Methods - -

    def __repr__(self):
        program_str = str(self._program)
        if self._program:
            program_str = f"'{program_str if len(program_str) <= 25 \
                              else (program_str[:25] + '...')}'"
            
        return f"({type(self).__name__}, " + \
               f"world={type(self._world).__name__ if self._world is not None else 'None'}, " + \
               f"program={program_str}, " + \
               f"pos={self._pos if self._pos is not None else 'None'}, " + \
               f"dir={self._curr_dir.name}, " + \
               f"rewards={self._score})"