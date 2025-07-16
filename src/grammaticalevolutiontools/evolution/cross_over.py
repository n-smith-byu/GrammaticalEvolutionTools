from ..programs.nodes.basic_nodes import TerminalNode
from ..programs.nodes import ProgramNode
from ..programs import ProgramTree
import random

from typing import Type, Tuple


def pick_compatible_nodes(program1: ProgramTree, program2: ProgramTree, 
        exclude: list[Type[ProgramNode]] = None, 
        exclude_children_of_roots: bool = False
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
    exclude_children_of_roots : bool, optional
        If True, prevents selecting both nodes as direct children of their
        respective root nodes. Default is False.
    
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
    
    incompatible_types = tuple(exclude or [])
    
    # Get all eligible node types from program1 (excluding root and incompatible types)
    eligible_types = set()
    program2_types = program2.node_types
    
    for node_type in program1.types_iter():
        if not issubclass(node_type, incompatible_types) \
            and node_type in program2_types:
            eligible_types.add(node_type)
    
    # if no matching types, return None, None
    if not eligible_types:
        return None, None
    
    # attempt to pick a matching type
    nodes_picked = False
    possible_node1s = None

    while not nodes_picked:
        possible_node1s = [node for node in (possible_node1s or program1.node_iter()) \
                           if type(node) in eligible_types \
                            and node is not program1._root]
        
        if not possible_node1s:
            return None, None
    
        # choose a random node from program1
        node1 = random.choice(possible_node1s)
        node1_child_of_root = node1._parent is program1.root

        # get a possible list of nodes from program2
        possible_node2s = [node for node in program2.node_iter(type=type(node1)) \
                           if type(node) == type(node1) \
                            and node is not program2._root \
                            and (not exclude_children_of_roots \
                                 or not node1_child_of_root \
                                 or node._parent is not program2.root) \
                            ]
        
        # if no matches, remove the type and try again
        if not possible_node2s:
            eligible_types.remove(type(node1))
            continue

        # once a compatible type is found, choose node2
        node2 = random.choice(possible_node2s)
        
        nodes_picked = True

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
        exclude_children_of_roots=True
    )
    
    if not node1 or not node2:      # if no match was found
        return []

    # swap the nodes in each tree
    program1.replace_node(node1, node2.copy())
    program2.replace_node(node2, node1.copy())

    # return a list of the newly created nodes
    return [program1, program2]
