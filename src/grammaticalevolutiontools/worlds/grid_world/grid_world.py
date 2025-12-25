from .grid_position import GridPosition
from .grid_world_agent import GridWorldAgent
from .grid_layout import GridLayout
from .grid_world_object import GridWorldObject
from ..base.world import World
from .grid_world_animation import GridWorldAnimation, Color

from collections import defaultdict
from typing import Type, Tuple, List


AgentStartState = Tuple[GridPosition, GridWorldAgent.Direction]


class GridWorld[A: GridWorldAgent = GridWorldAgent, 
                L: GridLayout = GridLayout, 
                O: GridWorldObject = GridWorldObject](World[A, L, O]):
    """
    An Class used to create Worlds for Grammatical Evolution Problems. 

    A

    Attributes:
        width (int): A read-only property. The width of the world. 
        height (int): A read-only propery. The height of the world.
        amount (float): A read-only property. The amount of this reward.
        pos (Position): A read-only property. The position of this 
            reward in the world. 
        __world (World): A private property. The world to which this 
            reward belongs. 
    """

    type AgentMarker = Tuple[Type[A], 'GridPosition', GridWorldAgent.Direction]
    type ObjMarker = Tuple[Type[O], 'GridPosition']

    type ObjTrace = List[Tuple[ObjMarker]]
    type AgentTrace = List[Tuple[AgentMarker]]

    _min_agent_class = GridWorldAgent
    _min_obj_class = GridWorldObject
    _layout_class = GridLayout


    def __init__(self, layout: GridLayout, agents_can_share_spaces:bool=False, 
                 agents_wrap_around=False):
        """
            Initializes an instance of a World object.

            Arguments:
                width (int): The width of the world. 
                height (int): The height of the World. 
                agent_classes (list[type]): A list of valid classes for agents that will appear in this World. Each must be a subclass of provided Agent class.
                reward_types (list[tuple[str, float]] | list[type]): A list of valid types of rewards in this World. 
                                                                    Each element must be either a tuple with a (str, float) pair specifyng the type of reward and the amount, 
                                                                    or a class that is a sub-class of the default Reward class. 
                default_start_position (Position): The default starting position to give to Agents added to the World if none is provided for them. 
                                                This value defaults to (0,0)
                reward_symbols (list[str]): An optional list of one-character symbols representing each reward type. Used to par
                map_file_path: An optional path to a text file containing a map layout. 

            Returns:
            
        """
        super(GridWorld, self).__init__(layout=layout)

        self._agents_can_share_spaces: bool = agents_can_share_spaces
        self._agents_wrap_around = agents_wrap_around

        self._agent_positions: dict[GridPosition, set[A]] = defaultdict(set)
        self._object_positions: dict[GridPosition, list[O]] = defaultdict(list)

        self._agent_trace: GridWorld.AgentTrace = []
        self._obj_trace: GridWorld.ObjTrace = []

        self._agents_changed: bool = False
        self._objs_changed: bool = False

        self._recording: bool = False

    # - - Assertions - -
    
    def _assert_pos_valid_and_open_for_agent(self, pos: GridPosition):
        self._layout.assert_space_within_map_bounds(pos)
        if not self.position_passable(pos):
            raise GridLayout.InvalidPositionError(
                "'pos' blocked by an impassable object."
            )
        if not self._agents_can_share_spaces and self.position_occupied(pos):
            raise GridLayout.InvalidPositionError(
                "'pos' blocked by another agent."
            )
        
    def _assert_pos_valid_and_open_for_object(self, pos: GridPosition, obj_passable: bool):
        self._layout.assert_space_within_map_bounds(pos)
        _pos = GridPosition(pos)
        if _pos in self._object_positions:
            raise GridLayout.InvalidPositionError(
                "'pos' already occupied by another object."
            )
        if not obj_passable and self.position_occupied(_pos):
            raise GridLayout.InvalidPositionError(
                "Cannot place an impassable object where an "
                "agent is located."
            )

    # -- Agent and Object Position Trackers --

    def update_agent_position(self, agent: A, old_pos: GridPosition):
        if old_pos is not None:
            self._agent_positions[old_pos].remove(agent)
        self._agent_positions[agent.position].add(agent)
        self.flag_agent_change()

    def update_obj_position(self, obj: O, old_pos: GridPosition):
        if old_pos is not None:
            self._object_positions[old_pos].remove(obj)
        self._object_positions[obj.pos].append(obj)
        self.flag_object_change()


    # -- Position Query Functions

    def space_within_map_bounds(self, pos: GridPosition) -> bool:
        return self._layout.space_within_map_bounds(pos)
    
    def position_passable(self, pos: GridPosition) -> bool:
        _objs = self.get_objects_at_position(pos)
        for obj in _objs:
            if not obj.is_passable():
                return False  
            
        return True
    
    def position_occupied(self, pos: GridPosition) -> bool:
        _agents = self.get_agents_at_position(pos)
        return len(_agents) > 0
    
    def space_valid_and_open(self, pos: GridPosition) -> bool:
        cond1 = self.space_within_map_bounds(pos) and self.position_passable(pos)
        if self._agents_can_share_spaces:
            return cond1
        else:
            return cond1 and not self.position_occupied(pos)
        

    # - - Object Manipulation - -

    def add_object(self, obj: GridWorldObject, position: GridPosition):
        self._assert_object_valid(obj)
        self._assert_pos_valid_and_open_for_object(position, obj.is_passable())

        _pos = GridPosition(position)

        self._object_positions[_pos].append(obj)
        self._objects.add(obj)
        obj._set_pos(_pos)

        self.flag_object_change()
    
    def remove_object(self, obj: GridWorldObject):
        self._object_positions[obj.pos].remove(obj)
        self._objects.remove(obj)
        obj._set_pos(None)

        self.flag_object_change()
    
    def clear_objects(self):
        self._object_positions.clear()
        self._objects.clear()

        self.flag_object_change()
    
    def get_objects_at_position(self, pos: GridPosition) -> list[GridWorldObject]:
        _pos = GridPosition(pos)
        
        return list(self._object_positions[_pos])

    # - - Agent Manipulation - -
    
    def add_agent(self, agent: A, pos: GridPosition, 
                  dir: GridWorldAgent.Direction = None): 
        super().add_agent(agent)
        _pos = GridPosition(pos)
        self._agent_positions[_pos].add(agent)
        agent._set_position(_pos, dir)

        self.flag_agent_change()

    def remove_agent(self, agent: GridWorldAgent):
        super().remove_agent(agent)
        self._agent_positions[agent.position].remove(agent)

        self.flag_agent_change()

    def clear_agents(self):
        super().clear_agents()
            
        self._agent_positions.clear()

        self.flag_agent_change()

    def get_agents_at_position(self, pos: GridPosition) -> list[GridWorldAgent]:
        _pos = GridPosition(pos)
        return list(self._agent_positions[_pos])
    
    # - - Helpers for Resetting the World - -

    def _load_objects_from_layout(self):
        for pos, obj_class in self._layout.get_object_positions().items():
            self.add_object(obj_class(world=self), pos)

    def _load_agents(self, agent_start_states: dict[GridWorldAgent, AgentStartState]):
        for agent in agent_start_states:
            pos, dir = agent_start_states[agent]
            self.add_agent(agent, pos, dir)
            agent.reset()

    def load_new_agents(self, new_agents: dict[GridWorldAgent, AgentStartState],
                        recording_on=False):
        
        self.clear_objects()
        self.clear_agents()
        
        self._obj_trace.clear()
        self._agent_trace.clear()

        self._load_objects_from_layout()
        self._load_agents(new_agents)

        self._recording = recording_on

        self.flag_object_change()
        self.flag_agent_change()
        
        if self._recording:
            self._record_state()
        
    # - - World Trace - -

    def flag_agent_change(self):
        if self._recording:
            self._agents_changed = True

    def flag_object_change(self):
        if self._recording:
            self._objs_changed = True

    def _record_state(self):
        
        # record new state of agents if they have changed
        if self._agents_changed:
            agent_trace = []
            for pos, agents in self._agent_positions.items():
                for agent in agents:
                    agent_trace.append((type(agent), pos, agent.direction))
        else:
            agent_trace = self._agent_trace[-1]

        # record new state of objects if they have changed
        if self._objs_changed:
            obj_trace = []
            for pos, objs in self._object_positions.items():
                for obj in objs:
                    obj_trace.append((type(obj), pos))
        else:
            obj_trace = self._obj_trace[-1]

        self._agent_trace.append(tuple(agent_trace))
        self._obj_trace.append(tuple(obj_trace))

        self._agent_changed = False
        self._obj_changed = False


    def get_traces(self):
        return self._agent_trace.copy(), self._obj_trace.copy()

    # - - Simulation - - 

    def toggle_recording_on(self):
        self._recording = True

    def toggle_recording_off(self):
        self._recording = False

    def tick(self, num_steps=1):
        for _ in range(num_steps):
            for agent in self._agents:
                agent.tick()

            if self._recording:
                self._record_state()

    # - - Create Animation - -

    def generate_animation(self, bg_color, agent_colors: dict[Type['GridWorldAgent'], Color], 
                           obj_colors: dict[Type['GridWorldObject'], Color], arrow_color=None):
        
        return GridWorldAnimation(world_dims = (self.height, self.width),
                                  world_agent_trace=self._agent_trace, world_obj_trace=self._obj_trace,
                                  agent_colors=agent_colors, obj_colors=obj_colors,
                                  bg_color=bg_color, arrow_color=arrow_color)
    
    # - - 

    @property
    def initialized(self) -> bool:
        return self._layout is not None
    
    @property
    def recording(self) -> bool:
        return self._recording
    
    @property
    def num_agents(self) -> int:
        return len(self._agent_positions)
    
    @property
    def height(self) -> int:
        return self._layout.height
    
    @property
    def width(self) -> int:
        return self._layout.width
    
    def __hash__(self):
        return hash(id(self))
    
