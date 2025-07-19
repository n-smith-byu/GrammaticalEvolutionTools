from grammaticalevolutiontools.programs.nodes import \
    basic_nodes, logic_nodes, factor_nodes
from grammaticalevolutiontools.grammars import \
    Grammar, as_grammar_node
from ..santafe_agent import SantaFeAgent

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from grammaticalevolutiontools.programs import AgentProgramTree

_MIN_SIGHT_RANGE = 1
_MAX_SIGHT_RANGE = 3

#############################################################################
# Welcome to an example implementation of a Grammar for the SantaFe Problem.
# 
# See /resources/grammar.txt to see the grammar this is based on. 
#############################################################################

"""
General Notes and Reminders:

 1) The idea is that any concrete node class (e.g. member of a grammar) should be fully implemented.
    This means you should be able to call MyNode() with no arguments and have it successfully create your node.
 2) **Every concrete node class must implement the copy function. If you have correctly implemented the node
    as described above, then you can just return super()._default_copy_method(). It will create a new instance of your node class 
    using type(self)() and then copy the children over. Otherwise, if you have additional arguments you need to pass in,
    you can call super().copy(kwargs={myarg1: val1, ...})

 3) In Non-Terminal Nodes, including most pre-defined derivative classes (e.g. SequentialNode, ConditionNode, etc.), 
    the 'label' parameter can be defined to have your node print out as "my_label(<Child1>,<Child2>,...)".
    If left empty, the node will not print itself in any way, and instead will just print its children. 
    (See RootNode and FoodConditionNode) for examples of each of these behaviors). 
 4) The 'token' parameter must be passed into the __init__ function of every base node class in the 
    grammaticalevolutiontools package. This parameter defines how a node is printed when it has no children 
    (e.g. Terminal Nodes or a Non-Terminal Node that has not had its children added yet.). 
    Convention is to use '<MyToken>' for non-terminal nodes, including the <> braces, and 'MyBehavior' for 
    terminal nodes, with no braces. 

 5) You can define custom probabilities for each possible child node to be chosen by calling 
    self._set_child_probs(child_index, list[probs_for_each_possible_child]). By default, they are 
    chosen uniformly. 
 6) You can also cause the probability of selecting each child node to be determined dynamically by overloading the 
    get_possible_children_and_probs(self, index) function. 
    (See ProgsNode for an example of how to do this.)

7) Each node, when included in a ProgramTree, will have access to its tree using 'self.tree'. 
   Each program tree must be linked to a specific agent, so Terminal nodes can access and interact with
   their agent by using 'self.tree.agent'. 

"""


