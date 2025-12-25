from grammaticalevolutiontools.programs import ProgramNode

from abc import abstractmethod

import pytest

class NodeAdditionalAbstractMethods(ProgramNode):
    def __init__():
        super().__init__()

    @abstractmethod
    def abstract_method(self):
        pass

class NodeNoInitFunc(ProgramNode):
    def _base_node_init(self, token, possible_children_dict = None,
                        special_child_probs=None):
        super()._base_node_init(token=token,
                                is_terminal=True,
                                is_root=False,
                                num_children=0,
                                possible_children_dict=possible_children_dict,
                                special_child_probs=special_child_probs)
        
    def _custom_init(self, param1):
        super()._custom_init()
        self._val = param1

class NodeInitWithParams(NodeNoInitFunc):
    def _base_node_init(token):
        super()._base_node_init(token)
    def _custom_init(param1):
        super()._custom_init(param1)

class ConcreteNode(NodeNoInitFunc):
    def _base_node_init(self):
        super()._base_node_init(token='<Concrete>')
    def _custom_init(self):
        super()._custom_init(param1=3)


# -- ReusableNode --
_token = ''
_num_children = 0
_is_terminal = True
_is_root = False
_label = None

class NodeTestingVals(ProgramNode):
    def _base_node_init(self):
        super()._base_node_init(token=_token,
                             is_terminal=_is_terminal,
                             is_root=_is_root,
                             num_children=_num_children,
                             label=_label)
        
    def _custom_init(self):
        super()._custom_init()


# --- Test Cases ---

def test_abstract_classes_cannot_be_instantiated():
    with pytest.raises(TypeError):
        NodeAdditionalAbstractMethods()

    with pytest.raises(TypeError):
        NodeInitWithParams()

    with pytest.raises(TypeError):
        NodeNoInitFunc()


def test_custom_init():
    node = ConcreteNode()
    assert node._val == 3

def test_base_node_init_core_vals_basic():
    node = ConcreteNode()

    assert node._token == '<Concrete>'
    assert node._max_num_children == 0
    assert node._is_terminal
    assert not node._is_root
    assert node._label is None

    assert node._ProgramNode__possible_children_dict == {}
    assert node._ProgramNode__special_child_probs == {}


# - -  Valid Value Checks - - 

def test_init_fail__invalid_token():
    global _token, _num_children, _is_terminal, _is_root, _label
    _num_children = 0
    _is_terminal = True
    _is_root = False
    _label = None
        
    _token = ''
    with pytest.raises(ValueError):
        NodeTestingVals()

    _token = 1
    with pytest.raises(TypeError):
        NodeTestingVals()

def test_init_fail__invalid_num_children():
    global _token, _num_children, _is_terminal, _is_root, _label
    _token = "<invalid>"
    _is_terminal = False
    _is_root = False
    _label = None

    _num_children = -1
    with pytest.raises(ValueError):
        NodeTestingVals()

    _num_children = "hello"
    with pytest.raises(TypeError):
        NodeTestingVals()

def test_init_fail__invalid_tags():
    global _token, _num_children, _is_terminal, _is_root, _label
    _token = "<invalid>"
    _num_children = 0
    _label = None

    _is_root = False
    _is_terminal = "not a bool"
    with pytest.raises(TypeError):
        NodeTestingVals()

    _is_root = "not_a_bool"
    _is_terminal = True
    with pytest.raises(TypeError):
        NodeTestingVals()

def test_init_fail__invalid_param_combos():
    global _token, _num_children, _is_terminal, _is_root, _label
    _token = "<invalid>"
    _label = None
    _num_children = 0

    _is_root = True
    _is_terminal = True
    with pytest.raises(ValueError):
        NodeTestingVals()

    _is_root = False
    _num_children = 1           # is still terminal
    with pytest.raises(ValueError):
        NodeTestingVals()

def test_init_fail__invalid_label():
    global _token, _num_children, _is_terminal, _is_root, _label
    _token = "<invalid>"
    _num_children = 0
    _is_root = False
    _is_terminal = False

    _label = 123
    with pytest.raises(TypeError):
        NodeTestingVals()


# - - Property Methods - - 

def test_properties():
    node = ConcreteNode()

    assert node.token is node._token
    assert node.is_terminal is node._is_terminal
    assert node.is_root is node._is_root
    assert node.max_num_children is node._max_num_children
    assert node.label is node._label

    assert node._possible_children_dict is \
        node._ProgramNode__possible_children_dict
    assert node._special_probs_dict is \
        node._ProgramNode__special_child_probs
    
def test_get_properties_to_pass_to_children():
    node = ConcreteNode()
    properties = node._get_properties_to_pass_to_children()

    assert 'tree' in properties
    assert '_depth' in properties

    # CONTINUE HERE

