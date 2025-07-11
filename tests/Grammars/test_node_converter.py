from grammaticalevolutiontools.programs.nodes import ProgramNode
from grammaticalevolutiontools.programs.nodes.basic_nodes import \
    RootNode
from grammaticalevolutiontools.programs.nodes.logic_nodes import \
    SequentialNode, ConditionNode
from grammaticalevolutiontools.programs.nodes.factor_nodes import \
    RandIntegerNode, IntegerNode
from grammaticalevolutiontools.grammars import Grammar, \
    GrammarNode, as_grammar_node

import numpy as np
import pytest


with Grammar() as grammar:
    @as_grammar_node
    class MyRootNode(RootNode):
        def _base_node_init(self):
            return super()._base_node_init(
                token='<Root>',
                possible_children=['MySeqNode', 'MyConditionNode'])
        
    @as_grammar_node
    class MySeqNode(SequentialNode):
        def _base_node_init(self):
            return super()._base_node_init(
                token='<SeqNode>',
                num_children=2,
                possible_children=['MyConditionNode',
                                   'ValidOverriddenMethodNode',
                                   'InvalidOverriddenMethodNode']
            )
        def _custom_init(self):
            return super()._custom_init()
            
    @as_grammar_node
    class MyConditionNode(ConditionNode):
        def _base_node_init(self):
            return super()._base_node_init(
                token='<ConditionNode>',
                condition_string='my_condition',
                possible_children_true=['MySeqNode', 'MyConditionNode'],
                possible_children_false=['MySeqNode', 'MyConditionNode'],
                factor_possible_vals=[
                    ['Two', 'Three'],
                    ['MyRandInt']
                ],
                t_child_probs=[0.8, 0.2],
                f_child_probs=[0.2, 0.8],
            )
        
        def _custom_init(self):
            return super()._custom_init(
                factor_names=[
                    'factor1',
                    'factor2'
                ]
            )
        
        def condition(self):
            return True
        
    @as_grammar_node
    class MyRandInt(RandIntegerNode):
        def _base_node_init(self):
            return super()._base_node_init()
        
        def _custom_init(self):
            return super()._custom_init(a=1, b=3)
        
    @as_grammar_node
    class Two(IntegerNode):
        def _base_node_init(self):
            return super()._base_node_init()
          
        def _custom_init(self):
            return super()._custom_init(num=2)    
        
    @as_grammar_node
    class Three(IntegerNode):
        def _base_node_init(self):
            return super()._base_node_init()
          
        def _custom_init(self):
            return super()._custom_init(num=3)
        
    @as_grammar_node
    class ValidOverriddenMethodNode(SequentialNode):
        def _base_node_init(self):
            return super()._base_node_init(
                token='<Overriden>',
                num_children=1,
                possible_children=['MySeqNode', 'MyConditionNode'])
        
        def get_probs(self, index):
            return 'overridden_value'
        
    @as_grammar_node
    class InvalidOverriddenMethodNode(SequentialNode):
        def _base_node_init(self):
            return super()._base_node_init(
                token='<Overriden>',
                num_children=1,
                possible_children=['MySeqNode', 'MyConditionNode'])
        
        def get_all_possible_children(self):
            return 'overridden_value'
        

# - - TESTS - - 

PATH_TO_RANDINT_MODULE = 'grammaticalevolutiontools.programs.nodes.factor_nodes.rand_int_node.random.randint'
    
def test_class_level_properties_correct():
    assert MyRootNode._ORIGINAL_NODE_CLS is not None
    assert MyRootNode._ORIGINAL_NODE_CLS is not MyRootNode
    assert MyRootNode._MAX_NUM_CHILDREN == 1
    assert isinstance(MyRootNode._POSSIBLE_CHILDREN_DICT, dict)
    assert MyConditionNode in MyRootNode._POSSIBLE_CHILDREN_DICT[0]
    assert MySeqNode in MyRootNode._POSSIBLE_CHILDREN_DICT[0]
    assert MyRootNode._SPECIAL_CHILD_PROBS == {}
    assert MyRootNode._IS_TERMINAL is False
    assert MyRootNode._IS_ROOT is True
    assert MyRootNode._TOKEN == '<Root>'
    assert MyRootNode._LABEL == None
    assert MyRootNode._GRAMMAR is grammar
    assert MyRootNode._RESOLVED is True
    assert MyRootNode._ALL_POSSIBLE_CHILDREN == {MyConditionNode, MySeqNode}

    assert len(MyConditionNode._SPECIAL_CHILD_PROBS) == 2
    assert np.all(MyConditionNode._SPECIAL_CHILD_PROBS[0] == [0.8, 0.2])
    assert np.all(MyConditionNode._SPECIAL_CHILD_PROBS[1] == [0.2, 0.8])

