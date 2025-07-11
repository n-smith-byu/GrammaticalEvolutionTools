from grammaticalevolutiontools.programs.nodes.basic_nodes import ExecutableNode, RootNode
from grammaticalevolutiontools.programs.nodes.logic_nodes import SequentialNode

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

    