from grammaticalevolutiontools.grammars import Grammar
from grammaticalevolutiontools.grammars import GrammarNode, OutOfContextError

import numpy as np

import pytest


def test_grammar_node_outside_context():
    """Test that GrammarNode cannot be subclassed outside a Grammar context."""
    with pytest.raises(OutOfContextError):
        class InvalidNode(GrammarNode):
            _MAX_NUM_CHILDREN = 0
            _POSSIBLE_CHILDREN_DICT = {}
            _IS_TERMINAL = False
            _IS_ROOT = True
            _TOKEN = "invalid"


def test_grammar_node_missing_required_attributes():
    """Test that GrammarNode subclasses must define all required attributes."""
    with pytest.raises(TypeError):
        with Grammar() as grammar:
            class MissingAttributesNode(GrammarNode):
                # Missing required attributes
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = False
                _IS_ROOT = True

    with pytest.raises(TypeError):
        with Grammar() as grammar:
            class MissingAttributesNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = False
                _TOKEN = 'test'  # Should be a string

    with pytest.raises(TypeError):
        with Grammar() as grammar:
            class MissingAttributesNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_ROOT = True
                _TOKEN = 'test'  # Should be a string

    with pytest.raises(TypeError):
        with Grammar() as grammar:
            class MissingAttributesNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = 'test'  # Should be a string

    with pytest.raises(TypeError):
        with Grammar() as grammar:
            class MissingAttributesNode(GrammarNode):
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = 'test'  # Should be a string


def test_grammar_node_invalid_attributes():
    """Test validation of GrammarNode attributes."""
    with pytest.raises(TypeError):
        with Grammar() as grammar:
            # Test invalid token
            class InvalidTokenNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = 123  # Should be a string

        with Grammar() as grammar:
            # Test invalid token
            class InvalidTokenNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = False
                _IS_ROOT = "not a bool"     # should be a bool
                _TOKEN = 'test'

    with pytest.raises(TypeError):
        with Grammar() as grammar:
            # Test invalid token
            class InvalidTokenNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = "not a bool"     # should be a bool
                _IS_ROOT = True
                _TOKEN = 'test'

    with pytest.raises(TypeError):
        with Grammar() as grammar:
            # Test invalid token
            class InvalidTokenNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = ["not", "a", "dict"]      # should be a dict[int, list]
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = 'test'

    with pytest.raises(ValueError):
        with Grammar() as grammar:
            # Test invalid token
            class InvalidTokenNode(GrammarNode):
                _MAX_NUM_CHILDREN = -1      # should be >= 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = 'test'

    with pytest.raises(TypeError):
        with Grammar() as grammar:
            # Test invalid token
            class InvalidTokenNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = 'test'

                _LABEL = {}     # should be None or a string

    with pytest.raises(TypeError):
        with Grammar() as grammar:
            # Test invalid token
            class InvalidTokenNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = 'test'

                _SPECIAL_CHILD_PROBS = ["not", "a", "dict"]     # should be dict[int, list[float]]


def test_grammar_node_root_terminal_conflict():
    """Test that a node cannot be both root and terminal."""
    with pytest.raises(ValueError):
        with Grammar() as grammar:
            class ConflictingNode(GrammarNode):
                _MAX_NUM_CHILDREN = 0
                _POSSIBLE_CHILDREN_DICT = {}
                _IS_TERMINAL = True
                _IS_ROOT = True 
                _TOKEN = "conflict"

def test_grammar_node_is_terminal_max_num_children_conflict():
    """Test that a node cannot be both root and terminal."""
    with pytest.raises(ValueError):
        with Grammar() as grammar:
            class RootNode(GrammarNode):
                _MAX_NUM_CHILDREN = 1
                _POSSIBLE_CHILDREN_DICT = {0: ['ConflictingNode']}
                _IS_TERMINAL = False
                _IS_ROOT = True
                _TOKEN = 'root'

            class ConflictingNode(GrammarNode):
                _MAX_NUM_CHILDREN = 1
                _POSSIBLE_CHILDREN_DICT = {0: []}
                _IS_TERMINAL = True
                _IS_ROOT = False
                _TOKEN = "conflict"

