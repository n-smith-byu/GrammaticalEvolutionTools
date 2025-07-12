from .meta import BaseNodeMeta

from abc import abstractmethod
import warnings
import random
import uuid

import numpy as np

from typing import Type, Tuple, Optional, Union


class BaseNode(metaclass=BaseNodeMeta):

    # - - Common Assertions - -

    @staticmethod
    def _assert_token_valid(token):
        if not isinstance(token, str):
            raise TypeError(
                "token must be of type str. "
                + f"Found value of type {type(token).__name__}"
            )

        if token == "":
            raise ValueError("token cannot be the empty string.")

    @staticmethod
    def _assert_max_num_children_valid(max_num_children, is_terminal=False):
        if not isinstance(max_num_children, int):
            raise TypeError(f"val must be an integer.")

        if max_num_children < 0:
            raise ValueError(f"max_num_children must be >= 0.")

        if is_terminal and max_num_children != 0:
            raise ValueError(
                "max_num_children must be 0 if is_terminal is True."
            )

    @staticmethod
    def _assert_label_valid(label):
        if label is not None and not isinstance(label, str):
            raise TypeError(
                "label must be of type str or None. "
                f"Found label of type {type(label).__name__}"
            )

    @staticmethod
    def _assert_tags_valid(is_terminal, is_root):
        at_fault = None
        if not isinstance(is_terminal, bool):
            at_fault = "is_terminal"
        if not isinstance(is_root, bool):
            at_fault = "is_root"

        if at_fault:
            raise TypeError(
                f"{at_fault} must be of type bool. Found object "
                f"of type {type(is_terminal).__name__}"
            )

        if is_root and is_terminal:
            raise ValueError(
                "A root node must be a non-terminal node. "
                "Found is_root set to True and "
                "is_terminal set to True"
            )

    @staticmethod
    def _assert_child_probs_dict_valid(
        child_probs_dict,
        possible_children_dict: dict[int, list[Type['BaseNode']]],
        warnings_=True,
    ):

        if not isinstance(child_probs_dict, dict):
            raise TypeError(
                "special_child_probs_dict, if defined, must  "
                "be a dictionary. Instead found instance of type "
                f"{type(child_probs_dict).__name__}"
            )

        unused_inds = []
        for ind in child_probs_dict:
            if ind not in possible_children_dict:
                unused_inds.append(ind)
                continue

            try:
                BaseNode._assert_child_probs_valid(
                    child_probs_dict[ind], possible_children_dict[ind]
                )
            except ValueError as e:
                raise ValueError(
                    f"Error at index {ind} in "
                    "special_child_probs_dict. "
                    f"Error: {e}"
                ) from e

        if warnings_:
            if len(unused_inds) > 0:
                warnings.warn(
                    message=f"Unused inds found in special_child_probs_dict. "
                             "These values are ignored.\n"
                            f"Unused inds: {unused_inds}",
                    category=UserWarning,
                )

    @staticmethod
    def _assert_child_probs_valid(child_probs: np.ndarray,
                                  possible_children: list):

        try:
            _probs = BaseNode.probs_to_numpy(child_probs)
            if _probs.ndim != 1:
                raise ValueError(
                    f"child_probs must be an 1d array. "
                    f"Found an array with {_probs.ndim} dimensions."
                )

        except ValueError as e:
            raise ValueError(
                f"Error in child_probs. Could not convert to a 1-D numpy array"
                 " of type float64.\n"
            ) from e

        if _probs.shape[0] != len(possible_children):
            raise ValueError(
                f"Size mismatch at between possible_children and child_probs. "
                f"possible_children found of length {len(possible_children)}. "
                f"child_probs found of length {_probs.shape[0]}."
            )

    @staticmethod
    def _assert_possible_children_dict_valid(
        possible_children_dict, max_num_children: int, warnings_=True
    ):

        if not isinstance(possible_children_dict, dict):
            raise TypeError(
                 "special_child_probs_dict, if defined, must be a dictionary. "
                f"Found object of type {type(possible_children_dict).__name__}"
            )

        possible_inds = [i for i in range(max_num_children)]
        for ind in possible_inds:
            if ind not in possible_children_dict:
                raise KeyError(
                    f"possible_children_dict must contain keys for every "
                    f"integer from 0 to {max_num_children - 1}."
                )

            value = possible_children_dict[ind]
            if not isinstance(value, list):
                raise TypeError(
                    f"possible_childen_dict[{ind}] must be a list. "
                    f"Found object of type {type(value).__name__}"
                )

        if warnings_:
            unused_inds = []
            for ind in possible_children_dict:
                if ind not in possible_inds:
                    unused_inds.append(ind)
            if len(unused_inds) > 0:
                warnings.warn(
                    message=f"Extra inds found in possible_children_dict. "
                             "These values are ignored.\n"
                            f"Unused inds: {unused_inds}",
                    category=UserWarning,
                )

    # - - Static Utilities - -

    @staticmethod
    def probs_to_numpy(probs) -> np.ndarray:
        return np.atleast_1d(np.array(probs, dtype=np.float64))

    @staticmethod
    def convert_probs_dict_to_numpy(
        special_child_probs_dict: dict[int, list[float]],
    ) -> dict[int, np.ndarray]:
        _dup = special_child_probs_dict.copy()

        for i in special_child_probs_dict:
            probs_as_numpy = BaseNode.probs_to_numpy(
                special_child_probs_dict[i]
            )
            _dup[i] = probs_as_numpy

        return _dup

    # ----------------------------------


    # - - User Methods - -

    def __init__(self):
        self._num_children = 0
        self._children: list[BaseNode] = [
            None for _ in range(self.max_num_children)
        ]
        self._identifier = uuid.uuid4()
        self._parent: BaseNode = None
        self._depth: int = 0

    def get_next_available_slot(self, node_type: Type['BaseNode']):
        possible_inds = [
            ind
            for ind in range(self.max_num_children)
            if node_type in self.get_possible_children(ind)
        ]
        if len(possible_inds) == 0:
            raise TypeError(
                f"{node_type.__name__} is not in the possible_children list "
                "for any child index."
            )

        for ind in possible_inds:
            if self._children[ind] is None:
                return ind

        return None

    def add_child(self, new_child: 'BaseNode', index: int = None) -> int:
        if new_child in self._children:
            raise ValueError(
                "new_child already in list of children. "
                "Cannot occupy two slots at once. "
                "Please make a copy instead."
            )

        if index is None:
            index = self.get_next_available_slot(type(new_child))
        if index is None:  # if still None (i.e. no valid index found)
            raise IndexError(
                "No available indeces available for nodes of type "
                f"{type(new_child).__name__}"
            )
        elif self._children[index] is not None:
            raise IndexError(
                f"Another child already exists at index {index}. "
                + "Try using replace_child() instead to overwrite."
            )
        elif type(new_child) not in self._possible_children_dict[index]:
            permitted_types = self._possible_children_dict[index]
            raise TypeError(
                 "new_child does not match possible child types for a node "
                f"of type {type(self)}.\n"
                f"Permitted types include {permitted_types}"
            )

        old_parent = new_child._parent
        new_child._parent = self

        self._children[index] = new_child
        self._num_children += 1
        
        if not new_child._set_depth(self._depth + 1):
            self._children[index] = None
            new_child._parent = old_parent
            self._num_children -= 1
            raise ValueError(
                "Node could not be added because it will cause a cycle to form."
                )

        return index

    def replace_child(self, index: int, 
                      new_child: 'BaseNode') -> 'BaseNode':
        old_child = self.pop_child(index)
        try:
            self.add_child(new_child, index=index)
        except TypeError as e:
            self.add_child(old_child, index=index)
            raise e

        return old_child

    def get_index_of_child(self, child_node: 'BaseNode') -> int:
        for index, child in enumerate(self._children):
            if child is child_node:
                return index

        return -1

    def pop_child(self, index: int) -> 'BaseNode':
        child = self._children[index]
        self._children[index] = None
        self._num_children -= 1
        child._parent = None

        child._set_depth(0)
        
        return child

    def remove_all_children(self):
        for i in range(len(self._children)):
            child = self._children[i]
            if child is not None:
                self.pop_child(i)

        self._num_children = 0

    def collect_descendants(self, include_self=True) -> set['BaseNode']:
        node_set = set()

        if include_self:
            self._collect_descendants(node_set)
        else:
            for child in self._children:
                if child is not None:
                    child._collect_descendants(node_set)

        return node_set


    # - - Helper Methods - -

    def _collect_descendants(self, node_set: set['BaseNode']):
        if self in node_set:
            raise ValueError(
                f"Error in recursively collecting descendants. "
                 "Repeat node detected."
            )

        node_set.add(self)

        for child in self._children:
            if child is not None:
                child._collect_descendants(node_set)

    def _copy_children_from(self, other: 'BaseNode'):
        if type(other) != type(self):
            raise TypeError(
                "Cannot copy children from a node of a different type."
            )

        # copy children over
        self.remove_all_children()

        for index, child in enumerate(other.children):
            if child is not None:
                type(self).add_child(self, child.copy(), index=index)
            else:
                self._children[index] = None
    
    def _set_depth(self, depth, visited: set['BaseNode'] = None) -> bool:
        
        if visited is None:
            visited = set()
        if self in visited:
            return False
        
        old_depth = self._depth
        self._depth = depth
        self._on_set_depth()
        visited.add(self)
        for child in self._children:
            if child is not None:
                if not child._set_depth(self._depth + 1, visited):
                    self._depth = old_depth
                    self._on_set_depth_rollback()
                    return False
        
        return True
                
    def _on_set_depth(self):
        pass   # hook for subclasses to set additional properties

    def _on_set_depth_rollback(self):
        pass   # specifies how to undo changes in _on_set_depth
    

    # - - Getters - -

    def get_possible_children_and_probs(self, index) -> Tuple[tuple[Type['BaseNode']], np.ndarray]:
        _possible_children = self.get_possible_children(index).copy()
        _probs = self.get_probs(index)

        return _possible_children, _probs

    def get_probs(self, index: int):
        special_probs = self._special_probs_dict
        if index not in special_probs or special_probs[index] is None:
            size = len(self.get_possible_children(index))
            return np.ones(size) / size
        else:
            return special_probs[index].copy()
    
    def get_possible_children(self, index: int) -> list[Type['BaseNode']]:
        return self._possible_children_dict[index].copy()

    def get_all_possible_children(self) -> set[Type['BaseNode']]:
        return self._all_possible_children.copy()
    
    def get_parent(self) -> Tuple['BaseNode', int]:
        if self._parent is None:
            return None, None
      
        return self._parent, self._parent.get_index_of_child(self)


    # - - Properties - -

    @property
    def special_probs_dict(self) -> dict[int, np.ndarray]:
        _dup = {}
        for ind, probs_list in self._special_probs_dict.items():
            _dup[ind] = probs_list.copy()

        return _dup

    @property
    def possible_children_dict(self) -> dict[int, list[Type['BaseNode']]]:
        _dup = {}
        for ind, chld_list in self._possible_children_dict.items():
            _dup[ind] = chld_list.copy()

        return _dup
    
    @property
    def num_children(self) -> int:
        return self._num_children

    @property
    def child_depth(self) -> int:
        return self._depth + 1

    @property
    def children(self) -> list['BaseNode']:
        return [child for child in self._children]
    

    # - - Abstract Properties - -

    @property
    @abstractmethod
    def _possible_children_dict(self) -> dict[int, list[Type['BaseNode']]]:
        return NotImplemented

    @property
    @abstractmethod
    def _special_probs_dict(self) -> dict[int, np.ndarray]:
        return NotImplemented
    
    @property
    @abstractmethod
    def _all_possible_children(self) -> set[Type['BaseNode']]:
        return NotImplemented

    @property
    @abstractmethod
    def max_num_children(self) -> int:
        return NotImplemented

    @property
    @abstractmethod
    def label(self) -> Optional[str]:
        return NotImplemented

    @property
    @abstractmethod
    def token(self) -> str:
        return NotImplemented

    @property
    @abstractmethod
    def is_terminal(self) -> bool:
        return NotImplemented

    @property
    @abstractmethod
    def is_root(self) -> bool:
        return NotImplemented


    # - - Utilities - -

    def _children_as_string(self):
        children = self.children
        _str = ""
        for i in range(len(children)):
            child = children[i]
            if child is None:
                chld_str = ""
            else:
                chld_str = str(child)
            _str += chld_str + (", " if i < len(children) - 1 else "")

        return _str
    
    def _default_copy_method(self, *args, **kwargs):
        _dup = type(self)(*args, **kwargs)
        _dup._copy_children_from(self)

        return _dup

    # - - Special Methods - -

    def copy(self) -> 'BaseNode':
        return self._default_copy_method()

    def __str__(self):
        if self.num_children == 0:
            return str(self.token)
        else:
            _str = self._children_as_string()
            if self.label is not None:
                _str = f"{self.label}({_str})"

        return _str

    def __hash__(self):
        return hash(self._identifier)
