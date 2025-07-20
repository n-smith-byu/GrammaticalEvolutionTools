from .agent_program import AgentProgramTree
from ..grammars import Grammar

from numbers import Number
from uuid import uuid4

from typing import Type, TYPE_CHECKING
import warnings

if TYPE_CHECKING:
    from ..worlds import World

class Agent:

    @classmethod
    def default_grammar(cls) -> Grammar:
        return None
    
    @classmethod
    def default_program_cls(cls) -> Type[AgentProgramTree]:
        if not cls._default_program_cls:
            default_grammar = cls.default_grammar()
            if default_grammar:
                class AgentProgram(AgentProgramTree):
                    _GRAMMAR = default_grammar
                    pass

                cls._default_program_cls = AgentProgram
        
        return cls._default_program_cls
    
    _default_program_cls = None

    # - - Exceptions - - 

    class WorldNotSetError(RuntimeError):
        pass

    class AlreadyInWorldError(RuntimeError):
        pass

    class AssignedProgramError(RuntimeError):
        pass

    class NotAssignedProgramError(RuntimeError):
        pass

    # - - Initialization - -

    def __init__(self, program: AgentProgramTree = None, autogen=True):
        self._world: World = None
        self._program: AgentProgramTree = None
        self._uuid = uuid4()       # just to make hashable

        self._score = 0
        self._num_actions = 0

        if program:
            self._assert_valid_program(program)
            self._set_program(program)
        elif autogen:
            program_cls = self.default_program_cls()
            if not program_cls:
                warnings.warn(
                        "Tried to create Program, but no default " \
                        "grammar found for agent class " \
                        f"{type(self).__name__}.",
                        UserWarning
                        )
            self._set_program(program_cls())
        
    # - - Assertions - -

    def _assert_not_in_world(self):
        if self.assigned_to_world():
            raise Agent.AlreadyInWorldError(
                "Cannot add agent to world because agent is already in another world. "
                "Remove agent from that world first. "
                )
        
    def _assert_not_assigned_program(self):
        if self._program:
            raise Agent.AssignedProgramError(
                "Cannot set program when agent is already assigned a program. "
                "Please remove old program first."
            )
        
    def _assert_valid_program(self, program):
        if not isinstance(program, AgentProgramTree):
            raise TypeError('program must be an instance of AgentProgramTree.')
        if program.agent and program.agent is not self:
            raise ValueError(
                "Cannot bind program to this agent when program is already "
                "bound to another agent. Unbind the program first."
                )
        
    # - - World Internal Access - -

    def _set_world(self, world: 'World'):
        self._assert_not_in_world()

        self._world = world

    # - - Helpers - - 

    def _set_program(self, program: AgentProgramTree):
        self._program = program
        if program: 
            program._set_agent(self)

    def _remove_program(self) -> AgentProgramTree:
        program = self._program
        program._set_agent(None)
        self._program = None
        
        return program
    
    def _replace_program(self, new_program: AgentProgramTree) -> AgentProgramTree:
        old = self._remove_program()
        try:
            self._set_program(new_program)
        except (TypeError, ValueError) as e:
            self._set_program(old)
            raise e

        return old
    
    # - - Public - - 

    def reset(self, program: AgentProgramTree = None):
        if program:
            self._assert_valid_program(program)
            self._replace_program(program)

        if self._program and self._program.running():
            self._program.kill()
        
        self._num_actions = 0
        self._score = 0

    def copy_program(self):
        return self._program.copy()

    # - - Running Program - -

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
        if status == AgentProgramTree.Status.EXITED and loop:
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
    def program(self) -> AgentProgramTree:
        return self._program
    
    @property
    def score(self) -> Number:
        return self._score
    
    @property
    def num_actions(self) -> int:
        return self._num_actions
    
    # - - Other Methods - -
    
    def __hash__(self):
        return hash(self._uuid)
