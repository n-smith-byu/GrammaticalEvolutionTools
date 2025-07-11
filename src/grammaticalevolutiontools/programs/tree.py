from .nodes.basic_nodes import NonTerminalNode, RootNode, ExecutableNode
from .nodes import ProgramNode

from enum import IntEnum
import random

from typing import Type, Union, Tuple, Set, TYPE_CHECKING

if TYPE_CHECKING:
    
    from ..agents import Agent
    
class ProgramTree:
    """Represents a runnable program composed of interconnected nodes.

    This class manages the structure and execution flow of a program.
    It provides capabilities for program generation, execution, and
    can be optionally attached to an external agent for interaction.
    """

    RANDOM_REPLACEMENT = 'Random'
    
    class Status(IntEnum):
        """An enumeration representing the execution status of a program."""
        EXITED = 0
        """The program has finished execution."""
        RUNNING = 1
        """The program is currently executing."""

    class ProgramInProgressError(RuntimeError):
        """Exception raised when an operation is attempted on a program that is currently running."""
        pass

    class NodeMissingChildError(RuntimeError):
        """Exception raised when a program encounters a node that is missing a child.

        This typically indicates an incomplete program structure.
        """
        pass

    class MissingAgentError(RuntimeError):
        """Exception raised when attempting to run a program not attached to an an agent."""
        pass

    class BoundToAgentError(RuntimeError):
        """Exception raised for operations requiring the program to be unbound from an agent when it is not."""
        pass

    # - - Initialization - - 

    def __init__(self, root: 'RootNode', agent:'Agent' = None):
        """Initializes a ProgramTree instance.

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
        typically not intended for direct external access. These include:

        * `_root` (:py:class:`~.nodes.basic_nodes.RootNode`): The root node of the tree.
        * `_nodes` (:py:class:`set` of :py:class:`~.nodes.ProgramNode`): A set of all nodes in the tree for quick lookup.
        * `_depth` (:py:class:`int` or :py:class:`None`): The maximum depth of the tree, calculated lazily.
        * `_agent` (:py:class:`~.agents.Agent` or :py:class:`None`): The agent instance, if attached.
        * `_program_stack` (:py:class:`list` of :py:class:`~.nodes.ProgramNode`): Used internally to manage program execution flow.

        The :py:meth:`~.nodes.ProgramNode.set_tree` method (called on the root) establishes a bidirectional link,
        and :py:meth:`~.ProgramTree._fill_out_program` is an internal method
        to build the initial tree structure based on the root.
        """
        self._root: 'RootNode' = root
        self._nodes: set['ProgramNode'] = set()
        self._depth = None       # depth calculated lazily, only when needed.
        self._agent = agent
        self._program_stack: list['ProgramNode'] = []

        self._root._set_program(self)
        self._fill_out_program()

    def _set_agent(self, agent: 'Agent'):
        """Sets the agent instance to which this program is bound.

        This method should typically only be called by an instance of
        :py:class:`~.agents.Agent` itself to establish the binding.

        Parameters
        ----------
        agent : Agent
            The agent instance to bind the program to.
        """
        self._agent = agent

    def _collect_nodes(self) -> set:
        """Collects all nodes in the program tree and updates the internal `_nodes` set.

        This method typically starts from the :py:attr:`~.ProgramTree._root` and
        traverses the tree to discover all connected nodes using
        :py:meth:`~.nodes.ProgramNode.collect_descendants`.

        Returns
        -------
        set of ProgramNode
            A set containing all :py:class:`~.nodes.ProgramNode` instances within the tree.
        """
        self._nodes = self._root.collect_descendants()

    def _fill_out_program(self):
        """Recursively fills out the program tree by adding random children to incomplete nodes.

        This method ensures that all non-terminal nodes have their required number
        of children, creating a complete and runnable program structure. It uses
        a breadth-first-like traversal starting from existing incomplete nodes.

        Process:
        1. Calls :py:meth:`~.ProgramTree._collect_nodes` to get all current nodes.

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
                v. Adds the new child to the `_nodes` set.
                vi. Attaches the child to `curr_node` using :py:meth:`~.nodes.ProgramNode.add_child`.
        """
        self._collect_nodes()
        queue = [node for node in self._nodes if node.num_children < node.max_num_children]
        
        while len(queue) > 0:
            curr_node: 'ProgramNode' = queue.pop(0)
            while curr_node.num_children < curr_node.max_num_children:
                index = curr_node.num_children
                possible_children, probs = curr_node.get_possible_children_and_probs(index)
                child_node_class = random.choices(possible_children, probs, k=1)[0]
                child_node = child_node_class()

                queue.append(child_node)
                self._nodes.add(child_node)
                curr_node.add_child(child_node)


    # - - User Methods - - 

    def get_parent_of_node(self, node: 'ProgramNode') -> Tuple['ProgramNode', int]:
        """Retrieves the parent node and the child index of a given node.

        Parameters
        ----------
        node : ProgramNode
            The node for which to find the parent.

        Returns
        -------
        tuple[ProgramNode, int]
            A tuple containing:
            - The parent :py:class:`~.nodes.ProgramNode` of the given node.
            - The integer index at which the node is a child of its parent.

        Raises
        ------
        ValueError
            If the provided node does not exist within this program tree.
        """
        if node not in self.nodes:
            raise ValueError('Node does not exist in tree')
        
        return node.get_parent()

    def replace_node(self, node, new_node: Union['ProgramNode', str] \
                     = RANDOM_REPLACEMENT):
        """Replaces a specific node in the tree with another node or a randomly generated branch.

        If `new_node` is set to :py:attr:`~.ProgramTree.RANDOM_REPLACEMENT`, the
        node will be replaced randomly, and a new complete branch will be generated
        from that point.

        Parameters
        ----------
        node : ProgramNode
            The existing node in the tree to be replaced.
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
            If the program is currently bound to an agent. Modifications are disallowed.
        ProgramTree.ProgramInProgressError
            If the program is currently :py:attr:`~.ProgramTree.running`. Modifications are disallowed.
        """
        if node is self._root:
            raise ValueError(
                "Cannot Replace the Root Node in Tree. " 
                "Try replacing a child node instead."
            )
        if self.bound_to_agent():
            raise ProgramTree.BoundToAgentError(
                "Cannot modify a program after it is bound to an agent."
            )
        if self.running():
            raise ProgramTree.ProgramInProgressError(
                "Cannot modify program while it is running. " \
                "Please kill program or run it to completion first."
            )

        # get the parent of the node to replace and the node it is at
        parent_node, index = self.get_parent_of_node(node)
        
        # if no replacement node specified, replace randomly
        if new_node is ProgramTree.RANDOM_REPLACEMENT:
            old = parent_node.pop_child(index)     # will get randomly replaced when tree is filled out
        else:
            old = parent_node.replace_child(index, new_node)

        self._fill_out_program()        # ensure program is complete


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
        # can't run unless bound to an agent
        if not self.bound_to_agent():
            raise ProgramTree.MissingAgentError('Cannot run program when not bound to an agent.')
        
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

        This clears the internal program stack and resets all nodes to their
        initial state, making the program ready to be run again from the start.
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
            True if the program's :py:attr:`~.ProgramTree.status` is
            :py:attr:`~.ProgramTree.Status.RUNNING`, False otherwise.
        """
        return self.status == ProgramTree.Status.RUNNING
        
    def bound_to_agent(self) -> bool:
        """Checks if the program is currently bound to an agent.

        Returns
        -------
        bool
            True if an :py:class:`~.agents.Agent` instance is attached to the program,
            False otherwise.
        """
        return self.agent is not None
        
    def copy(self) -> 'ProgramTree':
        """Creates a deep copy of the ProgramTree instance.

        The new ProgramTree will have a deep copy of its
        :py:attr:`~.ProgramTree._root` node and consequently all its
        descendant nodes. The `_agent` attribute is NOT copied (it will be None).

        Returns
        -------
        ProgramTree
            A new :py:class:`~.ProgramTree` instance that is a deep copy
            of the current program's structure.
        """
        return ProgramTree(root = self._root.copy())
        
    @property
    def agent(self) -> 'Agent':
        """The agent instance to which this program is currently attached.

        Returns
        -------
        Agent or None
            The attached agent, or None if no agent is currently bound.
        """
        return self._agent
    
    @property
    def size(self) -> int:
        """The total number of nodes in the program tree.

        Returns
        -------
        int
            The count of all :py:class:`~.nodes.ProgramNode` instances, including the root.
        """
        return len(self._nodes)
    
    @property
    def nodes(self) -> Set['ProgramNode']:
        """A set containing all nodes in the program tree.

        This property provides access to the internal set of nodes
        for inspection or iteration.

        Returns
        -------
        set of ProgramNode
            A set of all :py:class:`~.nodes.ProgramNode` objects comprising the tree.
        """
        return set(node for node in self._nodes)
    
    @property
    def depth(self) -> int:
        """The maximum depth of the program tree.

        The depth is calculated lazily (only when first accessed) and cached.
        The depth of a tree with only a root node is 0.

        Returns
        -------
        int
            The maximum depth of any node within the tree, where the root is at depth 0.
        """
        if self._depth is None:
            if len(self._nodes) == 0:
                self._depth = 0
            else:
                self._depth = max([node._depth for node in self._nodes])
        
        return self._depth
    
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

