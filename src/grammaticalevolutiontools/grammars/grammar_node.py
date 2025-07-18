from .._base_node import BaseNode

import numpy as np
from typing import Type, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .grammar import Grammar

class OutOfContextError(RuntimeError):
    def __init__(self):
        super(OutOfContextError, self).__init__("Cannot subclass GrammarNode outside of a Grammar context.")
    

class GrammarNode(BaseNode):

    # class properties

    # -- to be manually set --
    _MAX_NUM_CHILDREN: int = NotImplemented
    _POSSIBLE_CHILDREN_DICT: dict[int, list[Type['GrammarNode']]] = NotImplemented
    _IS_TERMINAL: bool = NotImplemented
    _IS_ROOT: bool = NotImplemented
    _TOKEN: str = NotImplemented

    _LABEL: Optional[str] = None
    _SPECIAL_CHILD_PROBS: Optional[dict[int, np.ndarray]] = None

    # -- automatically set when a class inherits --
    _ALL_POSSIBLE_CHILDREN: set[Type['GrammarNode']] = None
    _RESOLVED: bool = False
    _GRAMMAR: 'Grammar' = None

    # -------------------------

    def __init_subclass__(cls, **kwargs):

        from ..grammars import Grammar

        # - - Ensure class is being defined within a grammar context - - 

        current_grammar = Grammar.current_grammar
        if current_grammar is None:
            raise OutOfContextError()

        # - - Ensure necessary class properties are defined and correctly - - 

        # Ensure all required attributes are implemented 
        REQUIRED_CLASS_ATTRS = ["_MAX_NUM_CHILDREN", "_POSSIBLE_CHILDREN_DICT", "_IS_TERMINAL", "_IS_ROOT", "_TOKEN"]
 
        for attr in REQUIRED_CLASS_ATTRS:
            if getattr(cls, attr, NotImplemented) is NotImplemented:
                raise TypeError(f"Class attribute '{attr}' must be defined in {cls.__name__}, and cannot be 'NotImplemented'.")
                 
        GrammarNode._assert_token_valid(cls._TOKEN)
        GrammarNode._assert_label_valid(cls._LABEL)
        GrammarNode._assert_tags_valid(cls._IS_TERMINAL, cls._IS_ROOT)
        GrammarNode._assert_max_num_children_valid(cls._MAX_NUM_CHILDREN, cls._IS_TERMINAL)
        GrammarNode._assert_possible_children_dict_valid(cls._POSSIBLE_CHILDREN_DICT, cls._MAX_NUM_CHILDREN,
                                                         warnings_=current_grammar.warnings_enabled)
        
        if cls._SPECIAL_CHILD_PROBS is not None:
            GrammarNode._assert_child_probs_dict_valid(cls._SPECIAL_CHILD_PROBS, cls._POSSIBLE_CHILDREN_DICT,
                                                       warnings_=current_grammar.warnings_enabled)
            cls._SPECIAL_CHILD_PROBS = GrammarNode.convert_probs_dict_to_numpy(cls._SPECIAL_CHILD_PROBS)
        else:
            cls._SPECIAL_CHILD_PROBS = {}

        super().__init_subclass__()

        # if all is well, register the class with the grammar
        current_grammar.register(cls)

    # ------------------------

    @classmethod
    def _resolve_possible_children(cls):
        if cls.is_resolved():
            return

        for ind in cls._POSSIBLE_CHILDREN_DICT:
            cls._POSSIBLE_CHILDREN_DICT[ind] = [cls._GRAMMAR.get_class(cls_name) for cls_name in cls._POSSIBLE_CHILDREN_DICT[ind]]
        
        cls._ALL_POSSIBLE_CHILDREN = set()
        for ind, cls_list in cls._POSSIBLE_CHILDREN_DICT.items():
            for chld_cls in cls_list:
                cls._ALL_POSSIBLE_CHILDREN.add(chld_cls)

        cls._RESOLVED = True

    @classmethod
    def get_grammar(cls) -> 'Grammar':
        return cls._GRAMMAR
    
    @classmethod
    def is_resolved(cls):
        return cls._RESOLVED
    
    # -------------------------

    def __init__(self):
        if not self._GRAMMAR.is_valid:
            raise RuntimeError('Grammar setup failed. GrammarNodes cannot be instantiated.')
        
        super(GrammarNode, self).__init__()

    def get_all_possible_children(self):
        if type(self).is_resolved():
            return type(self)._ALL_POSSIBLE_CHILDREN.copy()
        else:
            raise RuntimeError('possible children not yet resolved.')
    
    @property
    def _possible_children_dict(self) -> dict[int, list[Type['GrammarNode']]]:
        if type(self).is_resolved():
            return type(self)._POSSIBLE_CHILDREN_DICT
        else:
            raise RuntimeError('possible children not yet resolved.')
    
    @property
    def _special_probs_dict(self) -> dict[int, np.ndarray]:
        return type(self)._SPECIAL_CHILD_PROBS
    
    @property
    def _all_possible_children(self) -> set[Type['GrammarNode']]:
        return type(self)._ALL_POSSIBLE_CHILDREN

    @property
    def max_num_children(self) -> int:
        return type(self)._MAX_NUM_CHILDREN
    
    @property
    def label(self) -> Optional[str]:
        return type(self)._LABEL
    
    @property
    def token(self) -> str:
        return type(self)._TOKEN
    
    @property
    def is_terminal(self) -> bool:
        return type(self)._IS_TERMINAL
    
    @property
    def is_root(self) -> bool:
        return type(self)._IS_ROOT
    

    
    
    