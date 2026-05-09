from .async_node import AsyncProgramNode

class AsyncNonTerminalNode(AsyncProgramNode):

    def _base_node_init(self, token, is_root, 
                        num_children,
                        possible_children_dict,
                        special_child_probs):
        super()._base_node_init(
            token=token, 
            is_terminal=False,
            is_root=is_root,
            num_children=num_children,
            possible_children_dict=possible_children_dict,
            special_child_probs=special_child_probs
            )
        
    def _custom_init(self):
        super()._custom_init()

    def _assert_editable(self):
        AsyncProgramNode._assert_editable(self)

        if self.is_running():
            from ...base import ProgramTree
            raise ProgramTree.ProgramInProgressError(
                'Cannot modify children while this node is still running. '
                'Please reset the node first.'
            )
        
    def reset(self):
        self._curr_child = -1
        self._status = AsyncProgramNode.Status.RESET
        for child in self.children:
            child.reset()
        
    def remove_all_children(self):
        # if node not attached to program or program not running, 
        # then resets node and removes all children
        self._assert_editable()
        self.reset()
        
        return self.remove_all_children()
        
    def is_running(self):
        return self._status == AsyncProgramNode.Status.RUNNING
    
    # - - - -
    
    @property
    def running_children(self):
        return [child for child in self.children if child.is_running()]

