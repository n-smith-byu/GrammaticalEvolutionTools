from ..programs.nodes.basic_nodes import TerminalNode
from ..programs.nodes import ProgramNode
from ..programs import ProgramTree
import random

from typing import Literal, Type, Tuple


CrossOverOption = Literal['same', 'any']

def pick_compatible_nodes_same_type_only(
    program1: ProgramTree, program2: ProgramTree, 
    exclude: list[Type[ProgramNode]] = None, 
    exclude_children_of_roots: bool = False
    ) -> Tuple[ProgramNode, ProgramNode]:
    
    incompatible_types = tuple(exclude or [])
    
    # Get all eligible node types from program1 (excluding root and incompatible types)
    eligible_types = set()
    possible_node1s = []
    
    for node_type in program1.types_iter():
        if not issubclass(node_type, incompatible_types) \
            and node_type in program2.node_types:
            eligible_types.add(node_type)
            possible_node1s.extend(program1.get_nodes_by_type(node_type))
    
    # if no matching types, return None, None
    if not eligible_types:
        return None, None
    
    # attempt to pick a matching type
    nodes_picked = False

    while not nodes_picked:
        possible_node1s = [node for node in possible_node1s \
                           if type(node) in eligible_types \
                              and node is not program1._root]
        
        if not possible_node1s:
            return None, None
    
        # choose a random node from program1
        node1: ProgramNode = random.choice(possible_node1s)
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


def pick_compatible_nodes_any_valid_replacement(program1: ProgramTree, program2: ProgramTree) -> Tuple[ProgramNode, ProgramNode]:
    picked = False
    incompatible_types = set([TerminalNode])
    possible_node1s = []
    while not picked:
        possible_node1s = [node for node in (possible_node1s or program1.node_iter()) \
                           if not isinstance(node, tuple(incompatible_types))]
        node1: ProgramNode = random.choice(possible_node1s)




def cross_over(program1: ProgramTree, program2: ProgramTree, 
               cross_over_option: CrossOverOption = 'same') -> list[ProgramTree]:

    # copy the nodes as to not modify the originals
    program1 = program1.copy()
    program2 = program2.copy()

    # select a pair of compatible nodes.
    # excludes terminals and prevents children of root nodes 
    # from being swapped with each other (root nodes excluded automatically)
    if cross_over_option == 'same':
        node1, node2 = pick_compatible_nodes_same_type_only(
            program1, program2, exclude=[TerminalNode],
            exclude_children_of_roots=True
        )
    elif cross_over_option == 'any':
        pick_compatible_nodes_any_valid_replacement(program1, program2)
    
    if not node1 or not node2:      # if no match was found
        return []

    # swap the nodes in each tree
    program1.replace_node(node1, node2.copy())
    program2.replace_node(node2, node1)

    # return a list of the newly created nodes
    return [program1, program2]
