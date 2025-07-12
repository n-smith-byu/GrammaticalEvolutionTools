from ..programs.nodes.basic_nodes import TerminalNode
from ..programs.nodes import ProgramNode
from ..programs import ProgramTree
import random

from typing import Type, Tuple


def pick_compatible_nodes(program1:ProgramTree, program2:ProgramTree, 
        exclude: list[Type[ProgramNode]] = None, 
        allow_children_of_root: bool = True
        ) -> Tuple[ProgramNode, ProgramNode]:
    """
    Pick two compatible nodes from different program trees that can be swapped.
    
    Parameters
    ----------
    program1 : ProgramTree
        The first program tree to select a node from.
    program2 : ProgramTree
        The second program tree to select a node from.
    exclude : list of Type, optional
        List of node types (and their subclasses) to exclude from selection.
        Default is None (no exclusions beyond root nodes).
    allow_children_of_root : bool, optional
        If True, prevents selecting both nodes as direct children of their
        respective root nodes. Default is True.
    
    Returns
    -------
    tuple of (ProgramNode, ProgramNode) or (None, None)
        A tuple containing two compatible nodes that can be swapped, or
        (None, None) if no compatible pair exists.
    
    Notes
    -----
    Root nodes are always excluded from selection. Terminal nodes are
    typically excluded as swapping them provides no benefit.
    """

    possible_node1s = program1.nodes_iter()
    
    nodes_picked = False
    incompatible = exclude or []

    while not nodes_picked:
        incompatible_types = tuple(incompatible) 

        # filter remaining possible nodes from program1 to exclude 
        # any new incompatible types
        possible_node1s = [
            node for node in possible_node1s if ( \
                node is not program1.root and \
                not issubclass(type(node), incompatible_types)
            )
        ]
        
        if len(possible_node1s) == 0:       # if no remaining possible nodes
            return None, None
        
        # choose a random node from program1 possible nodes
        node1 = random.choice(possible_node1s)
        node1_is_not_child_of_root = node1 not in program1.root._children

        # Create a list of eligible nodes from program2
        # optionally exclude children of root if node1 
        # is also a child of program1 root
        possible_node2s = [
            node for node in program2.nodes_iter() if ( \
                node is not program2.root and \
                (allow_children_of_root or \
                    node1_is_not_child_of_root or \
                    node not in program2.root._children) and \
                type(node) == type(node1)
            )
        ]
        if len(possible_node2s) == 0:           # if no compatible nodes from program2, 
            incompatible.append(type(node1))    # pick a different node1
            continue

        # randomly choose a node from the possible program2 nodes
        node2 = random.choice(possible_node2s)
        nodes_picked = True

    # return a tuplw with the matching pair
    return node1, node2


def cross_over(program1: ProgramTree, program2: ProgramTree) -> list[ProgramTree]:
    """
    Perform crossover between two program trees by swapping compatible subtrees.
    
    Parameters
    ----------
    program1 : ProgramTree
        The first parent program tree.
    program2 : ProgramTree
        The second parent program tree.
    
    Returns
    -------
    list of ProgramTree
        A list containing two new program trees with crossed-over subtrees.
        Returns an empty list if no compatible nodes can be found for crossover.
    
    Notes
    -----
    This function:
    1. Creates deep copies of both input programs (originals are not modified)
    2. Finds compatible nodes that can be swapped using pick_compatible_nodes
    3. Swaps the selected subtrees between the copies
    4. Returns the two new crossed-over programs
    
    Terminal nodes are excluded from crossover as swapping them provides no
    structural benefit. Root nodes and pairs of root children are also excluded
    to ensure meaningful genetic recombination.
    """
    # copy the nodes as to not modify the originals
    program1 = program1.copy()
    program2 = program2.copy()

    # select a pair of compatible nodes.
    # excludes terminals and prevents children of root nodes 
    # from being swapped with each other (root nodes excluded automatically)
    node1, node2 = pick_compatible_nodes(
        program1, program2, exclude=[TerminalNode],
        allow_children_of_root=False
    )
    
    if not node1 or not node2:      # if no match was found
        return []

    # swap the nodes in each tree
    program1.replace_node(node1, node2.copy())
    program2.replace_node(node2, node1.copy())

    # return a list of the newly created nodes
    return [program1, program2]
