from .. import ProgramNode
from ..basic_nodes import NonTerminalNode
from ..factor_nodes import IntegerNode

class RepeatNode(NonTerminalNode):
    def _base_node_init(
            self, 
            possible_numbers:list[IntegerNode], 
            possible_child_types:list[ProgramNode],
            label: str = 'repeat'):
        
        super()._base_node_init(
            token='<REPEAT>',
            label=label, 
            is_root=False,
            num_children=2, 
            possible_children={0:possible_numbers,
                               1:possible_child_types})

    def _custom_init(self):
        super()._custom_init()
        self._count = 0

    @property
    def num_repeats(self):
        number = self.children[0]
        if number is None:
            raise RuntimeError('This node does not have its number of repeats defined. Please add a NumberNode containing the number of repeats to child index 0.')
        
        return number()
    
    def get_next_child(self):
        num_reps = self.num_repeats()
        if self._count < num_reps:
            self._curr_child = 1
            self._count += 1
            return self.children[1]
        else:
            self._curr_child = -1
            self._count = 0
            return None
        

    def __str__(self):
        _str = f"{self.token}({self.children[1]}, {self.num_repeats})"
        