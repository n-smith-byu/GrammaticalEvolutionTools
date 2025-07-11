from .. import ProgramNode
from ..basic_nodes import NonTerminalNode
from ..factor_nodes import FactorNode

from abc import abstractmethod
from typing import Type, Optional

Probabilities = list[float]
FactorList = list[list[Type[FactorNode]]]

class ConditionNode(NonTerminalNode):

    TRUE_IND = 0
    FALSE_IND = 1

    def _base_node_init(
            self, token: str, 
            condition_string: str, 
            possible_children_true: list[Type[ProgramNode]], 
            possible_children_false: list[Type[ProgramNode]], 
            t_child_probs: Optional[Probabilities] = None, 
            f_child_probs: Optional[Probabilities] = None,
            factor_possible_vals: Optional[FactorList] = None
            ):
        
        # Construct traditional possible_children dict
        possible_children = {0: possible_children_true,
                             1: possible_children_false}
        
        for k, possible_vals in enumerate(factor_possible_vals, start=2):
            possible_children[k] = possible_vals.copy()
        
        child_probs = {0: t_child_probs,
                       1: f_child_probs}
        
        super()._base_node_init(
            token=token,
            label=condition_string,
            is_root=False,
            num_children=len(possible_children),
            possible_children=possible_children,
            child_probs=child_probs
        )
        
    def _custom_init(self, factor_names: list[str] = None):
        if factor_names is None:
            factor_names = []

        num_factors = len(self._possible_children_dict) - 2
        if len(factor_names) != num_factors:
            raise ValueError("Length of factor_names does not match number "
                            f"of factors. Num factors found: {num_factors}. "
                            f"Num names provided: {len(factor_names)} ")

        self._factor_inds: dict[str, int] = {}
        used = set()
        for i, factor in enumerate(factor_names, start=2):
            if factor in used:
                raise ValueError("Same factor name used twice. "
                                f"Value at fault: '{factor}'")
            self._factor_inds[factor] = i
                
        super()._custom_init()

    def _get_factor_ind(self, factor: str) -> int:
        return self._factor_inds[factor]
    
    def _get_factor(self, factor: str) -> FactorNode:
        return self._children[self._get_factor_ind(factor)]
    
    def get_next_child(self):
        if self._curr_child > -1:
            self._curr_child = -1
            return None
        else:
            child_if_true, child_if_false = self.children[:2]
            if self.condition():
                self._curr_child = 0
                return child_if_true
            else:
                self._curr_child = 1
                return child_if_false
            
    @abstractmethod
    def condition(self) -> bool:
        return True
    
    def __str__(self):
        _str = f"{self.label}({self._true_child}, {self._false_child}"
        for name, ind in self._factor_inds.items():
            _str += f", {name}={self._children[ind]}"

        return _str + ")"
    
    @property
    def _true_child(self) -> ProgramNode:
        return self._children[ConditionNode.TRUE_IND]
    
    @property
    def _false_child(self) -> ProgramNode:
        return self._children[ConditionNode.FALSE_IND]

