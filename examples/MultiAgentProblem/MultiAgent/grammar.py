from GrammaticalEvolutionTools.Programs.CustomNodes.BasicNodes import NonTerminalNode, TerminalNode
import numpy as np
from abc import abstractmethod

class CodeNode(NonTerminalNode):
    def __init__(self):
        super(CodeNode, self).__init__(token="<Code>",
                                       num_children=1,
                                       possible_children={0: [ProgsNode]})
        

class ProgsNode(NonTerminalNode):
    def __init__(self):
        super(ProgsNode, self).__init__(token="<Progs>",
                                       num_children=1,
                                       possible_children={0: [FoodConditionNode,
                                                              WallConditionNode,
                                                              Progs2Node, 
                                                              Progs3Node,
                                                              OperationNode]})
        
        self._child_probs[0] = [0.35,0.34,0.2,0.2,0.01]

    def possible_children(self, index, size_of_tree):
        possible_children, probs = super().possible_children(index, size_of_tree)
        probs[-1] += max(0, size_of_tree) / 180
        probs = probs / np.sum(probs)

        return possible_children, probs
        

class ConditionNode(NonTerminalNode):
    def __init__(self, token, condition_string):
        super(ConditionNode, self).__init__(token=token,
                                            num_children=3,
                                            possible_children={0: [NumberNode],
                                                               1: [ProgsNode],
                                                               2: [ProgsNode]})
        self.condition_string = condition_string
    
    @abstractmethod
    def condition(agent, num_spaces_param):
        return True
    
    def behavior(self, agent):
        _num_node, if_true, if_false = self.children
        num_spaces_param = _num_node.behavior(agent)
        if self.condition(agent, num_spaces_param):
            if_true.behavior(agent)
        else:
            if_false.behavior(agent)
    
    def __str__(self):
        return f'{self.condition_string}({str(self.children[0])}, ' + \
                             f'{str(self.children[1])}, ' + \
                             f'{str(self.children[2])})'
        
class FoodConditionNode(ConditionNode):
    def __init__(self):
        super(FoodConditionNode, self).__init__(token='<FoodCondition>',
                                                condition_string='if_food_ahead')

    def condition(self, agent, num_spaces_param):
        return agent.food_within(num_spaces_param)

class WallConditionNode(ConditionNode):
    def __init__(self):
        super(WallConditionNode, self).__init__(token='<WallCondition>',
                                                condition_string='if_wall_ahead')
        
    def condition(self, agent, num_spaces_param):
        return agent.wall_within(num_spaces_param)

class NumberNode(NonTerminalNode):
    def __init__(self):
        super(NumberNode, self).__init__(token='<Num>',
                                         num_children=1,
                                         possible_children={0: [One, Two, Three]})
        
    def behavior(self, agent):
        return self.children[0].behavior(agent)
    

class Progs2Node(NonTerminalNode):
    def __init__(self):
        super(Progs2Node, self).__init__(token="<Progs2>",
                                       num_children=2,
                                       possible_children={0: [ProgsNode],
                                                          1: [ProgsNode]})
        
    def behavior(self, agent):
        for child in self.children:
            child.behavior(agent)

    def __str__(self):
        return f'progs2({str(self.children[0])}, ' + \
                      f'{str(self.children[1])})'


class Progs3Node(NonTerminalNode):
    def __init__(self):
        super(Progs3Node, self).__init__(token="<Progs2>",
                                       num_children=3,
                                       possible_children={0: [ProgsNode],
                                                          1: [ProgsNode],
                                                          2: [ProgsNode]})
    
    def behavior(self, agent):
        success = True
        for child in self.children:
            if not child.behavior(agent):
                success = False
                break

        return success
    
    def __str__(self):
        return f'progs3({str(self.children[0])}, ' + \
                      f'{str(self.children[1])}, ' + \
                      f'{str(self.children[2])})'


class OperationNode(NonTerminalNode):
    def __init__(self):
        super(OperationNode, self).__init__(token='<Op>',
                                            num_children=1,
                                            possible_children={0:[TurnLeft, 
                                                                  TurnRight, 
                                                                  MoveForward]})
        

# ---- Terminal Nodes ----

# -- Movement -- 

class TurnLeft(TerminalNode):
    def __init__(self):
        super(TurnLeft, self).__init__(token='Left')

    def behavior(self, agent):
        agent.turn_left()
    
class TurnRight(TerminalNode):
    def __init__(self):
        super(TurnRight, self).__init__(token='Right')

    def behavior(self, agent):
        agent.turn_right()
    
class MoveForward(TerminalNode):
    def __init__(self):
        super(MoveForward, self).__init__(token='Move')

    def behavior(self, agent):
        agent.move()
    

# -- Numbers -- 

class One(TerminalNode):
    def __init__(self):
        super(One, self).__init__(token='1')

    def behavior(self, agent):
        return 1
    
class Two(TerminalNode):
    def __init__(self):
        super(Two, self).__init__(token='2')

    def behavior(self, agent):
        return 2
    
class Three(TerminalNode):
    def __init__(self):
        super(Three, self).__init__(token='3')

    def behavior(self, agent):
        return 3
