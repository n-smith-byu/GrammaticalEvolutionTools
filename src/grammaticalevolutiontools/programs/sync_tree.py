from .nodes.basic_nodes import NonTerminalNode, RootNode, ExecutableNode
from .nodes.sync_node import SyncProgramNode
from .base import ProgramTree

from enum import IntEnum

from typing import Type, Union


class SyncProgramTree(ProgramTree):
    """Represents a program as a hierarchical tree structure of interconnected nodes to be run synchronously.

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

    # - - Program Status - -

    class Status(IntEnum):
        """An enumeration representing the execution status of a program."""
        EXITED = 0
        """The program has finished execution."""
        RUNNING = 1
        """The program is currently executing."""

    # - - Assertions - - 

    def _assert_root_valid(self):
        if self._root is None:
            raise ValueError(
                "`root` cannot be None. Must be either an instance or " \
                "subclass of RootNode"
            )
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

    def __init__(self, root: Union[RootNode, Type[RootNode]],
                 autofill=True):
        """Initializes a SyncProgramTree instance with a root node and an optional agent.

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
        super().__init__(root, autofill=autofill)

        self._root: 'RootNode'
        self._nodes: set['SyncProgramNode']
        self._nodes_by_type: dict[type, set['SyncProgramNode']]

        self._program_stack: list['SyncProgramNode'] = []
        self._status: SyncProgramTree.Status = SyncProgramTree.Status.EXITED

    def tick(self):
        """Executes a single step of the program's execution.

        This method advances the program by one execution step.
        If the program is in an :py:attr:`~.ProgramTree.Status.EXITED` state,
        it will start execution from the :py:attr:`~.ProgramTree._root` node.
        It processes one executable node or advances the execution stack.

        Returns
        -------
        SyncProgramTree.Status
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
        if self.status == SyncProgramTree.Status.EXITED:
            self._program_stack.append(self._root)
            self._root.reset()

        while len(self._program_stack) > 0:
            # get the next node to run. 
            curr_node = self._program_stack[-1]
            if curr_node.num_children < curr_node.max_num_children:
                raise ProgramTree.NodeMissingChildError(
                    "Expected tree to be completely filled out, but "
                    "encountered node with missing children."
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
                    # if no more children nodes to run, pop the 
                    # current node off the stack
                    self._program_stack.pop(-1)
                else:
                    self._program_stack.append(next_child)
                
        if len(self._program_stack) > 0:
            self._status = SyncProgramTree.Status.RUNNING
        else:
            self._status = SyncProgramTree.Status.EXITED
        
        return self.status

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

    def kill(self):
        """Immediately stops the execution of the program and resets its state.

        This method clears the internal :py:attr:`~.ProgramTree._program_stack`
        and calls :py:meth:`~.nodes.ProgramNode.reset` on the :py:attr:`~.ProgramTree._root`
        node (which should propagate to all its descendants). This makes the
        program ready to be run again from the start.
        """
        self._program_stack.clear()
        self._root.reset()

    def running(self) -> bool:
        """Checks if the program is currently running.

        Returns
        -------
        bool
            :py:obj:`True` if the program's :py:attr:`~.ProgramTree.status` is
            :py:attr:`~.ProgramTree.Status.RUNNING`, :py:obj:`False` otherwise.
        """
        return self.status == SyncProgramTree.Status.RUNNING
    
    @property
    def status(self) -> SyncProgramTree.Status:
        """The current execution status of the program.

        The status is dynamically determined based on whether the internal
        :py:attr:`~.ProgramTree._program_stack` is empty.

        Returns
        -------
        SyncProgramTree.Status
            Either :py:attr:`~.SyncProgramTree.Status.RUNNING` if the program stack is not empty,
            or :py:attr:`~.SyncProgramTree.Status.EXITED` if the stack is empty.
        """
        return super().status
    