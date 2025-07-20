from ..programs.tree import ProgramTree
from ..grammars.program_mods import GrammarProgramAddin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agents import Agent


class AgentProgramTree(ProgramTree, GrammarProgramAddin):
    
    @classmethod
    def _assert_agent_valid(cls, agent):
        grammar = cls.get_grammar()
        if not isinstance(agent, grammar.target_agent_type):
            raise TypeError(
                "Cannot bind tree to an agent with which " \
                "it is not compatible"
                )
    
    # - - Exceptions - - 

    class MissingAgentError(RuntimeError):
        """Exception raised when attempting to run a program not attached to an an agent."""
        pass

    class BoundToAgentError(RuntimeError):
        """Exception raised for attempted operations requiring the program to be unbound from an agent when it is not."""
        pass

    # - - Local Assertions - - 
        
    def _assert_editable(self):
        if self.bound_to_agent():
            raise AgentProgramTree.BoundToAgentError(
                "Cannot modify a program while it is bound to an agent. "
                "Please remove the program from the agent first or create "
                "a copy to modify. "
            )
        ProgramTree._assert_editable(self)
        
    def _assert_runnable(self):
        if not self.bound_to_agent():
            raise AgentProgramTree.MissingAgentError(
                "Cannot run program when it is not bound to an agent."
            )
        ProgramTree._assert_runnable(self)

    # - - Initialization - - 

    def __init__(self, root=None, autofill=True):
        self._agent = None
        ProgramTree.__init__(self, root, autofill=autofill)
        
    def _verify_and_set_root(self, root):
        GrammarProgramAddin._verify_and_set_root(self, root)

    # - - Agent Access - - 
    
    def _set_agent(self, agent):
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
    
    # - - Public Methods

    def bound_to_agent(self) -> bool:
        """Checks if the program is currently bound to an agent.

        Returns
        -------
        bool
            :py:obj:`True` if an :py:class:`~.agents.Agent` instance is attached to the program
            (:py:attr:`~.ProgramTree._agent` is not :py:obj:`None`), :py:obj:`False` otherwise.
        """
        return self._agent is not None
        
    def is_editable(self):
        return ProgramTree.is_editable(self) and \
                not self.bound_to_agent()
    
    def is_runnable(self):
        return ProgramTree.is_runnable() and \
                self.bound_to_agent()
    
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