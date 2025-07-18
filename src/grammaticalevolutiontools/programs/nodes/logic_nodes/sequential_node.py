from .. import ProgramNode
from ..basic_nodes import NonTerminalNode
from typing import Union, Type

import warnings

class SequentialNode(NonTerminalNode):
    def _base_node_init(
            self, token: str, 
            num_children: int, 
            possible_children: Union[list, dict[int, list[Type[ProgramNode]]]],
            label: str = ''):
        
        # Can either pass in a dict specifying the possible 
        # children at each index 
        if isinstance(possible_children, dict):
            _possible_children = possible_children.copy()

        # Or a list of possible children, to be used for every index.
        elif isinstance(possible_children, list):
            _possible_children = {}
            if num_children == 0:
                if ProgramNode.SHOW_WARNINGS:
                    warnings.warn(
                        message="possible children list received, but "
                                "num_children is 0. possible_children list "
                                "will be ignored. May lead to unexpected "
                                "behavior",
                        category=UserWarning
                    )
            for i in range(num_children):
                _possible_children[i] = possible_children.copy()

        else:
            raise TypeError("possible_children must be a dict or a list. "
                            "Found invalid object of type "
                            f"{type(possible_children).__name__}")

        super()._base_node_init(token=token, is_root=False,
                                num_children=num_children, 
                                possible_children=_possible_children,
                                label=label)

    def get_next_child(self):
        if self._curr_child == self.num_children - 1:
            self._curr_child = -1
        else:
            self._curr_child += 1
        
        return self.children[self._curr_child] if self._curr_child > -1 else None
            
    