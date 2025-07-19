from abc import ABC, abstractmethod

from typing import Type, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...agents import Agent


class BoundToAgentAddin(ABC):

    # - - Abstract Class Methods - - 
    
    @classmethod
    @abstractmethod
    def get_compatible_agent_classes(cls) -> List[Type['Agent']]:
        pass

    # - - Exceptions - - 

    class MissingAgentError(RuntimeError):
        """Exception raised when attempting to run a program not attached to an an agent."""
        pass

    class BoundToAgentError(RuntimeError):
        """Exception raised for attempted operations requiring the program to be unbound from an agent when it is not."""
        pass

    # - - Assertions - - 

    @classmethod
    def _assert_agent_valid(cls, agent):
        compatible_types = cls.get_compatible_agent_classes()
        if not isinstance(agent, tuple(compatible_types)):
            raise TypeError(
                "Agent is of a type this program was " \
                "not designed for"
                )
        
    def _assert_editable(self):
        if self.bound_to_agent():
            raise BoundToAgentAddin.BoundToAgentError(
                "Cannot modify a program while it is bound to an agent. "
                "Please remove the program from the agent first or create "
                "a copy to modify. "
            )
        
    def _assert_runnable(self):
        if not self.bound_to_agent():
            raise BoundToAgentAddin.MissingAgentError(
                "Cannot run program when it is not bound to an agent."
            )
        
    # - - Initialization - - 
        
    def __init__(self):
        self._agent = None

    def _set_agent(self, agent: 'Agent'):
        """Sets the agent instance to which this program is bound.

        This method should typically only be called by an instance of
        :py:class:`~.agents.Agent` itself to establish the binding.

        Parameters
        ----------
        agent : Agent
            The agent instance to bind the program to.
        """
        self._assert_agent_valid(agent)
        self._agent = agent

    # - - Public Methods - - 

    def bound_to_agent(self) -> bool:
        """Checks if the program is currently bound to an agent.

        Returns
        -------
        bool
            :py:obj:`True` if an :py:class:`~.agents.Agent` instance is attached to the program
            (:py:attr:`~.ProgramTree._agent` is not :py:obj:`None`), :py:obj:`False` otherwise.
        """
        return self.agent is not None
    
    def is_editable(self):
        return not self.bound_to_agent()
    
    def is_runnable(self):
        return self.bound_to_agent()

    
    @property
    def agent(self) -> 'Agent':
        """The agent instance to which this program is currently attached.

        Returns
        -------
        Agent or None
            The attached :py:class:`~.agents.Agent` instance, or :py:obj:`None`
            if no agent is currently bound.
        """
        return self._agent
