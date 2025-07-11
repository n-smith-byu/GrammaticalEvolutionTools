from ..agents import Agent
from ..programs.nodes.basic_nodes import RootNode, TerminalNode
from ..programs import ProgramTree
import random


def pick_compatible_nodes(program1:ProgramTree, program2:ProgramTree):

    possible_node1s = iter(program1.nodes)
    
    nodes_picked = False
    incompatible_types = []

    while not nodes_picked:

        possible_node1s = [
            node for node in possible_node1s if ( \
                not isinstance(node, RootNode) \
                and not isinstance(node, TerminalNode) \
                and type(node) not in incompatible_types
            )
        ]
        
        if len(possible_node1s) == 0:
            return None, None
        node1 = random.choice(possible_node1s)

        possible_node2s = [node for node in program2.nodes if type(node) == type(node1)]
        if len(possible_node2s) == 0:           # if no compatible node2s, pick a different node1
            incompatible_types.append(type(node1))
            continue

        node2 = random.choice(possible_node2s)
        nodes_picked = True

    return node1, node2


def cross_over(program1: ProgramTree, program2: ProgramTree):

    program1_node, program2_node = pick_compatible_nodes(program1, program2)
    if program1_node is None or program2_node is None:      # if for some reason nodes weren't compatible
        return []

    program1.replace_node(program1_node, program2_node)
    program2.replace_node(program2_node, program1_node)

    new_child1 = Agent(program1)
    new_child2 = Agent(program2)

    return [new_child1, new_child2]
