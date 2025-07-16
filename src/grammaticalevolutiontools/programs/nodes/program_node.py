from ..._base.base_node import BaseNode

import warnings
import inspect

import numpy as np

from typing import Type, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..tree import ProgramTree


class ProgramNode(BaseNode):

    SHOW_WARNINGS = True
    _program_tree_cls = None

    # - - ClassMethods - - 
    @staticmethod
    def import_program_tree():
        if not ProgramNode._program_tree_cls:
            from ..tree import ProgramTree
            ProgramNode._program_tree_cls = ProgramTree

    # - - Assertions - -

    def _assert_possible_child_type_is_valid(self, node_type: Type):
        if not isinstance(node_type, type) or \
                not issubclass(node_type, ProgramNode):
            raise TypeError(
                f"Possible Children must be of type "
                f"Type[{ProgramNode.__name__}]. "
                f"Obj at fault: {node_type}"
            )

        node_type: Type[ProgramNode]
        if node_type().is_root:
            raise ValueError("Nodes cannot reference root nodes as possible "
                             "children. Possible child class at fault: "
                             f"{node_type.__name__}")

    def _assert_vals_valid(self):

        ProgramNode._assert_token_valid(self._token)
        ProgramNode._assert_label_valid(self._label)
        ProgramNode._assert_tags_valid(self._is_terminal, self._is_root)
        ProgramNode._assert_max_num_children_valid(
            self._max_num_children, self._is_terminal)
        ProgramNode._assert_possible_children_dict_valid(
            self.__possible_children_dict, 
            self._max_num_children,
            warnings_ = ProgramNode.SHOW_WARNINGS
        )
        ProgramNode._assert_child_probs_dict_valid(
            self.__special_child_probs, 
            self.__possible_children_dict,
            warnings_ = ProgramNode.SHOW_WARNINGS
        )
        
    @classmethod
    def _init_has_extra_args(cls) -> bool:        
        # Check if __init__ takes args besides self
        base_node_init = cls._base_node_init
        sig1 = inspect.signature(base_node_init)
        params1 = list(sig1.parameters.values())

        custom_init = cls._custom_init
        sig2 = inspect.signature(custom_init)
        params2 = list(sig2.parameters.values())
        
        return len(params1) > 1 or len(params2) > 1
        
    # - - BaseNode Init - - 

    def _init_possible_children(self, possible_children_dict: dict,
                                special_child_probs_dict: dict):

        for ind, psbl_chld_list in possible_children_dict.items():
            if ind in special_child_probs_dict:
                self._set_possible_children(
                    ind, psbl_chld_list, special_child_probs_dict[ind])
            else:
                self._set_possible_children(ind, psbl_chld_list)

    def _set_possible_children(self, index: int, 
                               possible_children_list: list[
                                   Type['ProgramNode']
                                   ],
                               special_probs: np.ndarray = None):

        for node_cls in possible_children_list:
            self._assert_possible_child_type_is_valid(node_cls)

        self.__possible_children_dict[index] = possible_children_list.copy()
        self.__all_possible_children.update(
            self.__possible_children_dict[index])

        if special_probs is not None:
            self._set_child_probs(index, special_probs)

    def _set_child_probs(self, index: int, probs: list[float]):
        if (index not in self.__possible_children_dict) or \
                (self.__possible_children_dict[index] is None):
            
            raise ValueError("Cannot set probs for possible children "
                             "where possible children not specified. "
                             "No possible children defined yet "
                             f"for index {index}.")

        if len(probs) != len(self.__possible_children_dict[index]):
            raise ValueError(
                "Size mismatch. Length of probs must match length of "
                "possible children at specified index."
            )

        self.__special_child_probs[index] = np.array(probs)

    # - - Initialization - -

    def __init__(self):
        self._base_node_init()
        self._custom_init()

    def _base_node_init(self, token: str, is_terminal: bool, 
                        is_root: bool, num_children: int, 
                        label: Optional[str] = None,
                        possible_children_dict: Optional[
                            dict[int, list[Type['ProgramNode']]]
                            ] = None,
                        special_child_probs: Optional[
                            dict[int, list[float]]
                            ] = None
                        ):

        if possible_children_dict is None:
            possible_children_dict = {}
            if special_child_probs is not None:
                warnings.warn(message="Received special_child_probs when "
                                      "possible_children was None. "
                                      "special_child_probs will be ignored.")
        if special_child_probs is None:
            special_child_probs = {}

        self._token: str = token
        self._label: str = label
        self._is_terminal: bool = is_terminal
        self._is_root: bool = is_root
        self._max_num_children: int = num_children

        self.__possible_children_dict: dict[int, list[Type[ProgramNode]]] = {}
        # enables custom probabilities for each child node being chosen
        self.__special_child_probs: dict[int, np.ndarray] = {}

        self.__all_possible_children: set[ProgramNode] = set()

        self._init_possible_children(
            possible_children_dict, 
            special_child_probs)

        self._assert_vals_valid()

        super(ProgramNode, self).__init__()

    def _custom_init(self):
        self._program: 'ProgramTree' = None
        self._parent: ProgramNode

    def _set_program(self, program: 'ProgramTree'):
        if program and self._program:
            raise ValueError("Cannot set program while already part of another program.")
        
        old_program = self._program
        self._program = program
    
        if self._program:
            self._program._mark_nodes_dirty()
        if old_program:
            old_program._mark_nodes_dirty()

        for child in self._children:
            if isinstance(child, ProgramNode):
                child._set_program(program)

    def _clear_program(self):
        self._set_program(None)

    def _on_collect_descendants(self):
        if self._program:
            if self._depth > self._program._max_child_depth:
                self._program._max_child_depth = self._depth
        
            self._program._nodes_by_type[type(self)].add(self)


    # - - Public Methods - -

    def add_child(self, new_child: 'ProgramNode', index = None):
        if new_child._program:
            raise ValueError("new_child must not be part of another program.")
        index = BaseNode.add_child(self, new_child, index)

        try:
            new_child._set_program(self._program)
        except ValueError as e:
            self._children[index] = None
            self.num_children -= 1
            raise e
        
    def pop_child(self, index) -> 'ProgramNode':
        child: ProgramNode = BaseNode.pop_child(self, index)
        if isinstance(child, BaseNode):
            child._clear_program()
        
        return child

    # - - Properties - -

    @property
    def _possible_children_dict(self) -> dict[int, list[Type['ProgramNode']]]:
        return self.__possible_children_dict

    @property
    def _special_probs_dict(self) -> dict[int, np.ndarray]:
        return self.__special_child_probs
    
    @property
    def _all_possible_children(self):
        return self.__all_possible_children

    @property
    def max_num_children(self) -> int:
        return self._max_num_children

    @property
    def label(self) -> Optional[str]:
        return self._label

    @property
    def token(self) -> str:
        return self._token

    @property
    def is_terminal(self) -> bool:
        return self._is_terminal

    @property
    def is_root(self) -> bool:
        return self._is_root
