from .grammar_node import GrammarNode

from typing import Type, TYPE_CHECKING
import warnings

if TYPE_CHECKING:
    from ..agents import Agent

class Grammar:

    class MultipleRootsException(ValueError):
        def __init__(self):
            super(Grammar.MultipleRootsException, self).__init__("Multiple Root Nodes Defined within Grammar.")

    class NoRootDefinedException(ValueError):
        def __init__(self):
            super(Grammar.NoRootDefinedException, self).__init__("No Root Nodes Defined within Grammar.")

    current_grammar = None

    def __init__(self, target_agent_type: Type[Agent] = None, 
                 warnings=True):
        self._roots: list[Type[GrammarNode]] = []
        self._all_node_classes: dict[str, Type[GrammarNode]] = {}
        self._concrete_types: set[Type[GrammarNode]] = set()
        self._abstract_types: set[Type[GrammarNode]] = set()

        self._target_agent_type = target_agent_type
        self._warnings = warnings
        self._is_valid = False

    def __enter__(self):
        Grammar.current_grammar = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        Grammar.current_grammar = None

        if exc_type is None:
            self._validate()
            self._is_valid = True
        
        return self._is_valid

    def _validate(self):
        if len(self._roots) == 0:
            raise Grammar.NoRootDefinedException()
        elif len(self._roots) > 1:
            raise Grammar.MultipleRootsException()
        
        for cls in self._abstract_types.union(self._concrete_types):
            self._all_node_classes[cls.__name__] = cls

        # Make sure all possible children are also in the Grammar
        seen_nodes = set()
        for node_cls in self._all_node_classes.values():
            try:
                node_cls._resolve_possible_children()
                
            except KeyError as e:
                raise LookupError(f"Error resolving possible children for {node_cls.__name__}. " + \
                                   "Child not defined within the scope of the Grammar.") from e
            
            for chld_cls in node_cls._ALL_POSSIBLE_CHILDREN:
                
                error = None
                if chld_cls is self.root:
                    error = "Root node class"
                if chld_cls in self._abstract_types:
                    error = "Abstract node class"
                if error is not None:
                    raise ValueError(f"{error} cannot be listed as a possible child of another class. Class at fault: {node_cls.__name__} referencing {chld_cls.__name__}")
                    
                seen_nodes.update(node_cls._ALL_POSSIBLE_CHILDREN)

        if self._warnings:
            # Raise a warning if abstract classes exist that weren't used to make concrete classes
            for abstract_class in self._abstract_types:
                implemented = False
                for cls in self._concrete_types:
                    if issubclass(cls, abstract_class):
                        implemented = True
                        break
                if not implemented:
                    warnings.warn(f"Abstract class {abstract_class.__name__} was defined but no concrete classes were ever created from it. " + 
                                "Please note that all concrete classes must have no parameters other than self in their __init__ function, " + \
                                "otherwise they will still be considered abstract classes.", 
                                UserWarning)

            # Raise a warning if a concrete class (besides the root) is not a possible child of any other class
            for node_cls in self._concrete_types:
                if node_cls is self.root:
                    continue

                if node_cls not in seen_nodes:
                    warnings.warn(f"{node_cls.__name__} is not listed as a possible child type for any other node in its grammar.", 
                                UserWarning)
                

    # --------------------

    def register(self, cls: Type[GrammarNode]):
        """Register a node class inside the grammar."""

        cls._GRAMMAR = self

        if cls.is_abstract_class():
            self._abstract_types.add(cls)
        else:
            if cls._IS_ROOT:
                self._roots.append(cls)

            self._concrete_types.add(cls)
                
    def get_class(self, cls_name: str) -> Type[GrammarNode]:
        return self._all_node_classes[cls_name]

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @property
    def root(self) -> Type[GrammarNode]:
        return self._roots[0]
    
    @property
    def warnings_enabled(self) -> bool:
        return self._warnings
    
    @property
    def abstract_classes(self) -> set[Type[GrammarNode]]:
        return self._abstract_types.copy()

    @property
    def valid_node_classes(self) -> set[Type[GrammarNode]]:
        return self._concrete_types.copy()   
    
    @property
    def target_agent_type(self) -> Type[Agent]:
        return self._target_agent_type
