from ..nodes.basic_nodes import NonTerminalNode, RootNode, ExecutableNode
from .program_node import ProgramNode

from collections import defaultdict
from enum import IntEnum
import random

from typing import Type, Union, Tuple, Set
    
    
class ProgramTree:
    """Represents a program as a hierarchical tree structure of interconnected nodes.

    This class provides the foundational framework for managing and
    executing a program defined by a hierarchical arrangement of
    :py:class:`~.nodes.ProgramNode` objects. It tracks the program's
    state, its constituent nodes, and facilitates interactions
    with an optional :py:class:`~.agents.Agent`.

    Parameters
    ----------
    root : RootNode or Type[RootNode]
        The root node of the program tree, serving as the entry point
        for program execution.

    Attributes
    ----------
    _root : ~.nodes.basic_nodes.RootNode
        The root node of the tree. This serves as the entry point for program
        execution and acts as the anchor for the entire tree structure.
    _nodes : set of ~.nodes.ProgramNode
        A set containing all unique :py:class:`~.nodes.ProgramNode` objects
        within the tree. This provides a fast lookup mechanism for any node
        in the program tree.
    _nodes_by_type : dict[type, set[~.nodes.ProgramNode]]
        A dictionary that organizes nodes by their type. Each key is a
        :py:class:`type` object (e.g., ``ConditionNode``, ``ActionNode``),
        and its corresponding value is a :py:class:`set` of all
        :py:class:`~.nodes.ProgramNode` instances of that specific type present
        in the tree. This facilitates quick access to nodes based on their class.
    _nodes_dirty : bool
        A flag indicating whether the internal node collections
        (:py:attr:`._nodes`, :py:attr:`._nodes_by_type`) need to be
        re-scanned and updated. This is typically set to :py:obj:`True`
        after structural changes to the tree.
    _max_child_depth : int or None
        The maximum depth of the tree (number of levels below the root).
        This value is calculated lazily, meaning it's computed only when
        first requested after a potential change. It is :py:obj:`None`
        if not yet calculated or if the tree is empty.
    _agent : ~.agents.Agent or None
        The agent instance to which this program is attached, if any.
        If an agent is provided during initialization, this attribute
        holds a reference to it, enabling program-agent interactions.
    _program_stack : list of ~.nodes.ProgramNode
        An internal list used to manage the execution flow of the program.
        This acts as a call stack for program nodes during traversal or execution.

    """

    # - - Exceptions - - 

    class ProgramInProgressError(RuntimeError):
        """Exception raised when program modification is attempted while the program is currently running."""
        pass

    class NodeMissingChildError(RuntimeError):
        """Exception raised when a program encounters a node that is missing a child.

        This typically indicates an `incomplete` program structure
        or a bug in the tree generation/modification logic.
        """
        pass

    # - - Assertions - - 

    def _assert_root_valid(self):
        if not isinstance(self._root, RootNode):
            raise TypeError(
                "Program root must be an instance of RootNode."
                f"Found object of type {type(self._root).__name__}"
                )

    def _assert_editable(self):
        if self.running():
            raise ProgramTree.ProgramInProgressError(
                "Cannot modify nodes in a program while it is running. " \
                "Please kill the program or run it to completion first."
            )
        
    def _assert_runnable(self):
        pass        # optional for addins and subclasses

    # - - Constants - - 

    RANDOM_REPLACEMENT = 'Random'
    """A sentinel value used with :py:meth:`~.ProgramTree.replace_node`
    to indicate that a node should be replaced by a randomly generated branch.
    """
    
    class Status(IntEnum):
        """An enumeration representing the execution status of a program."""
        EXITED = 0
        """The program has finished execution."""
        RUNNING = 1
        """The program is currently executing."""

    # - - Initialization - - 

    def __init__(self, root: Union[RootNode, Type[RootNode]],
                 autofill=True):
        """Initializes a ProgramTree instance with a root node and an optional agent.

        This constructor sets up the fundamental structure of the program tree,
        establishing the root node and preparing internal data structures for
        node management and program execution.

        Parameters
        ----------
        root : RootNode
            The root node of the program tree, serving as the entry point
            for program execution.
        agent : Agent, optional
            An optional agent instance to which this program is attached.
            If provided, the program can interact with the agent during execution.

        Notes
        -----
        Internal attributes (prefixed with `_`) are managed by the class and
        typically not intended for direct external access. They may be accessed by 
        subclasses, however. 

        For setting up the initial tree, the :py:meth:`~.ProgramTree.__init__`
        constructor establishes a bidirectional link between the root node
        and the program tree via :py:meth:`~.nodes.ProgramNode._set_program`.
        It then calls :py:meth:`~.ProgramTree._fill_out_program` to recursively
        discover and register all nodes reachable from the root, populating the
        tree's initial structure and internal node collections.
        """
        self._root: 'RootNode' = None
        self._nodes: set['ProgramNode'] = set()
        self._nodes_by_type: dict[type, set['ProgramNode']] = defaultdict(set)
        self._level_counts = defaultdict(int)   # keeps track of how many nodes on each level
        self._max_node_depth = -1

        self._program_stack: list['ProgramNode'] = []

        self._verify_and_set_root(root)
        self._collect_nodes()
        
        if autofill:
            self._fill_out_program()

    def _verify_and_set_root(self, root):
        self._root = root() if isinstance(root, type) else root
        self._assert_root_valid()

    # - - Private Helpers - - 

    def _cache_depth(self):
        if not self._level_counts:
            self._max_node_depth = -1
        else:
            self._max_node_depth = max(key for key in self._level_counts \
                                        if self._level_counts[key] > 0)

    def _collect_nodes(self):
        """Collects all nodes in the program tree and updates the internal node collections.

        This internal method is responsible for traversing the tree from the
        :py:attr:`~.ProgramTree._root` node to discover all connected nodes.
        It populates the :py:attr:`~.ProgramTree._nodes` set and
        :py:attr:`~.ProgramTree._nodes_by_type` dictionary. It also
        calculates the maximum depth of the tree and stores it in
        :py:attr:`~.ProgramTree._max_child_depth`.

        This method is called lazily by properties and methods that rely on
        up-to-date node collections (e.g., :py:meth:`~.ProgramTree.size`,
        :py:meth:`~.ProgramTree.depth`, :py:meth:`~.ProgramTree.get_nodes_by_type`).
        It only performs the collection if the :py:attr:`~.ProgramTree._nodes_dirty`
        flag is :py:obj:`True`.

        Returns
        -------
        set of ProgramNode
            A set containing all :py:class:`~.nodes.ProgramNode` instances within the tree.
        """
        self._nodes.clear()
        self._nodes_by_type.clear()
        self._level_counts.clear()

        self._root._program = self
        self._root.collect_descendants(traversal_mode='attach')
        self._cache_depth()

    def _fill_out_program(self):
        """Recursively fills out the program tree by adding random children to incomplete nodes.

        This method ensures that all non-terminal nodes have their required number
        of children, creating a complete and runnable program structure. It uses
        a breadth-first-like traversal starting from existing incomplete nodes.

        Process:
        
        1. Calls :py:meth:`~.ProgramTree._collect_nodes` to get all current nodes
           and ensure node collections are up-to-date.

        2. Initializes a queue with all nodes that have fewer than their maximum
           number of children.

        3. Enters a loop that continues as long as the queue is not empty:

           a. Dequeues a `curr_node`.

           b. While `curr_node` still needs children:

              i. Determines possible child node types and their probabilities
                 using :py:meth:`~.nodes.ProgramNode.get_possible_children_and_probs`.

              ii. Randomly selects a `child_node_class`.

              iii. Creates an instance of the `child_node_class`.

              iv. Adds the new child to the queue (if it might need children too).

              v. Attaches the child to `curr_node` using :py:meth:`~.nodes.ProgramNode.add_child`.
                 This action is expected to update node relationships and potentially
                 signal the tree that its node collections are now dirty.
        """
        queue = [node for node in self._nodes if node.num_children < node.max_num_children]
        
        while len(queue) > 0:
            curr_node: 'ProgramNode' = queue.pop(0)
            while curr_node.num_children < curr_node.max_num_children:
                for i, child in enumerate(curr_node._children):
                    if not child:
                        possible_children, probs = curr_node.get_possible_children_and_probs(i)
                        child_node_class = random.choices(possible_children, probs, k=1)[0]
                        child_node = child_node_class()

                        queue.append(child_node)
                        curr_node.add_child(child_node, index=i)


    # - - Public Methods - - 

    def get_nodes_by_type(self, node_type: type) -> set['ProgramNode']:
        """Get all nodes of a specific type.

        Parameters
        ----------
        node_type : type
            The :py:class:`type` of nodes to retrieve.
            This should be a subclass of :py:class:`~.nodes.ProgramNode`.

        Returns
        -------
        set of ProgramNode
            A set of all :py:class:`~.nodes.ProgramNode` instances of the specified type
            found within the program tree. If no nodes of the type exist, an empty set is returned.
        """
        return self._nodes_by_type[node_type]

    def get_parent_of_node(self, node: 'ProgramNode') -> Tuple['ProgramNode', int]:
        """Retrieves the parent node and the child index of a given node within this tree.

        This method identifies the direct parent of the specified `node`
        and returns its position (index) within that parent's children.

        Parameters
        ----------
        node : ProgramNode
            The node for which to find the parent. This node must be part of
            the current :py:class:`~.ProgramTree`.

        Returns
        -------
        tuple[ProgramNode, int]
            A tuple containing:
            - The parent :py:class:`~.nodes.ProgramNode` of the given node.
            - The integer index at which the node is a child of its parent.

        Raises
        ------
        ValueError
            If the provided `node` is not found within this program tree.
            If the provided `node` is the :py:attr:`~.ProgramTree._root` node,
            as the root has no parent.
        """
        if node not in self.nodes:
            raise ValueError('Node does not exist in tree')
        
        return node.get_parent()
    
    # - - Editing the Program - - 

    def replace_node(self, node, new_node: Union['ProgramNode', str] \
                     = RANDOM_REPLACEMENT):
        """Replaces a specific node in the tree with another node or a randomly generated branch.

        If `new_node` is set to :py:attr:`~.ProgramTree.RANDOM_REPLACEMENT`, the
        node will be conceptually "removed" (its slot becomes empty) and then
        subsequently filled in by a new complete randomly generated branch
        during the call to :py:meth:`~.ProgramTree._fill_out_program`.

        Parameters
        ----------
        node : ProgramNode
            The existing :py:class:`~.nodes.ProgramNode` in the tree to be replaced.
        new_node : ProgramNode or str, optional
            The node to replace `node` with. Can be an instance of
            :py:class:`~.nodes.ProgramNode` or the string
            :py:attr:`~.ProgramTree.RANDOM_REPLACEMENT` (default) for random replacement.

        Raises
        ------
        ValueError
            If an attempt is made to replace the :py:attr:`~.ProgramTree._root` node.
            If the provided `node` is not part of this tree.
        ProgramTree.BoundToAgentError
            If the program is currently :py:meth:`~.ProgramTree.bound_to_agent`.
            Structural modifications are disallowed while bound to an agent.
        ProgramTree.ProgramInProgressError
            If the program is currently :py:meth:`~.ProgramTree.running`.
            Structural modifications are disallowed during execution.
        """
        if node is self._root:
            raise ValueError(
                "Cannot Replace the Root Node in Tree. " 
                "Try replacing a child node instead."
            )

        # get the parent of the node to replace and the node it is at
        parent_node, index = self.get_parent_of_node(node)
        
        # if no replacement node specified, replace randomly
        if new_node is ProgramTree.RANDOM_REPLACEMENT:
            parent_node.pop_child(index)     # will get randomly replaced when tree is filled out
        else:
            parent_node.replace_child(index, new_node)

        self._fill_out_program()        # ensure program is complete


    # - - Program Execution - - 

    def tick(self) -> 'ProgramTree.Status':
        """Executes a single step of the program's execution.

        This method advances the program by one execution step.
        If the program is in an :py:attr:`~.ProgramTree.Status.EXITED` state,
        it will start execution from the :py:attr:`~.ProgramTree._root` node.
        It processes one executable node or advances the execution stack.

        Returns
        -------
        ProgramTree.Status
            The current :py:class:`~.ProgramTree.Status` of the program
            after the tick (either :py:attr:`~.ProgramTree.Status.RUNNING` or :py:attr:`~.ProgramTree.Status.EXITED`).

        Raises
        ------
        ProgramTree.MissingAgentError
            If the program is not :py:meth:`~.ProgramTree.bound_to_agent`.
        ProgramTree.NodeMissingChildError
            If an incomplete node is encountered during execution, indicating
            a structural issue in the program tree.
        """
        self._assert_runnable()

        # if stack empty, add root node
        if self.status == ProgramTree.Status.EXITED:
            self._program_stack.append(self._root)
            self._root.reset()

        while len(self._program_stack) > 0:
            # get the next node to run. 
            curr_node = self._program_stack[-1]
            if curr_node.num_children < curr_node.max_num_children:
                raise ProgramTree.NodeMissingChildError(
                    msg='Expected tree to be completely filled out, but'
                        'encountered node with missing children.'
                )
            if isinstance(curr_node, ExecutableNode):
                # run the node, then pop it off the stack
                curr_node.execute()
                self._program_stack.pop(-1)
                break
            else:
                curr_node: 'NonTerminalNode'
                next_child = curr_node.get_next_child()
                if next_child is None:
                    # if no more children nodes to run, pop the current node off the stack
                    self._program_stack.pop(-1)
                else:
                    self._program_stack.append(next_child)
                
        return self.status
    
    def kill(self):
        """Immediately stops the execution of the program and resets its state.

        This method clears the internal :py:attr:`~.ProgramTree._program_stack`
        and calls :py:meth:`~.nodes.ProgramNode.reset` on the :py:attr:`~.ProgramTree._root`
        node (which should propagate to all its descendants). This makes the
        program ready to be run again from the start.
        """
        self._program_stack.clear()
        self._root.reset()
    
    def run(self, n=1):
        """Runs the program to completion `n` times.

        This method repeatedly calls :py:meth:`~.ProgramTree.tick` until the
        program reaches an :py:attr:`~.ProgramTree.Status.EXITED` state,
        performing this cycle `n` times.

        Parameters
        ----------
        n : int, optional
            The number of times to run the program to completion (default is 1).

        Raises
        ------
        ProgramTree.MissingAgentError
            If the program is not :py:meth:`~.ProgramTree.bound_to_agent`.
        ProgramTree.NodeMissingChildError
            If an incomplete node is encountered during execution (propagated from :py:meth:`~.ProgramTree.tick`).
        """
        for _ in range(n):    
            # run the program through to completion n times
            while self.tick():
                pass

    def running(self) -> bool:
        """Checks if the program is currently running.

        Returns
        -------
        bool
            :py:obj:`True` if the program's :py:attr:`~.ProgramTree.status` is
            :py:attr:`~.ProgramTree.Status.RUNNING`, :py:obj:`False` otherwise.
        """
        return self.status == ProgramTree.Status.RUNNING
    

    # - - Special methods - - 
    
    def node_iter(self, type: Type[ProgramNode]=None):
        """Returns an iterator over the nodes in the program tree.

        If a `type` is specified, the iterator will yield only nodes
        of that specific type. Otherwise, it iterates over all nodes
        in the tree. The internal node collections are updated via
        :py:meth:`~.ProgramTree._collect_nodes` before iteration if they are dirty.

        Parameters
        ----------
        type : type of ProgramNode, optional
            If provided, yields only nodes that are instances of this
            specific :py:class:`~.nodes.ProgramNode` subclass.

        Returns
        -------
        iterator
            An iterator that yields :py:class:`~.nodes.ProgramNode` objects.
        """
        if not type:
            return iter(self._nodes)
        else:
            return iter(self._nodes_by_type[type])
    
    def types_iter(self):
        """Returns an iterator over all unique node types present in the program tree.

        The internal node collections are updated via
        :py:meth:`~.ProgramTree._collect_nodes` before iteration if they are dirty.

        Returns
        -------
        iterator
            An iterator that yields :py:class:`type` objects, representing
            the classes of :py:class:`~.nodes.ProgramNode` instances found
            within the tree.
        """
        return iter(self._nodes_by_type)
    
    def copy(self) -> 'ProgramTree':
        """Creates a deep copy of the ProgramTree instance.

        The new :py:class:`~.ProgramTree` will have a deep copy of its
        :py:attr:`~.ProgramTree._root` node and consequently all its
        descendant nodes.

        Returns
        -------
        ProgramTree
            A new :py:class:`~.ProgramTree` instance that is a deep copy
            of the current program's structure.
        """
        program_cls = type(self)
        return program_cls(root = self._root.copy())
    
    def is_editable(self):
        return not self.running()
    
    def is_runnable(self):
        return True          # optional for use with addins or subclasses
    
    @property
    def size(self) -> int:
        """The total number of nodes in the program tree.

        The node collection is updated via :py:meth:`~.ProgramTree._collect_nodes`
        if it is dirty before returning the size.

        Returns
        -------
        int
            The count of all :py:class:`~.nodes.ProgramNode` instances, including the root.
        """
        return len(self._nodes)
    
    @property
    def nodes(self) -> Set['ProgramNode']:
        """A set containing all nodes in the program tree.

        This property provides access to a *copy* of the internal set of nodes
        for inspection or iteration. Modifications to the returned set
        will not affect the program tree's internal state.
        The internal node collection is updated via :py:meth:`~.ProgramTree._collect_nodes`
        if it is dirty before returning the set.

        Returns
        -------
        set of ProgramNode
            A set of all :py:class:`~.nodes.ProgramNode` objects comprising the tree.
        """
        return self._nodes.copy()
    
    @property
    def node_types(self) -> Set[Type['ProgramNode']]:
        """A set containing all unique node types present in the program tree.

        The internal node collections are updated via
        :py:meth:`~.ProgramTree._collect_nodes` if they are dirty before returning.

        Returns
        -------
        set of type of ProgramNode
            A set of :py:class:`type` objects, representing the unique classes
            of :py:class:`~.nodes.ProgramNode` instances found within the tree.
        """
        self._collect_nodes()
        return set(self._nodes_by_type)   
    
    @property
    def height(self) -> int:
        """The number of levels in the program tree.

        Calculated based on the :py:attr:`~.ProgramTree._max_child_depth`. 
        A tree with no nodes will a height of 0. A tree with only a root node 
        will have a height of 1. 

        Returns
        -------
        int
            The number of levels in the tree. Returns 0 if the tree is considered empty
            (e.g., if no nodes were collected for some reason).
        """
        return self._max_node_depth + 1
    
    @property
    def status(self):
        """The current execution status of the program.

        The status is dynamically determined based on whether the internal
        :py:attr:`~.ProgramTree._program_stack` is empty.

        Returns
        -------
        ProgramTree.Status
            Either :py:attr:`~.ProgramTree.Status.RUNNING` if the program stack is not empty,
            or :py:attr:`~.ProgramTree.Status.EXITED` if the stack is empty.
        """
        if len(self._program_stack) > 0:
            return ProgramTree.Status.RUNNING
        else:
            return ProgramTree.Status.EXITED
        
    @property
    def root(self):
        """The root node of the program tree.

        This property provides direct access to the program's
        :py:class:`~.nodes.basic_nodes.RootNode`, which serves as the
        entry point and anchor of the tree structure.

        Returns
        -------
        RootNode
            The root :py:class:`~.nodes.basic_nodes.RootNode` of the program.
        """
        return self._root
    
    # - - Magic Methods - - 
    
    def __str__(self):
        """Returns a string representation of the program tree.

        This typically delegates to the string representation of the
        :py:attr:`~.ProgramTree._root` node, providing a human-readable
        representation of the entire program structure.

        Returns
        -------
        str
            A string showing the structure of the program tree.
        """
        return str(self._root)

