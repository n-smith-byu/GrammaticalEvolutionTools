from .tree import ProgramTree
from .addins import BoundToAgentAddin, GrammarProgramAddin


class AgentProgramTree(ProgramTree, BoundToAgentAddin, GrammarProgramAddin):

    @classmethod
    def get_compatible_agent_classes(cls):
        return [cls._GRAMMAR.target_agent_type]

    # - - - - - - - - 

    def __init__(self, root, autofill=True):
        ProgramTree.__init__(self, root, autofill=autofill)
        BoundToAgentAddin.__init__(self)

    def _assert_editable(self):
        ProgramTree._assert_editable(self)
        BoundToAgentAddin._assert_editable(self)

    def _assert_runnable(self):
        ProgramTree._assert_runnable()
        BoundToAgentAddin._assert_runnable()

    def _verify_and_set_root(self, root):
        GrammarProgramAddin._assert_root_valid(root)
        GrammarProgramAddin._set_root(root)

    def _set_agent(self, agent):
        if not isinstance(agent, self.get_grammar().root):
            raise TypeError("Cannot bind tree to an agent with which it is n")
        return super()._set_agent(agent)
        
    def is_editable(self):
        return ProgramTree.is_editable(self) and \
                BoundToAgentAddin.is_editable(self)
    
    def is_runnable(self):
        return ProgramTree.is_runnable() and \
                BoundToAgentAddin.is_runnable()