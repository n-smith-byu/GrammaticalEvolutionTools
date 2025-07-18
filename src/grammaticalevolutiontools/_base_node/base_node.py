from .meta import BaseNodeMeta

from abc import abstractmethod
import warnings
import random
import uuid

import numpy as np

from typing import Type, Tuple, Optional, Any, Literal

class BaseNode(metaclass=BaseNodeMeta):
    """Abstract base class for all nodes.

    This class defines the fundamental structure and common behaviors
    for all nodes, whether they are terminal (no children) or non-terminal
    (can have children). It manages parent-child relationships, node
    identification, and provides utilities for tree traversal and manipulation.

    Notes
    -----
    **Instantiation Constraints and `_init_has_extra_args`:**

    Concrete (instantiable) subclasses of `BaseNode` are strictly required
    to have an `__init__` method that takes no arguments other than `self`.
    This critical constraint is enforced by the :py:class:`~.BaseNodeMeta`.
    The metaclass uses the :py:meth:`~.BaseNode._init_has_extra_args` **class method**
    (defined on this class) to determine if a given class's `__init__` requires
    additional parameters.

    Internal attributes (prefixed with `_`) are managed by the class and
    typically not intended for direct external access.

    See Also
    --------
    :py:class:`~.meta.BaseNodeMeta`
    :py:meth:`~.meta.BaseNodeMeta._init_has_extra_args`

    Attributes
    ----------
    _num_children : int
        The current number of children attached to this node.
    _children : list of BaseNode or None
        A list representing the child slots of this node. Each element
        is either a :py:class:`~.BaseNode` instance or :py:obj:`None` if the slot is empty.
        The length of this list is determined by :py:attr:`~.BaseNode.max_num_children`.
    _identifier : uuid.UUID
        A unique identifier for this specific node instance.
        This is used for hashing and distinguishing between node instances.
    _parent : BaseNode or None
        A reference to the parent :py:class:`~.BaseNode` of this node, or
        :py:obj:`None` if this node is the root or is detached from a tree.
    _depth : int
        The depth of this node within the tree, where the root node has a depth of 0.
        This value is maintained when the node is added to a tree or its depth changes.

    """

    # - - Assertion Utilities - -

    @staticmethod
    def _assert_token_valid(token):
        """Asserts that a given token is a valid string.

        Parameters
        ----------
        token : str
            The token to validate.

        Raises
        ------
        TypeError
            If `token` is not of type :py:class:`str`.
        ValueError
            If `token` is an empty string.
        """
        if not isinstance(token, str):
            raise TypeError(
                "`token` must be of type str. Found value of type "
               f"{type(token).__name__}"
            )

        if token == '':
            raise ValueError("`token` cannot be the empty string.")

    @staticmethod
    def _assert_max_num_children_valid(max_num_children, is_terminal=False):
        """Asserts that `max_num_children` is a valid integer.

        Parameters
        ----------
        max_num_children : int
            The maximum number of children to validate.
        is_terminal : bool, optional
            A flag indicating if the node is considered terminal.
            If :py:obj:`True`, `max_num_children` must be 0 (default is :py:obj:`False`).

        Raises
        ------
        TypeError
            If `max_num_children` is not an integer.
        ValueError
            If `max_num_children` is negative.
            If `is_terminal` is :py:obj:`True` and `max_num_children` is not 0.
        """
        if not isinstance(max_num_children, int):
            raise TypeError(
                "`max_num_children` must be an integer. Found object of type"
               f"{type(max_num_children).__name__}")

        if max_num_children < 0:
            raise ValueError(f"`max_num_children` must be >= 0.")

        if is_terminal and max_num_children != 0:
            raise ValueError(
                "`max_num_children` must be 0 if `is_terminal` is True."
            )

    @staticmethod
    def _assert_label_valid(label):
        """Asserts that a given label is a valid string or None.

        Parameters
        ----------
        label : str or None
            The label to validate.

        Raises
        ------
        TypeError
            If `label` is not of type :py:class:`str` and not :py:obj:`None`.
        """
        if label is not None and not isinstance(label, str):
            raise TypeError(
                "`label` must be of type str or None. Found object of type "
               f"{type(label).__name__}"
            )

    @staticmethod
    def _assert_tags_valid(is_terminal, is_root):
        """Asserts that the `is_terminal` and `is_root` tags are valid boolean values.

        Also enforces the constraint that a root node cannot be a terminal node.

        Parameters
        ----------
        is_terminal : bool
            The value for the `is_terminal` tag.
        is_root : bool
            The value for the `is_root` tag.

        Raises
        ------
        TypeError
            If `is_terminal` or `is_root` is not a boolean.
        ValueError
            If both `is_root` and `is_terminal` are :py:obj:`True` (a root node cannot be terminal).
        """
        at_fault = None
        if not isinstance(is_terminal, bool):
            at_fault = "is_terminal"
        if not isinstance(is_root, bool):
            at_fault = "is_root"

        if at_fault:
            raise TypeError(
                f"{at_fault} must be of type `bool`. Found object "
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
        possible_children_dict,
        warnings_=True,
        ):
        """Asserts that a dictionary of child probabilities is valid.

        This method checks the type of `child_probs_dict` and then
        iterates through its entries to ensure that each probability
        array/list is valid for its corresponding child index. It also
        warns about unused indices in `child_probs_dict`.

        Parameters
        ----------
        child_probs_dict : dict[int, list[float] or np.ndarray]
            A dictionary where keys are child indices and values are
            lists or NumPy arrays of probabilities for child types.
        possible_children_dict : dict[int, list[Type[BaseNode]]]
            A dictionary where keys are child indices and values are
            lists of possible child node types for that index. This
            is used to validate the dimensions of probability arrays.
        warnings_ : bool, optional
            If :py:obj:`True`, a warning will be issued for unused indices
            in `child_probs_dict` (default is :py:obj:`True`).

        Raises
        ------
        TypeError
            If `child_probs_dict` is not a dictionary.
        ValueError
            If any probability list/array within `child_probs_dict` is invalid,
            propagated from :py:meth:`~.BaseNode._assert_child_probs_valid`.

        Warns
        -----
        UserWarning
            If `warnings_` is :py:obj:`True` and `child_probs_dict` contains
            keys that do not correspond to valid child indices in
            `possible_children_dict`.
        """
        if not isinstance(child_probs_dict, dict):
            raise TypeError(
                "`child_probs_dict`, if defined, must be a dictionary. "
                "Instead found object of type "
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
                    f"Error at index {ind} in `special_child_probs_dict`. "
                    ) from e

        if warnings_:
            if len(unused_inds) > 0:
                warnings.warn(
                    message=f"Unused inds found in `special_child_probs_dict`. "
                             "These values are ignored.\n"
                            f"Unused inds: {unused_inds}",
                    category=UserWarning,
                )

    @staticmethod
    def _assert_child_probs_valid(child_probs,
                                  possible_children):
        """Asserts that a given array or list of child probabilities is valid.

        This checks that `child_probs` can be converted to a 1D NumPy array
        of float64 and that its length matches the number of `possible_children`.

        Parameters
        ----------
        child_probs : list[float] or numpy.ndarray
            The probabilities for each possible child type.
        possible_children : list[Type[BaseNode]]
            A list of the possible child node types. Used to check size mismatch.

        Raises
        ------
        ValueError
            If `child_probs` cannot be converted to a 1D float64 NumPy array.
            If the length of `child_probs` does not match the length of `possible_children`.
        """
        try:
            _probs = BaseNode.probs_to_numpy(child_probs)
        except ValueError as e:
            raise ValueError(
                f"Error in `child_probs`. Could not convert to a 1-D numpy array"
                 " of type float64.\n"
            ) from e
        
        if _probs.ndim != 1:
            raise ValueError(
                f"`child_probs` must be an 1d array. "
                f"Found an array with {_probs.ndim} dimensions."
            )

        if _probs.shape[0] != len(possible_children):
            raise ValueError(
                f"Size mismatch between `possible_children` and `child_probs`. "
                f"`possible_children` has length {len(possible_children)}, "
                f"but `child_probs` has length {_probs.shape[0]}."
            )

    @staticmethod
    def _assert_possible_children_dict_valid(
            possible_children_dict, 
            max_num_children: int, 
            warnings_=True
        ):
        """Asserts that a dictionary of possible children is valid.

        This method verifies that `possible_children_dict` is a dictionary,
        contains keys for all required child indices (from 0 to `max_num_children` - 1),
        and that each value is a list of node types. It also warns about
        extra, unused keys in the dictionary.

        Parameters
        ----------
        possible_children_dict : dict[int, list[Type[BaseNode]]]
            A dictionary where keys are child indices and values are
            lists of possible child node types for that index.
        max_num_children : int
            The maximum number of children allowed for the node, used to
            determine the expected range of indices.
        warnings_ : bool, optional
            If :py:obj:`True`, a warning will be issued for extra, unused indices
            in `possible_children_dict` (default is :py:obj:`True`).

        Raises
        ------
        TypeError
            If `possible_children_dict` is not a dictionary.
            If any value in `possible_children_dict` is not a list.
        KeyError
            If `possible_children_dict` does not contain a key for every
            integer from 0 to `max_num_children` - 1.

        Warns
        -----
        UserWarning
            If `warnings_` is :py:obj:`True` and `possible_children_dict` contains
            keys that are outside the range of expected child indices.

        """
        if not isinstance(possible_children_dict, dict):
            raise TypeError(
                 "special_child_probs_dict, if defined, must be a dictionary. "
                f"Found object of type {type(possible_children_dict).__name__}"
            )

        possible_inds = [i for i in range(max_num_children)]
        for ind in possible_inds:
            if ind not in possible_children_dict:
                raise KeyError(
                    f"`possible_children_dict` must contain a key for every "
                    f"integer from 0 to {max_num_children - 1}."
                )

            value = possible_children_dict[ind]
            if not isinstance(value, list):
                raise TypeError(
                    f"`possible_childen_dict[{ind}]` must be a list. "
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

    # - - Other Utilities - -

    @staticmethod
    def probs_to_numpy(probs) -> np.ndarray:
        """Converts a list or array of probabilities to a 1D NumPy array of float64.

        Parameters
        ----------
        probs : list[float] or numpy.ndarray
            The probabilities to convert. Can be a list of floats or a NumPy array.

        Returns
        -------
        numpy.ndarray
            A 1-dimensional NumPy array of probabilities with dtype float64.
        """
        return np.atleast_1d(np.array(probs, dtype=np.float64))

    @staticmethod
    def convert_probs_dict_to_numpy(
            special_child_probs_dict: dict[int, list[float]],
        ) -> dict[int, np.ndarray]:
        """Converts probability lists within a dictionary to NumPy arrays.

        This utility method takes a dictionary where values are lists of floats
        (representing probabilities) and converts those lists into 1D NumPy arrays,
        returning a new dictionary with the converted values.

        Parameters
        ----------
        special_child_probs_dict : dict[int, list[float]]
            A dictionary where keys are child indices and values are
            lists of probabilities.

        Returns
        -------
        dict[int, numpy.ndarray]
            A new dictionary with the same keys, but with probability lists
            converted to 1D NumPy arrays of float64.
        """
        _dup = special_child_probs_dict.copy()

        for i in special_child_probs_dict:
            probs_as_numpy = BaseNode.probs_to_numpy(
                special_child_probs_dict[i]
            )
            _dup[i] = probs_as_numpy

        return _dup
    
    # ----------------------------------------

    # - - Exceptions - - 

    class CycleDetectedError(RuntimeError):
        """"""
        pass

    # - - Literals - - 

    CollectionReason = Literal["collect", "add", "pop"]

    # - - User Methods - -

    def __init__(self):
        """Initializes a new instance of BaseNode.

        This constructor sets up the basic attributes for a node,
        including its children slots, unique identifier, and parent reference.
        It must be called by subclasses.
        """
        self._num_children = 0
        self._children: list[BaseNode] = [
            None for _ in range(self.max_num_children)
        ]
        self._identifier = uuid.uuid4()
        self._parent: BaseNode = None
        self._depth: int = 0
        self._attr_cache: dict[str, Any] = {}

    def get_next_available_slot(self, node_type: Type['BaseNode']):
        """Finds the next available (empty) child slot that can accept a given node type.

        This method searches for the lowest index in `_children` that is currently
        :py:obj:`None` and for which `node_type` is an allowed child type.

        Parameters
        ----------
        node_type : Type[BaseNode]
            The class (type) of the node to be placed in a slot.

        Returns
        -------
        int or None
            The index of the first available slot, or :py:obj:`None` if no such slot is found.

        Raises
        ------
        TypeError
            If `node_type` is not among the possible children for any child index of this node.
        """
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
    
    def get_index_of_child(self, child_node: 'BaseNode') -> int:
        """Returns the index of a given child node within this node's children list.

        Parameters
        ----------
        child_node : BaseNode
            The child node to find the index of.

        Returns
        -------
        int
            The integer index of `child_node` if found, otherwise -1.
        """
        for index, child in enumerate(self._children):
            if child is child_node:
                return index

        return -1

    def add_child(self, new_child: 'BaseNode', 
                  index: int = None) -> int:
        """Adds a new child node to this node at a specified or next available index.

        If `index` is :py:obj:`None`, the method attempts to find the
        :py:meth:`~.BaseNode.get_next_available_slot`.
        If successful, the new child is linked, its depth is set, and the
        `_num_children` count is incremented.

        Parameters
        ----------
        new_child : BaseNode
            The node to add as a child.
        index : int, optional
            The specific index at which to add the child. If :py:obj:`None`,
            the next available suitable slot will be used.

        Returns
        -------
        int
            The index at which the child was added.

        Raises
        ------
        ValueError
            If `new_child` is already a child of this node.
            If adding `new_child` would create a cycle in the tree.
        IndexError
            If `index` is specified but is already occupied.
            If no available slot can be found for `new_child` when `index` is :py:obj:`None`.
        TypeError
            If `new_child` is not of a type permitted for the specified `index`.
        """
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

        self._children[index] = new_child
        self._num_children += 1

        properties = self._get_properties_to_pass_to_children()
        new_child._set_properties(properties)

        try:
            new_child.collect_descendants(reason='add')
        except RuntimeError as e:
            self._children[index] = None
            self._num_children -= 1

            raise ValueError('New child caused a cycle.') from e

        return index

    def pop_child(self, index: int) -> 'BaseNode':
        """Removes and returns the child node at the specified index.

        The removed child's parent reference is set to :py:obj:`None`,
        its depth is reset to 0, and the `_num_children` count is decremented.

        Parameters
        ----------
        index : int
            The index of the child to remove.

        Returns
        -------
        BaseNode
            The child node that was removed.

        Raises
        ------
        IndexError
            If `index` is out of bounds or if no child exists at the given `index`.
        """
        child = self._children[index]
        self._children[index] = None
        self._num_children -= 1
        
        if child:
            properties = self._get_properties_for_removed_child()
            child._set_properties(properties)

            child.collect_descendants(reason='pop')

        return child
    
    def replace_child(self, index: int, 
                      new_child: 'BaseNode') -> 'BaseNode':
        """Replaces an existing child node at a specific index with a new child.

        The old child is first removed (popped), and then the `new_child`
        is added to the same index. If the `new_child` cannot be added
        (e.g., due to type mismatch or cycle creation), the operation is
        rolled back, and the original child is re-inserted.

        Parameters
        ----------
        index : int
            The index of the child to be replaced.
        new_child : BaseNode
            The new node to place at the specified index.

        Returns
        -------
        BaseNode
            The old child node that was replaced.

        Raises
        ------
        IndexError
            If `index` is out of bounds or no child exists at `index`.
        TypeError
            If `new_child` is not of a type permitted for the specified `index`.
        ValueError
            If adding `new_child` would create a cycle in the tree.
        """
        old_child = self.pop_child(index)
        try:
            self.add_child(new_child, index=index)
        except Exception as e:
            # if new child caused an error, rollback changes
            self.add_child(old_child, index=index)
            raise e

        return old_child

    def remove_all_children(self):
        """Removes all children from this node.

        This iterates through all child slots, calling :py:meth:`~.BaseNode.pop_child`
        for each non-empty slot, effectively detaching all children and resetting
        their parent references and depths.
        """
        for i in range(len(self._children)):
            child = self._children[i]
            if child is not None:
                self.pop_child(i)

        self._num_children = 0

    def collect_descendants(self, reason: CollectionReason) -> set['BaseNode']:
        """Collects all descendant nodes reachable from this node, optionally including itself.

        This method performs a depth-first traversal to gather all nodes
        in the subtree rooted at this node (or its immediate children if `include_self` is :py:obj:`False`).
        It also detects and raises an error if a cycle is present in the tree.

        Parameters
        ----------
        include_self : bool, optional
            If :py:obj:`True`, this node itself is included in the returned set.
            If :py:obj:`False`, only its children and their descendants are included
            (default is :py:obj:`True`).

        Returns
        -------
        set of BaseNode
            A set containing all unique :py:class:`~.BaseNode` instances in the
            subtree rooted at this node (or its children), excluding duplicates.

        Raises
        ------
        ValueError
            If a cycle is detected in the tree structure (a node is encountered more than once).
        """
        node_set = set()
        if not self._collect_descendants(node_set, reason):
            if reason in ['add', 'pop']:
                self._rollback_changes(node_set, reason)
            raise BaseNode.CycleDetectedError(
                "Cycle encountered in node tree. All changes rolled back."
                )
        
        return node_set

    # - - Helper Methods - -

    def _collect_descendants(self, visited: set['BaseNode'],
                             reason: CollectionReason) -> bool:
        """Recursively collects descendants for :py:meth:`~.BaseNode.collect_descendants`.

        This is an internal helper method used for the recursive traversal.
        It adds the current node to `node_set` and then recursively calls
        itself for each child. It includes a check for cycles.

        Parameters
        ----------
        node_set : set[BaseNode]
            The set to which discovered nodes are added. This set also serves
            to track visited nodes for cycle detection.

        Raises
        ------
        ValueError
            If a cycle is detected (the current node is already in `node_set`).
        """
        if self in visited:
            return False
            
        self._on_collect_descendants(reason)
        visited.add(self)
        
        modifying_children = reason in ['add', 'pop']
        properties = (modifying_children and \
                      self._get_properties_to_pass_to_children()) or {}
        
        for child in self._children:
            if child is not None:
                child._set_properties(properties)
                if not child._collect_descendants(visited, reason):
                    return False
        
        return True
    
    def _on_collect_descendants(self, reason: CollectionReason):
        if reason == 'add':
            self._on_collect_descendants_add()
        if reason == 'pop':
            self._on_collect_descendants_pop()
    
    def _rollback_changes(self, visited: set['BaseNode'], 
                          collection_reason: CollectionReason):
        if collection_reason not in ['add', 'pop']:
            return
        
        for node in visited:
            node._rollback_properties()

            if collection_reason == 'add':
                node._rollback_add()
            if collection_reason == 'pop':
                node._rollback_pop()

    def _copy_children_from(self, other: 'BaseNode'):
        """Copies the children structure from another node of the same type.

        This method clears all existing children of the current node and then
        performs a deep copy of the children from the `other` node,
        adding them to the corresponding slots.

        Parameters
        ----------
        other : BaseNode
            The other :py:class:`~.BaseNode` instance from which to copy children.

        Raises
        ------
        TypeError
            If `other` is not of the same type as this node.
        """
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
    
    def _set_properties(self, properties: dict[str, Any]):
        # Method for a parent to set the properties of its children
        self._attr_cache.clear()
        for name, val in properties.items():
            self._attr_cache[name] = getattr(self, name)    # cache the old property
            setattr(self, name, val)

    def _rollback_properties(self):
        # Method for rolling back properties in all edited nodes 
        # in case of an error
        for name, val in self._attr_cache.items():
            setattr(self, name, val)

    # - - Overridable Helper Methods

    def cache_old_properties(self):
        self._attr_cache.clear()
        self._attr_cache['_parent'] = self._parent
        self._attr_cache['_depth'] = self._depth

    def _get_properties_for_removed_child(self):
        return {'_parent': None,
                '_depth': 0}
        
    def _get_properties_to_pass_to_children(self) -> dict[str, Any]:
        return {'_parent': self, 
                '_depth': self._depth + 1} 
    
    def _on_collect_descendants_add(self):
        pass

    def _on_collect_descendants_pop(self):
        pass

    def _rollback_pop(self):
        pass

    def _rollback_add(self):
        pass


    # - - Getters - -

    def get_possible_children_and_probs(self, index) -> Tuple[tuple[Type['BaseNode']], np.ndarray]:
        """Returns the possible child node types and their corresponding probabilities for a given index.

        This method retrieves the available child types for a specific slot
        and their associated probability distribution, which can be custom
        defined or a uniform distribution if no special probabilities are set.

        Parameters
        ----------
        index : int
            The child index for which to retrieve possible children and probabilities.

        Returns
        -------
        tuple[tuple[Type[BaseNode], ...], numpy.ndarray]
            A tuple containing:
            - A tuple of :py:class:`type` objects, representing the possible
              :py:class:`~.BaseNode` subclasses that can be placed at `index`.
            - A 1D :py:class:`numpy.ndarray` of floats representing the
              probability distribution over these possible children.

        Raises
        ------
        KeyError
            If `index` is not a valid child index for this node.
        """
        _possible_children = self.get_possible_children(index).copy()
        _probs = self.get_probs(index)

        return _possible_children, _probs

    def get_probs(self, index: int):
        """Returns the probability distribution for child types at a specific index.

        If a specific probability distribution is defined for `index` in
        :py:attr:`~.BaseNode._special_probs_dict`, it is returned. Otherwise,
        a uniform probability distribution is generated for all
        :py:meth:`~.BaseNode.get_possible_children` at that index.

        Parameters
        ----------
        index : int
            The child index for which to retrieve probabilities.

        Returns
        -------
        numpy.ndarray
            A 1D :py:class:`numpy.ndarray` of float64 representing the
            probability distribution over possible child types at `index`.

        Raises
        ------
        KeyError
            If `index` is not a valid child index for this node.
        """
        special_probs = self._special_probs_dict
        if index not in special_probs or special_probs[index] is None:
            size = len(self.get_possible_children(index))
            return np.ones(size) / size
        else:
            return special_probs[index].copy()
    
    def get_possible_children(self, index: int) -> list[Type['BaseNode']]:
        """Returns a list of node types that can be children at a specific index.

        Parameters
        ----------
        index : int
            The child index for which to retrieve possible node types.

        Returns
        -------
        list[Type[BaseNode]]
            A list of :py:class:`type` objects, where each type is a
            :py:class:`~.BaseNode` subclass that can be a child at `index`.

        Raises
        ------
        KeyError
            If `index` is not a valid child index for this node.
        """
        return self._possible_children_dict[index].copy()

    def get_all_possible_children(self) -> set[Type['BaseNode']]:
        """Returns a set of all unique node types that can ever be children of this node.

        This combines all possible child types across all child indices.

        Returns
        -------
        set of Type[BaseNode]
            A set of :py:class:`type` objects, representing all unique
            :py:class:`~.BaseNode` subclasses that this node can potentially have as a child.
        """
        return self._all_possible_children.copy()
    
    def get_parent(self) -> Tuple['BaseNode', int]:
        """Retrieves the parent node and the child index of this node.

        If the node has no parent (i.e., it is the root of a tree or a detached node),
        it returns ``(None, None)``. Otherwise, it returns a tuple containing
        the parent node and the index at which this node is a child of its parent.

        Returns
        -------
        tuple[BaseNode or None, int or None]
            A tuple containing:
            - The parent :py:class:`~.BaseNode` of this node, or :py:obj:`None` if it has no parent.
            - The integer index at which this node is a child of its parent,
              or :py:obj:`None` if it has no parent.
        """
        if self._parent is None:
            return None, None
      
        return self._parent, self._parent.get_index_of_child(self)


    # - - Properties - -

    @property
    def special_probs_dict(self) -> dict[int, np.ndarray]:
        """A copy of the dictionary mapping child indices to their custom probability distributions.

        Returns
        -------
        dict[int, numpy.ndarray]
            A dictionary where keys are child indices and values are
            :py:class:`numpy.ndarray` instances representing custom
            probability distributions for child types at that index.
            Returns a copy to prevent external modification.
        """
        _dup = {}
        for ind, probs_list in self._special_probs_dict.items():
            _dup[ind] = probs_list.copy()

        return _dup

    @property
    def possible_children_dict(self) -> dict[int, list[Type['BaseNode']]]:
        """A copy of the dictionary mapping child indices to lists of possible child types.

        Returns
        -------
        dict[int, list[Type[BaseNode]]]
            A dictionary where keys are child indices and values are
            lists of :py:class:`type` objects, representing the allowed
            :py:class:`~.BaseNode` subclasses for each child slot.
            Returns a copy to prevent external modification.
        """
        _dup = {}
        for ind, chld_list in self._possible_children_dict.items():
            _dup[ind] = chld_list.copy()

        return _dup
    
    @property
    def num_children(self) -> int:
        """The current number of children attached to this node.

        Returns
        -------
        int
            The count of non-empty child slots.
        """
        return self._num_children

    @property
    def child_depth(self) -> int:
        """The depth at which to set the children of this node.

        This is effectively `self.depth + 1`.

        Returns
        -------
        int
            The depth level of any direct children of this node.
        """
        return self._depth + 1

    @property
    def children(self) -> list['BaseNode']:
        """A list of the direct children of this node.

        The list includes :py:obj:`None` for empty child slots.
        Returns a shallow copy of the internal children list.

        Returns
        -------
        list of BaseNode or None
            A list containing references to the direct child :py:class:`~.BaseNode`
            instances, or :py:obj:`None` for unoccupied slots.
        """
        return [child for child in self._children]
    

    # - - Abstract Properties - -

    @property
    @abstractmethod
    def _possible_children_dict(self) -> dict[int, list[Type['BaseNode']]]:
        """Abstract property: A dictionary mapping child indices to their possible child types.

        Subclasses must implement this to define which types of nodes are
        allowed at each child position.

        Returns
        -------
        dict[int, list[Type[BaseNode]]]
            A dictionary where keys are integer child indices (0 to `max_num_children`-1)
            and values are lists of :py:class:`type` objects, representing the allowed
            :py:class:`~.BaseNode` subclasses for each child slot.
        """
        return NotImplemented

    @property
    @abstractmethod
    def _special_probs_dict(self) -> dict[int, np.ndarray]:
        """Abstract property: A dictionary mapping child indices to custom probability distributions.

        Subclasses can implement this to define non-uniform probability
        distributions for selecting child types at specific indices. If an index
        is not present or its value is :py:obj:`None`, a uniform distribution is assumed.

        Returns
        -------
        dict[int, numpy.ndarray]
            A dictionary where keys are integer child indices and values are
            1D :py:class:`numpy.ndarray` of floats representing probability
            distributions over the types returned by :py:attr:`~.BaseNode._possible_children_dict`
            for the corresponding index.
        """
        return NotImplemented
    
    @property
    @abstractmethod
    def _all_possible_children(self) -> set[Type['BaseNode']]:
        """Abstract property: A set of all unique node types that can be children of this node.

        Subclasses must implement this to return a comprehensive set of all
        :py:class:`~.BaseNode` subclasses that can ever be a child of this node,
        regardless of the specific child index.

        Returns
        -------
        set of Type[BaseNode]
            A set of :py:class:`type` objects.
        """
        return NotImplemented

    @property
    @abstractmethod
    def max_num_children(self) -> int:
        """Abstract property: The maximum number of children this node can have.

        Subclasses must implement this to define the capacity of the node.
        Terminal nodes must have `max_num_children` set to 0.

        Returns
        -------
        int
            The maximum number of children this node can hold.
        """
        return NotImplemented

    @property
    @abstractmethod
    def label(self) -> Optional[str]:
        """Abstract property: An optional human-readable label for the node.

        This label is used when printing a node and precedes its children's string representations.

        - If the label is a **non-empty string** (e.g., `'if_food_ahead'`), the node will be printed as
          `if_food_ahead(<child1>, <child2>, ...)`.
        - If the label is an **empty string** (`''`), the node will be printed as
          `(<child1>, <child2>, ...)`.
        - If the label is **`None`**, the node will be printed as
          `<child1>, <child2>, ...` (without parentheses or a label prefix).

        Returns
        -------
        str or None
            A string label for the node, or an empty string, or :py:obj:`None`.
        """
        return NotImplemented

    @property
    @abstractmethod
    def token(self) -> str:
        """Abstract property: A string representing this node.

        This token serves as the string representation of the node **when it has no children**,
        which is especially relevant for terminal nodes.

        For example, if a `my_node` has token `'<Root>'`, and `my_node`
        has no children, `print(my_node)` will output `'<Root>'`.

        Returns
        -------
        str
            A non-empty string token for the node.
        """
        return NotImplemented

    @property
    @abstractmethod
    def is_terminal(self) -> bool:
        """Abstract property: Indicates if this node is a terminal node.

        A terminal node cannot have any children (i.e., `max_num_children` must be 0).

        Returns
        -------
        bool
            :py:obj:`True` if this node is terminal, :py:obj:`False` otherwise.
        """
        return NotImplemented

    @property
    @abstractmethod
    def is_root(self) -> bool:
        """Abstract property: Indicates if this node is intended to be a root node.

        A root node cannot be a terminal node.

        Returns
        -------
        bool
            :py:obj:`True` if this node is designed to be a root, :py:obj:`False` otherwise.
        """
        return NotImplemented


    # - - Utilities - -

    def _children_as_string(self):
        """Generates a comma-separated string representation of the node's children.

        This helper method is used by the `__str__` method to create
        a compact string representation of the children, useful for
        tree visualization.

        Returns
        -------
        str
            A string with comma-separated string representations of the children.
            Empty slots are represented as empty strings.
        """
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
        """Provides a default deep copy mechanism for BaseNode and its subclasses.

        This helper method creates a new instance of the same node type and
        then recursively copies the children from the current node to the new instance.
        It's intended to be called by the `copy` method of subclasses.

        Parameters
        ----------
        *args :
            Positional arguments passed to the new node's constructor.
        **kwargs :
            Keyword arguments passed to the new node's constructor.

        Returns
        -------
        BaseNode
            A new :py:class:`~.BaseNode` instance that is a deep copy of this node.
        """
        _dup = type(self)(*args, **kwargs)
        _dup._copy_children_from(self)

        return _dup

    # - - Special Methods - -

    def copy(self) -> 'BaseNode':
        """Creates a deep copy of this BaseNode instance.

        This method utilizes :py:meth:`~.BaseNode._default_copy_method` to perform
        a recursive deep copy, ensuring that all descendants are also copied.

        Returns
        -------
        BaseNode
            A new :py:class:`~.BaseNode` instance that is a deep copy of the current node.
        """
        return self._default_copy_method()

    def __str__(self):
        """Returns a human-readable string representation of the node.

        For terminal nodes, this is simply their :py:attr:`~.BaseNode.token`.
        For non-terminal nodes, it constructs a string representing the node's
        :py:attr:`~.BaseNode.label` (if present) and a comma-separated list
        of its children's string representations.

        Returns
        -------
        str
            A string representation of the node, showing its structure and content.
        """
        if self.num_children == 0:
            return str(self.token)
        else:
            _str = self._children_as_string()
            if self.label is not None:
                _str = f"{self.label}({_str})"

        return _str

    def __hash__(self):
        """Returns the hash value for the node.

        The hash is based on the node's unique :py:attr:`~.BaseNode._identifier`,
        allowing node instances to be stored in sets and used as dictionary keys.

        Returns
        -------
        int
            The hash value of the node.
        """
        return hash(self._identifier)