with Grammar(min_compliant_agent=SantaFeAgent) as SantaFeGrammar:
    # CodeNode will be the root node for our SantaFe Grammar, so we inherit from the base RootNode
    # In our Grammar, <Code> always goes to <Progs>, so there is only one possible child.
    @as_grammar_node 
    class CodeNode(basic_nodes.RootNode):
        def _base_node_init(self):
            super()._base_node_init(token="<Code>",
                                    possible_children=['ProgsNode'])
            
        def _custom_init(self):
            return super()._custom_init()

    # ProgsNode is a NonTerminal node that has a single child
    #  - We inherit from SequentialNode since the logic for verifying and running child nodes is already there. 
    #  - We pass in 1 for the number of children into SequentialNode.__init__()
    #  - <Progs> can be replaces by <Progs2>, <Progs3>, <Op>, if_food_ahead() etc., so each of these is a possible_child
    #  - Because there is only one child, we can just pass in a list of possible children. SequentialNodes assume every index
    #    has the same set of possible children unless you specify different lists for each index using a dict[int, list[Type]]. 
    #  - We want the probability of choosing <Op> to increase the deeper we get into our tree in order to prevent the 
    #    size of the tree from exploding expentially. Therefore we overload get_possible_children_and_probs to make the 
    #    the probability of <Op> increase with depth. 
    @as_grammar_node
    class ProgsNode(logic_nodes.SequentialNode):
        def _base_node_init(self):
            super()._base_node_init(
                token="<Progs>",
                label=None,
                num_children=1,
                possible_children=[
                    'FoodConditionNode',
                    'WallConditionNode',
                    'Progs2Node', 
                    'Progs3Node',
                    'OperationNode'
                ])
            
            self._set_child_probs(0, [0.35,0.34,0.2,0.2,0.01])

        def _custom_init(self):
            return super()._custom_init()

        def get_probs(self, index):
            SeqNode = logic_nodes.SequentialNode
            probs = SeqNode.get_probs(self, index)   # cannot use super()
            probs[-1] += max(0, self._depth) / 3
            probs = probs / np.sum(probs)

            return probs
        
    # Progs2Node is a node that runs two ProgsNodes sequentially
    # - We inherit from SequentialNode and set num_children = 2
    # - Similar to Progs, since we will draw from the same list of possible children for each
    #   child node, we can simply pass in a list of possible_children and it will be used for 
    #   every index. However, if we wanted to define different possible Nodes for child1 vs. child2,
    #   we could instead pass in a dict.
    # - since we are using the 'label' param and setting it to "progs2", this when printed this node will
    #   print as "progs2(<Child1>,<Child2>)"
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
    # - See Definition for Progs2Node
    @as_grammar_node
    class Progs3Node(logic_nodes.SequentialNode):
        def _base_node_init(self):
            super()._base_node_init(token="<Progs3>",
                                    label='Progs3',
                                    num_children=3,
                                    possible_children=['ProgsNode'])
        def _custom_init(self):
            return super()._custom_init()
        

    # The FoodConditionNode checks if food is within n spaces, directly in front of the agent and runs its 
    # first child if True, its second child if False. 
    # - The logic for determining which child to run is already implemented in the ConditionNode base class, 
    #   so we inherit from ConditionNode.
    # - We define the condition to check by implementing the 'condition' function
    #   Notice that we can access the agent we need to check the condition for by using 'self.tree.agent'. 
    #   Since this grammar is designed for SantaFeAgents specifically, we know the agent will have a method
    #   called food_within() that will tell us if there is any food within some number of spaces
    # - The n or num_spaces parameter is determined programmaticaly using a third child of our condition node known as a factor. 
    #   Factors are parameters for your condition you want to be determined dynamically by nodes in your tree, rather than hard-coded in. 
    # - We pass in num_factors=1 to tell our Condition node we want it to have one extra child node representing our parameter n. 
    #   The 'possible_factor_values' parameter takes a list of lists, where possible_factor_values[i] is a list of 
    #   possible_children for our ith factor. 
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


    # WallConditionNode checks if a wall is 
    @as_grammar_node
    class WallConditionNode(logic_nodes.ConditionNode):
        def _base_node_init(self):
            super()._base_node_init(
                token='<WallCondition>',
                label='if_wall_ahead',
                possible_children_true=['ProgsNode'],
                possible_children_false=['ProgsNode'],
                factor_possible_vals=[
                    ['RandDistNode']
                ]
            )

        def _custom_init(self):
            return super()._custom_init(
                factor_names=['dist'])
            
        def condition(self):
            self._program: AgentProgramTree
            agent: SantaFeAgent = self._program.agent
            num_spaces: int = self._get_factor('dist').value

            return agent.wall_within(num_spaces)
        
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
                       'MoveForward']
                    }
                )
            
        def _custom_init(self):
            return super()._custom_init()
        
        def __str__(self):
            return str(self.children[0])
            

    # ---- Terminal Nodes ----

    # -- Movement -- 

    @as_grammar_node
    class TurnLeft(basic_nodes.ExecutableNode):
        def _base_node_init(self):
            super()._base_node_init(token='Left')

        def _custom_init(self):
            return super()._custom_init()

        def execute(self):
            self._program: AgentProgramTree
            agent: SantaFeAgent = self._program.agent
            agent.turn_left()
        
    @as_grammar_node
    class TurnRight(basic_nodes.ExecutableNode):
        def _base_node_init(self):
            super()._base_node_init(token='Right')

        def _custom_init(self):
            return super()._custom_init()

        def execute(self):
            self._program: AgentProgramTree
            agent: SantaFeAgent = self._program.agent
            agent.turn_right()
        
    @as_grammar_node
    class MoveForward(basic_nodes.ExecutableNode):
        def _base_node_init(self):
            super()._base_node_init(token='Move')

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
