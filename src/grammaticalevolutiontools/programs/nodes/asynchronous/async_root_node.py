from .async_non_terminal_node import AsyncNonTerminalNode
from .async_node import AsyncProgramNode

from typing import Type, List

class AsyncRootNode(AsyncNonTerminalNode):
    def _base_node_init(self, token: str, 
                        possible_children_list: list[Type['AsyncProgramNode']],
                        child_probs: list[float] = None, 
                        label: str = None):
        super()._base_node_init(
            token=token,
            is_root=True,
            num_children=1,
            possible_children = {0: possible_children_list},
            child_probs={0: child_probs},
            label=label
            )
        
        self._children: List[AsyncProgramNode]
        
    def tick(self) -> AsyncProgramNode.Status:
        self._curr_child = (self._curr_child + 1) % self._num_children
        self._status = self._children[self._curr_child].tick()
        
        return self._status