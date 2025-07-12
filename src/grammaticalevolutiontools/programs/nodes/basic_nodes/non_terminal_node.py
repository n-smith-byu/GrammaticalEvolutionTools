from ..program_node import ProgramNode
from abc import abstractmethod
from typing import Type


class NonTerminalNode(ProgramNode):
    """
    Abstract class
    """

    def _base_node_init(self, token: str, 
                        is_root: bool, num_children: int, 
                        possible_children: dict[int, list[Type[ProgramNode]]],
                        child_probs: dict[int, list[float]] = None,
                        label: str = None):
        
        super()._base_node_init(
            token=token,
            is_terminal=False,
            is_root=is_root,
            num_children=num_children,
            possible_children_dict=possible_children,
            special_child_probs=child_probs,
            label=label
        )
        
    def _custom_init(self):
        self._curr_child: int = -1
        return super()._custom_init() 
    
    def _assert_not_running(self):
        # if node is attached to program and the program is running
        if self._program and self._program.running():
            raise self._program.ProgramInProgressError(
                    'Cannot modify program while it is running. '
                    'Please kill program or run it to completion first.'
                )
        # if node not attached to program, but node is not reset
        elif self.is_running():
            raise RuntimeError(
                'Cannot modify children while this node is still running. '
                'Please reset th node first.'
            )

    def reset(self):
        self._curr_child = -1
        for child in self.running_children:
            child.reset()

    def add_child(self, child_node, index = None):
        self._assert_not_running()
        return ProgramNode.add_child(self, child_node, index)
    
    def replace_child(self, index, new_child):
        self._assert_not_running()
        return ProgramNode.replace_child(self, index, new_child)
    
    def pop_child(self, index):
        self._assert_not_running()
        return ProgramNode.pop_child(self, index)
    
    def remove_all_children(self):
        # don't allow modifications to program while running
        if self._program and self._program.running():
            raise self._program.ProgramInProgressError(
                    'Cannot modify program while it is running. '
                    'Please kill program or run it to completion first.'
                )
        
        # if node not attached to program or program not running, 
        # then resets node and removes all children
        self.reset()
        return ProgramNode.remove_all_children(self)
        
    def is_running(self):
        return self._curr_child > -1
    
    # - - - -
    
    @property
    def running_children(self):
        return [child for child in self.children \
                if isinstance(child, NonTerminalNode) and child.is_running()]
    
    @abstractmethod
    def get_next_child(self):
        raise NotImplementedError('get_next_child not implemented.')
    
