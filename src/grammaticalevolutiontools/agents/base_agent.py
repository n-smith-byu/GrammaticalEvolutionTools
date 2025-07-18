from ..programs import ProgramTree
from ..programs.nodes.basic_nodes import RootNode

from abc import ABC, abstractmethod
from uuid import uuid4

from typing import TYPE_CHECKING, Type
from numbers import Number

if TYPE_CHECKING:
    from ..worlds import World

class Agent(ABC):

    class WorldNotSetError(RuntimeError):
        def __init__(self, msg):
            super(Agent.WorldNotSetError, self).__init__(msg)

    class ProgramError(RuntimeError):
        def __init__(self, msg):
            super(Agent.ProgramError, self).__init__(msg)

    class AgentAlreadyInWorldError(AssertionError):
        def __init__(self, msg):
            super(Agent.AgentAlreadyInWorldError, self).__init__(msg)

    _world_class = None

    @classmethod
    def valid_world_classes(cls) -> bool:
        return NotImplemented
    
    @classmethod
    @abstractmethod
    def get_default_program_root_type(cls) -> Type[RootNode]:
        "Must Return a subclass of AbstractProgramTree.Nodes.RootNode"
        return NotImplemented
    
    # - - Initialization - -

    def __init__(self, program: ProgramTree = None):

        self._world: World = None
        self._score = 0
        self._num_actions = 0
        self._program: ProgramTree = None
        self._uuid = uuid4()       # just to make hashable

        if program is None:
            # generate a new program
            root_node_type = type(self).get_default_program_root_type()
            program = ProgramTree(root_node_type)

        self._set_program(program)

    def _set_program(self, program: ProgramTree):
        self._assert_valid_program(program)

        self._program = program
        program._set_agent(self)

    # - - Assertions - -

    def _assert_not_in_world(self):
        if self.assigned_to_world():
            raise Agent.AgentAlreadyInWorldError(
                "Cannot add agent to world because agent is already in another world. "
                "Remove agent from that world first. "
                )
        
    def _assert_world_valid(self, world: 'World'):
        if self._world_class and not isinstance(world, self._world_class):
            raise TypeError("Attempting to add agent to an imcompatible world type.")
        
    def _assert_valid_program(self, program: ProgramTree):
        if not isinstance(program, ProgramTree):
            raise TypeError('program must be an instance of Program.')
        if program.agent and program.agent is not self:
            raise ValueError(
                "Cannot bind program to this agent when program is already "
                "bound to another agent. Unbind the program first."
                )
        
    # - - World Internal Access - -

    def _set_world(self, world: 'World'):
        self._assert_world_valid(world)
        self._assert_not_in_world()

        self._world = world

    def _reset(self):
        if self._program.running():
            self._program.kill()

        self._world = None
        self._num_actions = 0
        self._score = 0

    # - - Running Program - -

    def replace_program(self, new_program: ProgramTree) -> ProgramTree:
        old = self._program
        try:
            self._set_program(new_program)
        except (TypeError, ValueError) as e:
            self._set_program(old)
            raise e

        return old

    def copy_program(self):
        return self._program.copy()

    def execute_program(self, n=1):
        """
        Resets the program and runs to completion once.
        """
        if self._program.running():
            self._program.kill()

        self._program.run(n=n)

    def tick(self, loop: bool=True):
        """
            Runs the program through the next executable node. Exits if run and no nodes are left. 
            If loop is True (default), then the program will restart rather than exiting. 
        """
        if self.requires_world and not self.assigned_to_world():
            raise Agent.WorldNotSetError("Cannot run program without agent being assigned a world unless this is a worldless agent.")

        status = self._program.tick()
        if status == ProgramTree.Status.EXITED and loop:
            self._program.tick()

    def give_reward(self, amount):
        self._score += amount


    # - - Listeners - -

    def _on_action_taken(self):
        self._record_action()

    # - - Operations - - 

    def _record_action(self):
        self._num_actions += 1

    # - - Getters - -

    def assigned_to_world(self):
        return self._world is not None
    
    @property
    def program(self) -> ProgramTree:
        return self._program
    
    @property
    def score(self) -> Number:
        return self._score
    
    @property
    def num_actions(self) -> int:
        return self._num_actions
    
    @property
    def requires_world(self):
        return self._world_class is not None
    
    # - - Other Methods - -
    
    def __hash__(self):
        return hash(self._uuid)
