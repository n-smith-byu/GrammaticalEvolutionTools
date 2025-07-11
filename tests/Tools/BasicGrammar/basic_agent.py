from grammaticalevolutiontools.agents import Agent
from .basic_grammar import CodeNode

class BasicWorldAgent(Agent):
    @staticmethod
    def import_world():
        if not BasicWorldAgent._world_class:
            from ..BasicWorld import BasicWorld
            BasicWorldAgent._world_class = BasicWorld

    def __init__(self, program=None):
        super(BasicWorldAgent, self).__init__(program)
        BasicWorldAgent.import_world()
    
    @classmethod
    def get_default_program_root_type(cls):
        return CodeNode
    
class BasicWorldlessAgent(Agent):
    def __init__(self, program=None):
        super(BasicWorldlessAgent, self).__init__(program)
    
    @classmethod
    def get_default_program_root_type(cls):
        return CodeNode
