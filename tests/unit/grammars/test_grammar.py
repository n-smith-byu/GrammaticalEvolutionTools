from grammaticalevolutiontools.grammars import Grammar
from grammaticalevolutiontools.grammars import GrammarNode

import warnings

import pytest


class WorkingGrammar:
    _GRAMMAR = None

    @staticmethod
    def get_grammar():
        if WorkingGrammar._GRAMMAR is None:
            with Grammar() as wg:
                class RootNode(GrammarNode):
                    _MAX_NUM_CHILDREN = 1
                    _POSSIBLE_CHILDREN_DICT = {0: ['ChildNode']}
                    _IS_TERMINAL = False
                    _IS_ROOT = True
                    _TOKEN = "<Root>"

                class ChildNode(GrammarNode):
                    _MAX_NUM_CHILDREN = 0
                    _POSSIBLE_CHILDREN_DICT = {}
                    _IS_TERMINAL = True
                    _IS_ROOT = False
                    _TOKEN = "<Child>"


def test_grammar_no_root():
    """Test that a grammar must have at least one root node."""
    with pytest.raises(Grammar.NoRootDefinedException):
        with Grammar() as grammar:
            class NonRootNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = True
                _IS_ROOT = False
                _TOKEN = "non_root"


def test_grammar_multiple_roots():
    """Test that a grammar cannot have multiple root nodes."""
    with pytest.raises(Grammar.MultipleRootsException):
        with Grammar() as grammar:
            class RootNode1(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = "root1"

            class RootNode2(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = "root2"


def test_grammar_context_manager():
    """Test that the Grammar context manager correctly sets and unsets the current_grammar."""
    assert Grammar.current_grammar is None
    
    with Grammar() as grammar:
        assert Grammar.current_grammar is grammar
        
        class RootNode(GrammarNode):
            _MAX_NUM_CHILDREN = 0
            _POSSIBLE_CHILDREN_DICT = {}
            _IS_TERMINAL = False
            _IS_ROOT = True
            _TOKEN = "root"
    
    assert Grammar.current_grammar is None


def test_grammar_node_registration():
    """Test that nodes are correctly registered with the grammar."""
    with Grammar() as grammar:
        class RootNode(GrammarNode):
            _MAX_NUM_CHILDREN = 1
            _POSSIBLE_CHILDREN_DICT = {0: ['ChildNode']} 
            _IS_TERMINAL = False
            _IS_ROOT = True
            _TOKEN = "root"

        class ChildNode(GrammarNode):
            _MAX_NUM_CHILDREN = 0
            _POSSIBLE_CHILDREN_DICT = {}
            _IS_TERMINAL = True
            _IS_ROOT = False
            _TOKEN = "child"
        
        assert len(grammar.valid_node_classes) == 2
        assert RootNode in grammar.valid_node_classes
        assert ChildNode in grammar.valid_node_classes
        assert grammar.root == RootNode


def test_grammar_abstract_node_warning():
    """Test that a warning is issued for unused abstract classes."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        with Grammar() as grammar:
            class AbstractNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {0: []}
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = "abstract"
                
                # Make it abstract by requiring parameters in __init__
                def __init__(self, param):
                    super().__init__()
            
            class RootNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = "root"
        
        # Check if a warning was issued about the unused abstract class
        assert any("Abstract class AbstractNode was defined but no concrete classes were ever created from it" in str(warning.message) for warning in w)


def test_grammar_node_reference_validation():
    """Test that nodes can only reference other nodes defined in the same grammar."""
    with pytest.raises(LookupError):
        with Grammar() as grammar2:
            class RootNode2(GrammarNode):
                _MAX_NUM_CHILDREN = 1
                _POSSIBLE_CHILDREN_DICT = {0: ['ChildNode1']}  # Reference to node not defined in the grammar
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = "root2"


def test_grammar_node_cannot_reference_root():
    """Test that nodes cannot reference the root node as a possible child."""
    with pytest.raises(ValueError):
        with Grammar() as grammar:
            class RootNode(GrammarNode):
                _MAX_NUM_CHILDREN = 1
                _POSSIBLE_CHILDREN_DICT = {0: ['ChildNode']}  # Will be updated
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = "root"
                
            class ChildNode(GrammarNode):
                _MAX_NUM_CHILDREN = 1
                _POSSIBLE_CHILDREN_DICT = {0: ['RootNode']}  # Invalid reference to root
                _IS_TERMINAL = False
                _IS_ROOT = False
                _TOKEN = "child"


def test_grammar_node_grammar_property():
    """Test that nodes classes have a reference to their grammar."""
    with Grammar() as grammar:
        class RootNode(GrammarNode):
            _MAX_NUM_CHILDREN = 0
            _POSSIBLE_CHILDREN_DICT = {}
            _IS_TERMINAL = False
            _IS_ROOT = True
            _TOKEN = "root"
        
    assert RootNode._GRAMMAR is grammar