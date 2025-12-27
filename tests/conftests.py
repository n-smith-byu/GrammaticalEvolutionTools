from grammaticalevolutiontools.worlds.base import WorldLayout
from grammaticalevolutiontools.worlds.base import WorldObject
from grammaticalevolutiontools.worlds import World
from grammaticalevolutiontools.agents import Agent

from grammaticalevolutiontools.programs.nodes.basic_nodes import ExecutableNode, RootNode
from grammaticalevolutiontools.programs.nodes.logic_nodes import SequentialNode
from grammaticalevolutiontools.grammars import Grammar


import pytest


# - - Agents - - 

class BasicWorldAgent(Agent):
    _requires_world = True
    _default_grammar = None

    def __init__(self):
        super().__init__()


# - - Layouts - - 

class EmptyLayout(WorldLayout):
    def __init__(self, lock=False, initialize=True):
        super(EmptyLayout, self).__init__()

        self._initialized = initialize

        if lock:
            self.lock()

    def initialized(self):
        return self._initialized
    
    def copy(self, lock=True):
        _dup = EmptyLayout()
        if lock:
            _dup.lock()

        return _dup


# - - Worlds - - 

class BasicWorld(World):

    _min_agent_class = BasicWorldAgent
    _layout_class = EmptyLayout

    def __init__(self):
        super(BasicWorld, self).__init__(agent_class=[BasicWorldAgent], obj_types=[], 
                                         world_layout=EmptyLayout(lock=True))
        
    def tick(self):
        for agent in self._agents:
            agent.tick()

    def _load_objects_from_layout(self):
        pass
    
    def load_new_agents(self):
        pass


# - - Nodes - - 

class CodeNode(RootNode):
    def _base_node_init(self):
        super()._base_node_init(token='<Code>', 
                                possible_children = [MidNode])
    def _custom_init(self):
        return super()._custom_init()

class MidNode(SequentialNode):
    def _base_node_init(self):
        super()._base_node_init(token='<Mid>',
                                num_children=2, 
                                possible_children=[ChildNode])  
    def _custom_init(self):
        return super()._custom_init()   

class ChildNode(ExecutableNode):
    PRINT_STR = "test"
    def _base_node_init(self):
        super()._base_node_init(token='<Child>')
    def _custom_init(self):
        return super()._custom_init()
    def execute(self):
        print(ChildNode.PRINT_STR, end='')

