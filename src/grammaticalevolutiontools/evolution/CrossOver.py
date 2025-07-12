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
    this is a docstring
    """

    possible_node1s = program1.nodes_iter()
    
    nodes_picked = False
    incompatible = exclude or []

    while not nodes_picked:
        incompatible_types = tuple(incompatible)

        possible_node1s = [
            node for node in possible_node1s if ( \
                node is not program1.root and \
                not issubclass(type(node), incompatible_types)
            )
        ]
        
        if len(possible_node1s) == 0:
            return None, None
        node1 = random.choice(possible_node1s)
        node1_is_not_child_of_root = node1 not in program1.root._children

        possible_node2s = [
            node for node in program2.nodes_iter() if ( \
                node is not program2.root and \
                (allow_children_of_root or \
                    node1_is_not_child_of_root or \
                    node not in program2.root._children) and \
                type(node) == type(node1)
            )
        ]
        if len(possible_node2s) == 0:           # if no compatible node2s, pick a different node1
            incompatible.append(type(node1))
            continue

        node2 = random.choice(possible_node2s)
        nodes_picked = True

    return node1, node2


def cross_over(program1: ProgramTree, program2: ProgramTree) -> list[ProgramTree]:
    """
    this is a docstring
    """
    program1 = program1.copy()
    program2 = program2.copy()
    node1, node2 = pick_compatible_nodes(
        program1, program2, exclude=[TerminalNode],
        allow_children_of_root=False
    )
    
    if not node1 or not node2:      # if for some reason nodes weren't compatible
        return []

    program1.replace_node(node1, node2.copy())
    program2.replace_node(node2, node1.copy())

    return [program1, program2]
