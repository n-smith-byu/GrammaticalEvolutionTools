from ...meta import BaseNode

import warnings
import inspect

import numpy as np

from typing import Type, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .program_tree import ProgramTree


class ProgramNode(BaseNode):
    """Represents a node within a program tree, extending BaseNode.

    This class is designed as a foundational, **custom-abstract** building block for nodes,
    defining core properties and a unique, carefully controlled initialization pattern
    that dictates its instantiability.

    **Important Note on Custom Abstractness and Subclass Chaining:**
    `ProgramNode` itself is considered "abstract" in a custom sense and **cannot be
    instantiated directly**. Its abstract nature, and that of its subclasses, is
    determined both by the argument requirements of its internal initialization methods:
    :py:meth:`~.ProgramNode._base_node_init` and :py:meth:`~.ProgramNode._custom_init`, 
    and by the presence of unimplemented abstract methods. 

    A subclass of `ProgramNode` becomes truly **concrete** (instantiable by your
    system) when its specific implementations of :py:meth:`~.ProgramNode._base_node_init` 
    and :py:meth:`~.ProgramNode._custom_init` can be called **without requiring any 
    arguments beyond `self`**.

    Attributes
    ----------
    SHOW_WARNINGS : bool
        A class-level flag that controls whether warnings are shown during
        assertion checks (e.g., for unused indices in probability dictionaries).
    _program_tree_cls : Type['ProgramTree'] or None
        A cached reference to the `ProgramTree` class, imported lazily.
    _token : str
        The string token representing this node, used for printing when no children are present.
    _label : str or None
        An optional human-readable label for the node, used for printing non-terminal nodes.
    _is_terminal : bool
        Indicates if this node is a terminal node (cannot have children).
    _is_root : bool
        Indicates if this node is designed to be a root node (cannot be terminal).
    _max_num_children : int
        The maximum number of children this node can accommodate.
    __possible_children_dict : dict[int, list[Type['ProgramNode']]]
        A private dictionary mapping child indices to lists of allowed `ProgramNode` types.
    __special_child_probs : dict[int, numpy.ndarray]
        A private dictionary mapping child indices to custom probability distributions
        over their possible child types.
    __all_possible_children : set[Type['ProgramNode']]
        A private set containing all unique `ProgramNode` types that can be children of this node.
    _program : ProgramTree or None
        A reference to the `ProgramTree` instance this node belongs to, or :py:obj:`None` if detached.

    See Also
    --------
    :py:class:`~._base.base_node.BaseNode`
    :py:class:`~._base.meta.BaseNodeMeta`
    :py:class:`~.tree.ProgramTree`
    :py:meth:`~.ProgramNode._init_has_extra_args`

    Notes
    -----
    This class is intended to be subclassed. Subclasses will primarily define
    the concrete values for properties inherited or extended from `BaseNode`
    (e.g., :py:attr:`~.BaseNode.token`, :py:attr:`~.BaseNode.label`,
    :py:attr:`~.BaseNode.max_num_children`, etc.) by calling their **immediate parent's**
    :py:meth:`~.ProgramNode._base_node_init` method.

    Subclasses can either:
    1.  Provide *all* remaining required parameters to `_base_node_init` (and `_custom_init`),
        making the class concrete.
    2.  Provide *some* required parameters and expose others as new parameters in their
        own `_base_node_init` (and `_custom_init`) methods, remaining abstract and
        expecting *their* subclasses to fulfill the remaining parameters. This allows
        for a flexible chain of abstract definitions.

    All custom properties specific to `ProgramNode` or its further subclasses,
    which are not directly related to `BaseNode`'s core attributes, should be
    defined and initialized within the :py:meth:`~.ProgramNode._custom_init` method.
    """

    SHOW_WARNINGS: bool = True

    # - - - - - - - - - - - - - - -

    @classmethod
    def _init_has_extra_args(cls) -> bool:
        """Class method: Checks if the `_base_node_init` or `_custom_init` methods of this class take any arguments beyond `self`.

        This method **overrides** a similar check (or expectation) from `BaseNodeMeta`
        to provide custom logic for `ProgramNode` and its subclasses. It is crucial
        for the custom abstractness enforcement within the inheritance chain.

        Specifically, it inspects the method signatures of both
        :py:meth:`~.ProgramNode._base_node_init` and :py:meth:`~.ProgramNode._custom_init`
        for the current class (`cls`). If either of these methods defines any parameters
        in addition to the required `self` (i.e., `len(params) > 1`), it indicates
        that the class's initialization process still requires external arguments,
        thus deeming the class "abstract" and preventing direct instantiation.

        Returns
        -------
        bool
            :py:obj:`True` if either :py:meth:`~.ProgramNode._base_node_init` or
            :py:meth:`~.ProgramNode._custom_init` requires parameters beyond `self`,
            :py:obj:`False` otherwise.
        """ 
        base_node_init = cls._base_node_init
        sig1 = inspect.signature(base_node_init)
        params1 = list(sig1.parameters.values())

        custom_init = cls._custom_init
        sig2 = inspect.signature(custom_init)
        params2 = list(sig2.parameters.values())
        
        return len(params1) > 1 or len(params2) > 1
    
    # - - - - - - - - - - - - - - -

    # - - Assertions - -

    def _assert_possible_child_type_is_valid(self, node_type: Type):
        """Asserts that a given node type is a valid `ProgramNode` subclass and not a root node.

        This internal assertion is called during the setup of `__possible_children_dict`
        to ensure that only valid `ProgramNode` types are listed as possible children.
        It specifically disallows root node types as children.

        Parameters
        ----------
        node_type : Type
            The node class (type) to validate.

        Raises
        ------
        TypeError
            If `node_type` is not a class or is not a subclass of `ProgramNode`.
        ValueError
            If `node_type` is a class designated as a root node.
        """
        if not isinstance(node_type, type) or \
                not issubclass(node_type, ProgramNode):
            raise TypeError(
                f"Possible Children must be of type "
                f"Type[{ProgramNode.__name__}]. "
                f"Obj at fault: {node_type}"
            )

        node_type: Type[ProgramNode]

    def _assert_vals_valid(self):
        """Performs a series of assertions to validate the node's internal state.

        This method centralizes the validation calls for various properties
        like token, label, tags, max number of children, and the structure
        of possible children and special probabilities. It relies on static
        assertion methods defined in `BaseNode`.

        Warnings related to unused indices in probability/children dictionaries
        are controlled by `ProgramNode.SHOW_WARNINGS`.

        Raises
        ------
        TypeError
            If any of the validated values have an incorrect type.
        ValueError
            If any of the validated values are logically inconsistent or invalid.
        KeyError
            If `__possible_children_dict` is missing expected keys.
        UserWarning
            If `SHOW_WARNINGS` is :py:obj:`True` and unused indices are found.
        """
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

    def _assert_editable(self):
        if self._program:
            self._program._assert_editable()

    # - - Initialization Helpers - - 

    def _init_possible_children(self, possible_children_dict: dict,
                                special_child_probs_dict: dict):
        """Initializes the node's `__possible_children_dict` and `__special_child_probs`.

        This helper method iterates through the provided dictionaries and
        sets the possible children types and their associated probabilities
        for each child index using :py:meth:`~.ProgramNode._set_possible_children`.

        Parameters
        ----------
        possible_children_dict : dict[int, list[Type[ProgramNode]]]
            A dictionary defining the allowed child node types for each index.
        special_child_probs_dict : dict[int, list[float]]
            A dictionary defining custom probability distributions for child
            selection at specific indices.
        """
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
        """Sets the possible children types for a specific index and optionally their probabilities.

        This method validates each `node_type` in `possible_children_list`
        using :py:meth:`~.ProgramNode._assert_possible_child_type_is_valid`. It then updates
        `__possible_children_dict` and `__all_possible_children`. If
        `special_probs` are provided, it also calls :py:meth:`~.ProgramNode._set_child_probs`.

        Parameters
        ----------
        index : int
            The child index for which to set the possible children.
        possible_children_list : list[Type[ProgramNode]]
            A list of `ProgramNode` types that can be children at `index`.
        special_probs : numpy.ndarray, optional
            A 1D NumPy array of probabilities corresponding to `possible_children_list`.
            If :py:obj:`None`, no special probabilities are set for this index.

        Raises
        ------
        TypeError
            If any `node_type` in `possible_children_list` is invalid.
        ValueError
            If any `node_type` in `possible_children_list` is a root node type.
            If `special_probs` has a size mismatch with `possible_children_list`.
        """
        for node_cls in possible_children_list:
            self._assert_possible_child_type_is_valid(node_cls)

        self.__possible_children_dict[index] = possible_children_list.copy()
        self.__all_possible_children.update(
            self.__possible_children_dict[index])

        if special_probs is not None:
            self._set_child_probs(index, special_probs)

    def _set_child_probs(self, index: int, probs: list[float]):
        """Sets the probability distribution for child types at a specific index.

        This method requires that possible children for the given `index`
        have already been defined. It validates the length of `probs` against
        the number of possible children at that index and stores the probability
        array.

        Parameters
        ----------
        index : int
            The child index for which to set the probabilities.
        probs : numpy.ndarray
            A 1D NumPy array of probabilities. Its length must match the
            number of possible children at `index`.

        Raises
        ------
        ValueError
            If no possible children are defined for the `index`.
            If the length of `probs` does not match the number of possible children.
        """
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
        """Initializes a new instance of ProgramNode.

        This constructor orchestrates the initialization process by calling
        two internal initialization methods:
        :py:meth:`~.ProgramNode._base_node_init` to set up core `BaseNode` properties
        and :py:meth:`~.ProgramNode._custom_init` for `ProgramNode`-specific initialization.

        **This method should not be overridden by subclasses.**
        Instead, subclasses should implement their logic within their own
        overrides of :py:meth:`~.ProgramNode._base_node_init` and
        :py:meth:`~.ProgramNode._custom_init`.

        **Instantiation Requirement:**
        For a `ProgramNode` subclass to be concrete (instantiable), its override of
        :py:meth:`~.ProgramNode._base_node_init` and :py:meth:`~.ProgramNode._custom_init`
        **must not require any arguments beyond `self`**. This is enforced by
        :py:meth:`~.ProgramNode._init_has_extra_args` and `BaseNodeMeta`.
        """
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
        """Initializes the fundamental properties of the node inherited or extended from `BaseNode`.

        This method is responsible for setting :py:attr:`~.ProgramNode._token`,
        :py:attr:`~.ProgramNode._label`, :py:attr:`~.ProgramNode._is_terminal`,
        :py:attr:`~.ProgramNode._is_root`, :py:attr:`~.ProgramNode._max_num_children`,
        and for initializing the child-related dictionaries (`__possible_children_dict`,
        `__special_child_probs`, `__all_possible_children`).
        It also performs initial validation via :py:meth:`~.ProgramNode._assert_vals_valid`.

        **Subclasses of `ProgramNode` (and intermediate abstract subclasses) are expected to 
        override this method.** The override can take one of two forms:

        1.  **Chained Abstract Definition:** The subclass defines *some* of these parameters
            but leaves others as arguments for *its own* `_base_node_init` override. It then calls its
            **immediate parent's** `_base_node_init` method using the explicit class name,
            passing along the parameters it receives:

            .. code-block:: python

                class AbstractTerminalNode(ProgramNode):
                    def _base_node_init(self, token: str, label: Optional[str] = None):
                        # Fix 'is_terminal' to True and 'num_children' to 0 for all descendants
                        # Pass 'token' and 'label' down to ProgramNode's _base_node_init
                        ProgramNode._base_node_init(
                            self,
                            token=token,
                            is_terminal=True,
                            is_root=False,
                            num_children=0,
                            label=label,
                        )

        2.  **Concrete Definition:** The subclass defines *all* remaining required parameters,
            resulting in a parameter-less `_base_node_init` override, making the class concrete.
            It calls its immediate parent's `_base_node_init` with all values:

            .. code-block:: python

                class MyConcreteTerminalNode(AbstractTerminalNode):
                    def _base_node_init(self):
                        # This class is concrete because its _base_node_init takes no args
                        # It calls its parent (AbstractTerminalNode) and provides the token/label
                        AbstractTerminalNode._base_node_init(
                            self,
                            token="MY_TERM",
                            label="My Terminal Node"
                        )


        Parameters
        ----------
        token : str
            The string token for this node.
        is_terminal : bool
            Whether this node is a terminal node.
        is_root : bool
            Whether this node is a root node.
        num_children : int
            The maximum number of children this node can have.
        label : str, optional
            An optional human-readable label.
        possible_children_dict : dict[int, list[Type[ProgramNode]]], optional
            A dictionary defining allowed child types per index.
        special_child_probs : dict[int, list[float]], optional
            Custom probability distributions for child selection.

        Warnings
        --------
        A warning is issued if `special_child_probs` is provided when
        `possible_children_dict` is :py:obj:`None`.
        """
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
        """Performs custom, `ProgramNode`-specific initialization.

        This method is called by :py:meth:`~.ProgramNode.__init__` after
        :py:meth:`~.ProgramNode._base_node_init` has been executed.
        It is the designated place for defining and initializing **all custom properties**
        that are specific to `ProgramNode` or its subclasses, and are not directly
        related to the core attributes inherited or extended from `BaseNode`.

        **Subclasses can override this method.**
        Similar to `_base_node_init`, the override can either take no parameters
        (making the class concrete with respect to custom initialization) or
        introduce its own parameters to be fulfilled by further subclasses in the chain.

        When overriding, it should call its **immediate parent's** `_custom_init` method
        using the explicit class name, *not* `super()`:

        .. code-block:: python

            class AbstractNodeWithCache(ProgramNode):
                # ... _base_node_init override ...

                def _custom_init(self, cache_size: int):
                    # Call ProgramNode's _custom_init first
                    ProgramNode._custom_init(self) # Explicitly pass 'self'
                    self._cache_size = cache_size
                    self._node_cache = {} # Initialize a custom property


            class ConcreteNodeWithSmallCache(AbstractNodeWithCache):
                # ... _base_node_init override ...

                def _custom_init(self):
                    # This class is concrete for _custom_init as it takes no args
                    # It calls its parent (AbstractNodeWithCache) and provides the cache_size
                    AbstractNodeWithCache._custom_init(self, cache_size=10)

                    # Further custom properties specific to ConcreteNodeWithSmallCache can go here
        """
        self._program: 'ProgramTree' = None
        self._parent: ProgramNode


    # - - Public Methods - -

    def add_child(self, new_child: 'ProgramNode', index = None) -> int:
        """Adds a `ProgramNode` as a child to this node.

        This method extends the functionality of `BaseNode.add_child`. In addition
        to adding the child, it ensures that the `_program` reference for the new
        child (and its entire subtree) is correctly set to this node's `_program`.

        Parameters
        ----------
        new_child : ProgramNode
            The `ProgramNode` instance to add as a child.
        index : int, optional
            The index at which to add the child. If :py:obj:`None`, the child is appended.

        Returns
        -------
        int
            The index at which the child was added.

        Raises
        ------
        ValueError
            If `new_child` is already part of another `ProgramTree`.
            If `new_child` is not compatible with `__possible_children_dict` at `index`.
        IndexError
            If `index` is out of bounds or `max_num_children` is exceeded.
        """
        self._assert_editable()
        if new_child._program:
            raise ValueError("new_child must not be part of another program.")

        index = BaseNode.add_child(self, new_child, index=index)  

        if self._program:
            self._program._cache_depth()
        
        return index

    def pop_child(self, index) -> 'ProgramNode':
        self._assert_editable()
        removed_node = BaseNode.pop_child(self, index)

        if self._program:
            self._program._cache_depth()
        
        return removed_node

    # - - Overridden Methods - - 

    def _get_properties_to_pass_to_children(self) -> dict[str, Any]:
        properties = BaseNode._get_properties_to_pass_to_children(self)
        properties['_program'] = self._program
        return properties
    
    def _get_properties_for_popped_child(self):
        properties = BaseNode._get_properties_for_popped_child(self)
        properties['_program'] = None
        return properties
    
    def _on_collect_descendants_attach(self):
        if self._program and not (self in self._program._nodes):
            self._program._nodes.add(self)
            self._program._nodes_by_type[type(self)].add(self)
            self._program._level_counts[self._depth] += 1

    def _on_collect_descendants_detach(self):
        program: ProgramTree = self._attr_cache['_program']
        if program and (self in program._nodes):
            original_depth = self._attr_cache['_depth']

            # remove the node from the tree's collections
            program._nodes.discard(self)
            program._nodes_by_type[type(self)].discard(self)
            program._level_counts[original_depth] -= 1

            # remove any non-used keys
            if not program._nodes_by_type[type(self)]:
                program._nodes_by_type.pop(type(self))
            if not program._level_counts[original_depth]:
                program._level_counts.pop(original_depth)   

    def _rollback_detach(self):
        self._on_collect_descendants_detach()

    def _rollback_attach(self):
        self._on_collect_descendants_attach()


    # - - Properties - -

    @property
    def _possible_children_dict(self) -> dict[int, list[Type['ProgramNode']]]:
        """dict[int, list[Type['ProgramNode']]]: A dictionary mapping child indices to lists of allowed `ProgramNode` types.

        This property provides access to the internal `__possible_children_dict`
        which defines the structural constraints for this node's children.
        """
        return self.__possible_children_dict

    @property
    def _special_probs_dict(self) -> dict[int, np.ndarray]:
        """dict[int, numpy.ndarray]: A dictionary mapping child indices to custom probability distributions
        over their possible child types.

        This property provides access to the internal `__special_child_probs`
        which defines custom probability weights for child selection at specific positions.
        """
        return self.__special_child_probs
    
    @property
    def _all_possible_children(self) -> set[Type['ProgramNode']]:
        """set[Type['ProgramNode']]: A set containing all unique `ProgramNode` types that can be children of this node.

        This property provides a consolidated view of all distinct `ProgramNode` types
        that can be placed as children at any valid index of this node.
        """
        return self.__all_possible_children

    @property
    def max_num_children(self) -> int:
        """int: The maximum number of children this node can accommodate.

        This property reflects the `_max_num_children` attribute set during initialization,
        defining the structural capacity of the node.
        """
        return self._max_num_children

    @property
    def label(self) -> Optional[str]:
        """str or None: An optional human-readable label for the node.

        This property provides access to the `_label` attribute, typically used for
        printing non-terminal nodes in a more descriptive way than their token.
        """
        return self._label

    @property
    def token(self) -> str:
        """str: The string token representing this node.

        This property provides access to the `_token` attribute, which is a concise
        string representation primarily used for printing terminal nodes or when
        a label is not available.
        """
        return self._token

    @property
    def is_terminal(self) -> bool:
        """bool: Indicates if this node is a terminal node.

        A terminal node cannot have any children. This property reflects the
        `_is_terminal` attribute set during initialization.
        """
        return self._is_terminal

    @property
    def is_root(self) -> bool:
        """bool: Indicates if this node is designed to be a root node.

        A root node cannot be terminal and is typically the entry point of a program tree.
        This property reflects the `_is_root` attribute set during initialization.
        """
        return self._is_root