def test_grammar_node_property_implementations():
    """Test that GrammarNode correctly implements all abstract properties from BaseNode."""
    with Grammar() as grammar:
        class ValidTerminalNode(GrammarNode):
            _MAX_NUM_CHILDREN = 0
            _POSSIBLE_CHILDREN_DICT = {}
            _IS_TERMINAL = False
            _IS_ROOT = True
            _TOKEN = "terminal"
            _LABEL = "term_label"

    node = ValidTerminalNode()
    
    # Test all properties are correctly implemented
    assert node.max_num_children == ValidTerminalNode._MAX_NUM_CHILDREN
    assert node.label == ValidTerminalNode._LABEL
    assert node.token == ValidTerminalNode._TOKEN
    assert node.is_terminal == ValidTerminalNode._IS_TERMINAL
    assert node.is_root == ValidTerminalNode._IS_ROOT

    assert node._possible_children_dict is ValidTerminalNode._POSSIBLE_CHILDREN_DICT
    assert node._special_probs_dict is ValidTerminalNode._SPECIAL_CHILD_PROBS


def test_grammar_node_registration():
    """Test that GrammarNode subclasses are automatically registered with the grammar."""
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

        # Check registration
        assert RootNode in grammar.valid_node_classes
        assert ChildNode in grammar.valid_node_classes
        assert grammar.root == RootNode


def test_grammar_node_special_probs():
    """Test that special child probabilities are correctly handled."""
    with Grammar() as grammar:
        class ChildNodeA(GrammarNode):
            _MAX_NUM_CHILDREN = 0
            _POSSIBLE_CHILDREN_DICT = {}
            _IS_TERMINAL = True
            _IS_ROOT = False
            _TOKEN = "childA"

        class ChildNodeB(GrammarNode):
            _MAX_NUM_CHILDREN = 0
            _POSSIBLE_CHILDREN_DICT = {}
            _IS_TERMINAL = True
            _IS_ROOT = False
            _TOKEN = "childB"

        class ParentNode(GrammarNode):
            _MAX_NUM_CHILDREN = 2
            _POSSIBLE_CHILDREN_DICT = {0: ['ChildNodeA', 'ChildNodeB'], 
                                       1: ['ChildNodeA']}
            _IS_TERMINAL = False
            _IS_ROOT = True
            _TOKEN = "parent"
            _SPECIAL_CHILD_PROBS = {0: [0.7, 0.3]}  # Custom probabilities for first child

    parent = ParentNode()
    
    # Test that special probabilities are correctly converted to numpy arrays
    assert isinstance(parent._special_probs_dict[0], np.ndarray)
    assert np.allclose(parent._special_probs_dict[0], np.array([0.7, 0.3]))
    
    # Test that default uniform probabilities are used when not specified
    child1_probs = parent.get_probs(1)
    assert np.allclose(child1_probs, np.array([1.0]))


def test_grammar_node_get_all_possible_children():
    """Test that get_all_possible_children returns the correct set of child types."""
    with Grammar() as grammar:
        class ParentNode(GrammarNode):
            _MAX_NUM_CHILDREN = 2
            _POSSIBLE_CHILDREN_DICT = {0: ['ChildNodeA', 'ChildNodeB'], 
                                       1: ['ChildNodeA']}
            _IS_TERMINAL = False
            _IS_ROOT = True
            _TOKEN = "parent"

        class ChildNodeA(GrammarNode):
            _MAX_NUM_CHILDREN = 0
            _POSSIBLE_CHILDREN_DICT = {}
            _IS_TERMINAL = True
            _IS_ROOT = False
            _TOKEN = "childA"

        class ChildNodeB(GrammarNode):
            _MAX_NUM_CHILDREN = 0
            _POSSIBLE_CHILDREN_DICT = {}
            _IS_TERMINAL = True
            _IS_ROOT = False
            _TOKEN = "childB"

    parent = ParentNode()
    all_children = parent.get_all_possible_children()
    
    assert ChildNodeA in all_children
    assert ChildNodeB in all_children
    assert len(all_children) == 2