def test_converted_nodes_are_both_grammar_and_custom_node_class():
    assert issubclass(MyRootNode, GrammarNode)
    assert issubclass(MyRootNode, ProgramNode)
    assert issubclass(MyRootNode, MyRootNode._ORIGINAL_NODE_CLS)

def test_resulting_classes_can_be_instantiated():
    MyRootNode()
    MySeqNode()
    MyConditionNode()
    MyRandInt()
    Three()
    Two()

def test_decorator_fails_on_abstract_classes():
    with pytest.raises(TypeError):
        with Grammar() as grammar2:
            @as_grammar_node
            class MyAbstractNodeClass(ConditionNode):
                pass

def test_instances_dont_have_basic_properties_local():
    instance = MyRootNode()

    with pytest.raises(AttributeError):
        instance._token
    with pytest.raises(AttributeError):
        instance._label
    with pytest.raises(AttributeError):
        instance._is_root
    with pytest.raises(AttributeError):
        instance._is_terminal
    with pytest.raises(AttributeError):
        instance._max_num_children

    with pytest.raises(AttributeError):
        instance.__possible_children_dict
    with pytest.raises(AttributeError):
        instance.__special_child_probs
    with pytest.raises(AttributeError):
        instance.__all_possible_children

    with pytest.raises(AttributeError):
        instance._MyRootNode__possible_children_dict
    with pytest.raises(AttributeError):
        instance._MyRootNode__special_child_probs
    with pytest.raises(AttributeError):
        instance._MyRootNode__all_possible_children

def test_custom_properties_and_methods_copied_over_correctly():
    instance1: ConditionNode = MyConditionNode()

    assert instance1._true_child is None
    assert instance1._false_child is None

    assert instance1._get_factor_ind('factor1') == 2
    assert instance1._get_factor_ind('factor2') == 3

    assert instance1._get_factor('factor1') is None

    assert instance1._curr_child == -1

    t_child = MySeqNode()
    f_child = MyConditionNode()
    instance1.add_child(t_child, 0)             
    instance1.add_child(f_child, 1)

    assert instance1.condition() is True
    assert instance1.get_next_child() is t_child

def test_custom_node_assertions_and_helpers_not_copied():
        instance: ConditionNode = MyConditionNode()

        with pytest.raises(AttributeError):
            instance._base_node_init()

        with pytest.raises(AttributeError):
            instance._init_possible_children()

        with pytest.raises(AttributeError):
            instance._set_possible_children()

        with pytest.raises(AttributeError):
            instance._set_child_probs()

        with pytest.raises(AttributeError):
            instance._assert_possible_child_type_is_valid()

        with pytest.raises(AttributeError):
            instance._assert_vals_valid()
        

def test_dynamic_custom_properties_work_correctly(mocker):
    mock_randint = mocker.patch(
        PATH_TO_RANDINT_MODULE,
        side_effect=[1, 2]  # First call returns 1, second returns 2
    )
    instance1: RandIntegerNode = MyRandInt()
    instance2: RandIntegerNode = MyRandInt()

    assert mock_randint.call_count == 2
    mock_randint.assert_has_calls([
        mocker.call(1, 3),
        mocker.call(1, 3)
    ])
    
    assert instance1._val == 1
    assert instance2._val == 2

def test_valid_overridden_methods_hold():
    instance = ValidOverriddenMethodNode()
    assert instance.get_probs(index=0) == 'overridden_value'

def test_invalid_dup_method_not_copied():
    instance = InvalidOverriddenMethodNode()
    assert instance.get_all_possible_children() != 'overridden_value'
    
def test_custom_class_properties_copied_over_correctly():
    assert MyConditionNode.TRUE_IND == 0
    assert MyConditionNode.FALSE_IND == 1

def test_base_node_abstract_properties_correctly_implemented():
    instance = MyRootNode()

    assert instance.token is MyRootNode._TOKEN
    assert instance.label is MyRootNode._LABEL
    assert instance.is_terminal is MyRootNode._IS_TERMINAL
    assert instance.is_root is MyRootNode._IS_ROOT
    assert instance.max_num_children is MyRootNode._MAX_NUM_CHILDREN
    assert instance._possible_children_dict is MyRootNode._POSSIBLE_CHILDREN_DICT
    assert instance._special_probs_dict is MyRootNode._SPECIAL_CHILD_PROBS
    