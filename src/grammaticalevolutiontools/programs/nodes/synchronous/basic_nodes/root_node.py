from .non_terminal_node import NonTerminalNode

from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from ..sync_node import SyncProgramNode

class RootNode(NonTerminalNode):    

    def _base_node_init(self, token: str, 
                        possible_children_list: list[Type['SyncProgramNode']],
                        child_probs: list[float] = None, 
                        label: str = None):
        
        super()._base_node_init(
            token=token, 
            label=label, 
            is_root=True, 
            num_children=1, 
            possible_children_dict={0: possible_children_list},
            child_probs={0: child_probs}
        )

    def _custom_init(self):
        return super()._custom_init()
    
    # - - - -

    def get_next_child(self):
        if self._curr_child < 0:
            self._curr_child = 0
            return self.children[0]
        else:
            self._curr_child = -1
            return None

    
