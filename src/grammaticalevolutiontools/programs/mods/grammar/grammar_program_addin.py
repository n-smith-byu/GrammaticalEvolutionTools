from ....grammars import Grammar

class GrammarProgramMeta(type):
    def __call__(cls, *args, **kwds):
        if issubclass(cls, GrammarProgramAddin):
            if cls._grammar is NotImplemented:
                raise TypeError(
                    "`GrammarProgramTree` subclasses must implement the "
                    "`_grammar` class attribute before they can be "
                    "instantiated."
                    )
        
        return super().__call__(*args, **kwds)

class GrammarProgramAddin(metaclass=GrammarProgramMeta):
    
    _grammar = NotImplemented

    def __init_subclass__(cls):
        if cls._grammar is not NotImplemented and \
                not isinstance(cls._grammar, Grammar):
            raise TypeError(
                "`_grammar` class attribute of subclasses must be a valid "
                "instance of Grammar. Found object of type "
                f"{type(cls._grammar).__name__}"
                )
        return super().__init_subclass__()

    def _assert_root_valid(self, root):
        if root and not isinstance(root, self.get_root_class()):
            raise TypeError(
                "Provided `root` does not match this Program's Grammar."
            )
        
    def _verify_and_set_root(self, root):
        GrammarProgramAddin._assert_root_valid(self, root)
        GrammarProgramAddin._set_root(self, root)
        
    def _set_root(self, root):
        self._root = root or self.create_root()

    @classmethod
    def create_root(cls):
        root_class = cls.get_root_class()
        return root_class()
    
    @classmethod
    def get_root_class(cls):
        return cls._grammar.root

    @classmethod
    def get_grammar(cls):
        return cls._grammar