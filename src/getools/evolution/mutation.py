from ..programs import ProgramTree
import random

def mutate_terminals(program:ProgramTree, num_mutations, terminal_types:list[type]):
    possible_nodes = [node for node in program.nodes if type(node) \
                        in terminal_types]
    
    num_mutations = min(num_mutations, len(possible_nodes))
    for k in range(num_mutations):
        node = random.choice(possible_nodes)
        if node in program.nodes:
            program.replace_node(node)
            possible_nodes.remove(node)
        else:
            print('error')

def replace_random_branch(program: ProgramTree, possible_node_types:list[type]):
    possible_nodes = [n for n in program.nodes if type(n) in possible_node_types]
    node = random.choice(possible_nodes)
    program.replace_node(node)          # randomly replaces node by default

