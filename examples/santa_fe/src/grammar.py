from grammaticalevolutiontools.programs.nodes import \
    basic_nodes, logic_nodes, factor_nodes
from grammaticalevolutiontools.grammars import \
    Grammar, as_grammar_node

from .santafe_agent import SantaFeAgent

from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from grammaticalevolutiontools.agents import AgentProgramTree

_MIN_SIGHT_RANGE = 1
_MAX_SIGHT_RANGE = 1

#############################################################################
# This is an example implementation of a Grammar for the SantaFe Problem.
# 
# See ../resources/grammar.txt to see the grammar this is based on. 
#############################################################################


with Grammar(target_agent_type=SantaFeAgent) as SantaFeGrammar:
    # CodeNode will be the root node for our SantaFe Grammar, so we inherit 
    # from the base RootNode
    @as_grammar_node 
    class CodeNode(basic_nodes.RootNode):
        def _base_node_init(self):
            super()._base_node_init(token="<Code>",
                                    possible_children=[
                                        'ProgsNode'
                                    ])
            
        def _custom_init(self):
            return super()._custom_init()

    # A Node that can be replaced with any other type of node (except CodeNode)
    @as_grammar_node
    class ProgsNode(logic_nodes.SequentialNode):
        def _base_node_init(self):
            super()._base_node_init(
                token="<Progs>",
                label=None,
                num_children=1,
                possible_children=[
                    'FoodConditionNode',
                    'Progs2Node', 
                    'Progs3Node',
                    'OperationNode'
                ])
            
            self._set_child_probs(0, [0.59,0.2,0.2,0.01])

        def _custom_init(self):
            return super()._custom_init()

        def get_probs(self, index):
            # Increase probability of choosing OperationNode as the
            # tree gets deeper. Prevents tree explosion. 
            SeqNode = logic_nodes.SequentialNode
            probs = SeqNode.get_probs(self, index)   # cannot use super()
            probs[-1] += max(0, self._depth) / 3
            probs = probs / np.sum(probs)

            return probs
        
    # Progs2Node is a node that runs two ProgsNodes sequentially
    @as_grammar_node
    class Progs2Node(logic_nodes.SequentialNode):
        def _base_node_init(self):
            super()._base_node_init(token="<Progs2>",
                                    label='Progs2',
                                    num_children=2,
                                    possible_children=['ProgsNode'])
        def _custom_init(self):
            return super()._custom_init()

    # Progs3Node is a node that runs three ProgsNodes sequentially
    @as_grammar_node
    class Progs3Node(logic_nodes.SequentialNode):
        def _base_node_init(self):
            super()._base_node_init(token="<Progs3>",
                                    label='Progs3',
                                    num_children=3,
                                    possible_children=['ProgsNode'])
        def _custom_init(self):
            return super()._custom_init()
        

    # The FoodConditionNode checks if food is within n spaces directly 
    # in front of the agent and runs its first child if true, its 
    # second if false
    @as_grammar_node
    class FoodConditionNode(logic_nodes.ConditionNode):
        def _base_node_init(self):
            super()._base_node_init(
                token='<FoodCondition>',
                label='if_food_ahead',
                possible_children_true=['ProgsNode'],
                possible_children_false=['ProgsNode'],
                factor_possible_vals=[
                    ['RandDistNode']
                ]
            )
            
        def _custom_init(self):
            return super()._custom_init(
                factor_names=['dist']
            )
        
        def condition(self) -> bool:
            self._program: AgentProgramTree
            agent: SantaFeAgent = self._program.agent
            num_spaces: int = self._get_factor('dist').value

            return agent.food_within(num_spaces)
        
    @as_grammar_node
    class OperationNode(logic_nodes.SequentialNode):
        def _base_node_init(self):
            super()._base_node_init(
                token='<Op>',
                label=None,
                num_children=1,
                possible_children={
                    0:['TurnLeft', 
                       'TurnRight', 
                       'TurnAround',
                       'MoveForward']
                    }
                )
            self._set_child_probs(0, [0.2, 0.2, 0.2, 0.4])
            
        def _custom_init(self):
            return super()._custom_init()
        
        def __str__(self):
            return str(self.children[0])
            

    # ---- Terminal Nodes ----

    # -- Movement -- 

    @as_grammar_node
    class TurnLeft(basic_nodes.ExecutableNode):
        def _base_node_init(self):
            super()._base_node_init(token='TurnLeft')

        def _custom_init(self):
            return super()._custom_init()

        def execute(self):
            self._program: AgentProgramTree
            agent: SantaFeAgent = self._program.agent
            agent.turn_left()
        
    @as_grammar_node
    class TurnRight(basic_nodes.ExecutableNode):
        def _base_node_init(self):
            super()._base_node_init(token='TurnRight')

        def _custom_init(self):
            return super()._custom_init()

        def execute(self):
            self._program: AgentProgramTree
            agent: SantaFeAgent = self._program.agent
            agent.turn_right()

    @as_grammar_node
    class TurnAround(basic_nodes.ExecutableNode):
        def _base_node_init(self):
            super()._base_node_init(token='TurnAround')

        def _custom_init(self):
            return super()._custom_init()

        def execute(self):
            self._program: AgentProgramTree
            agent: SantaFeAgent = self._program.agent
            agent.turn_around()
        
    @as_grammar_node
    class MoveForward(basic_nodes.ExecutableNode):
        def _base_node_init(self):
            super()._base_node_init(token='MoveForward')

        def _custom_init(self):
            return super()._custom_init()

        def execute(self):
            self._program: AgentProgramTree
            agent: SantaFeAgent = self._program.agent
            agent.move_forward()

    # -- Numbers -- 

    @as_grammar_node
    class RandDistNode(factor_nodes.RandIntegerNode):
        def _base_node_init(self):
            super()._base_node_init() 

        def _custom_init(self):
            return super()._custom_init(_MIN_SIGHT_RANGE, _MAX_SIGHT_RANGE)
        
        def copy(self):
            dup = self._default_copy_method()
            dup._val = self._val        # copy over randomized val

            return dup
