from .async_node import AsyncProgramNode

from typing import Type

class AsyncNonTerminalNode(AsyncProgramNode):

    def _base_node_init(self, token: str, 
                        is_root: bool, num_children: int, 
                        possible_children_dict: dict[int, list[Type[AsyncProgramNode]]],
                        child_probs: dict[int, list[float]] = None,
                        label: str = None):
        super()._base_node_init(
            token=token, 
            is_terminal=False,
            is_root=is_root,
            num_children=num_children,
            possible_children_dict=possible_children_dict,
            special_child_probs=child_probs,
            label=label
            )
        
    def _custom_init(self):
        self._curr_child: int = -1
        return super()._custom_init()

    def _assert_editable(self):
        AsyncProgramNode._assert_editable(self)

        if self.is_running():
            from ...base import ProgramTree
            raise ProgramTree.ProgramInProgressError(
                'Cannot modify children while this node is still running. '
                'Please reset the node first.'
            )
        
    def reset(self):
        self._curr_child = 0
        self._status = AsyncProgramNode.Status.RESET
        for child in self.children:
            child.reset()
        
    def remove_all_children(self):
        # if node not attached to program or program not running, 
        # then resets node and removes all children
        self._assert_editable()
        self.reset()
        
        return self.remove_all_children()
    
    # - - - -
    
    @property
    def running_children(self):
        return [child for child in self.children if child.is_running()]

