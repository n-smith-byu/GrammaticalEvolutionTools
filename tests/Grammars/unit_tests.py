from grammaticalevolutiontools.programs.nodes import ProgramNode
from grammaticalevolutiontools.programs.nodes.basic_nodes import RootNode
from grammaticalevolutiontools.programs.nodes.logic_nodes import \
    SequentialNode, ConditionNode
from grammaticalevolutiontools.programs.nodes.factor_nodes import \
    RandIntegerNode, IntegerNode
from grammaticalevolutiontools.grammars import Grammar, \
    GrammarNode, as_grammar_node

import unittest
from unittest.mock import patch

import numpy as np

# - - SETUP - - 

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
                label='my_condition',
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

class TestNodeConverter(unittest.TestCase):

    # Tests that properties were copied over to 
    # class-level attributes correctly
    def test_class_level_properties_correct(self):
        self.assertIsNot(MyRootNode._ORIGINAL_NODE_CLS, None)
        self.assertIsNot(MyRootNode._ORIGINAL_NODE_CLS, MyRootNode)
        self.assertEqual(MyRootNode._MAX_NUM_CHILDREN, 1)
        self.assertIsInstance(MyRootNode._POSSIBLE_CHILDREN_DICT, dict)
        self.assertIn(MyConditionNode, MyRootNode._POSSIBLE_CHILDREN_DICT[0])
        self.assertIn(MySeqNode, MyRootNode._POSSIBLE_CHILDREN_DICT[0])
        self.assertEqual(MyRootNode._SPECIAL_CHILD_PROBS, {})
        self.assertIs(MyRootNode._IS_TERMINAL, False)
        self.assertIs(MyRootNode._IS_ROOT, True)
        self.assertEqual(MyRootNode._TOKEN, '<Root>')
        self.assertEqual(MyRootNode._LABEL, '')
        self.assertIs(MyRootNode._GRAMMAR, grammar)
        self.assertIs(MyRootNode._RESOLVED, True)
        self.assertEqual(
            MyRootNode._ALL_POSSIBLE_CHILDREN, 
            {MyConditionNode, MySeqNode}
        )

        self.assertEqual(len(MyConditionNode._SPECIAL_CHILD_PROBS), 2)
        self.assertTrue(np.all(MyConditionNode._SPECIAL_CHILD_PROBS[0] == [0.8, 0.2]))
        self.assertTrue(np.all(MyConditionNode._SPECIAL_CHILD_PROBS[1] == [0.2, 0.8]))


    # Tests the new node is a subclass of both GrammarNode 
    # and the original ProgramNode class
    # Only works if new class uses InheritingNode meta
    def test_converted_nodes_are_both_grammar_and_custom_node_class(self):
        self.assertTrue(issubclass(MyRootNode, GrammarNode))
        self.assertTrue(issubclass(MyRootNode, ProgramNode))
        self.assertTrue(issubclass(MyRootNode, MyRootNode._ORIGINAL_NODE_CLS))


    # Tests that the new classes are actually valid, not abstract,
    # and can be instantiated with no issues
    def test_resulting_classes_can_be_instantiated(self):
        MyRootNode()
        MySeqNode()
        MyConditionNode()
        MyRandInt()
        Three()
        Two()


    # Tests that only concrete classes work with the decorator
    def test_decorator_fails_on_abstract_classes(self):
        def invalid_use():
            with Grammar() as grammar2:
                @as_grammar_node
                class MyAbstractNodeClass(ConditionNode):
                    pass        # doesn't define condition, so is abstract

        self.assertRaises(Exception, invalid_use)
            

    # Tests to ensure BaseNode properties are not contained at the 
    # instance level in the new class. i.e. The new class never 
    # calls ProgramNode.__init__
    def test_instances_dont_have_basic_properties_local(self):
        instance = MyRootNode()

        self.assertRaises(AttributeError, lambda: instance._token)
        self.assertRaises(AttributeError, lambda: instance._label)
        self.assertRaises(AttributeError, lambda: instance._is_root)
        self.assertRaises(AttributeError, lambda: instance._is_terminal)
        self.assertRaises(AttributeError, lambda: instance._max_num_children)
        self.assertRaises(AttributeError, lambda: instance.__possible_children_dict)
        self.assertRaises(AttributeError, lambda: instance.__special_child_probs)
        self.assertRaises(AttributeError, lambda: instance._all_possible_children)


    # Tests to ensure all custom behavior was copied over correctly
    # uses ConditionNode, which defines _custom_init behavior,
    # inherits other custom_init, behavior, and has additional 
    # method defined.
    def test_custom_properties_and_methods_copied_over_correctly(self):
        instance1: ConditionNode = MyConditionNode()

        # assert instances of MyConditionNode still have 
        # custom properties
        self.assertIs(instance1._true_child, None)
        self.assertIs(instance1._false_child, None)

        # assert instances of MyConditionNode still have 
        # custom methods, and that they still work
        self.assertEqual(instance1._get_factor_ind('factor1'), 2)

        self.assertIs(instance1._get_factor('factor1'), None)

        # assert still carries properties from NonTerminalNode, 
        # which ConditionNode inherits from
        self.assertEqual(instance1._curr_child, -1)

        # Assert methods from NonTerminalNode still work
        t_child = MySeqNode()                           # setup
        f_child = MyConditionNode()
        instance1.add_child(t_child, 0)             
        instance1.add_child(f_child, 1)

        self.assertIs(instance1.condition(), True)      # actual tests
        self.assertIs(instance1.get_next_child(), t_child)


    # Tests to ensure assertions and methods related to setting and verifying
    # instance-level BaseNode properties are not copied over.
    def test_custom_node_assertions_and_helpers_not_copied(self):
        instance: ConditionNode = MyConditionNode()

        self.assertRaises(
            AttributeError,
            lambda: instance._base_node_init
        )
        self.assertRaises(
            AttributeError,
            lambda: instance._init_possible_children
        )
        self.assertRaises(
            AttributeError,
            lambda: instance._set_possible_children
        )
        self.assertRaises(
            AttributeError,
            lambda: instance._set_child_probs
        )
        self.assertRaises(
            AttributeError, 
            lambda: instance._assert_possible_child_type_is_valid
        )
        self.assertRaises(
            AttributeError,
            lambda: instance._assert_vals_valid
        )
        

    # Additional tests to ensure _custom_init still works as expected. 
    # tests that dynamic properties are indeed being calculated for each
    # instance of the new class rather than being copied from a 
    # single instance of the ProgramNode class to every 
    # instance of the new class
    @patch('random.randint')
    def test_dynamic_custom_properties_work_correctly(self, mock_randint):
        mock_randint.return_value = 1
        instance1: RandIntegerNode = MyRandInt()

        mock_randint.return_value = 2
        instance2: RandIntegerNode = MyRandInt()
        
        self.assertEqual(instance1._val, 1)
        self.assertEqual(instance2._val, 2)


    # Tests that when get_probs is overridden by the ProgramNode,
    # it is still overridden in the new class. 
    def test_valid_overridden_methods_hold(self):
        instance = ValidOverriddenMethodNode()
        self.assertEqual(instance.get_probs(index=0), 'overridden_value')


    # Tests that other methods from GrammarNode are not replaced,
    # even if overridden
    def test_invalid_dup_method_not_copied(self):
        instance = InvalidOverriddenMethodNode()
        self.assertNotEqual(
            instance.get_all_possible_children(), 
            'overridden_value'
        )
        

    # Tests that custom class-level properties are copied over correctly
    def test_custom_class_properties_copied_over_correctly(self):
        self.assertEqual(MyConditionNode.TRUE_IND, 0)
        self.assertEqual(MyConditionNode.FALSE_IND, 1)

    # Tests that the key abstract properties from BaseNode
    # are implemented correctly on the new class. Should exhibit 
    # the behavior of GrammarNodes
    def test_base_node_abstract_properties_correctly_implemented(self):
        instance = MyRootNode()

        self.assertIs(instance.token, MyRootNode._TOKEN)
        self.assertIs(instance.label, MyRootNode._LABEL)
        self.assertIs(instance.is_terminal, MyRootNode._IS_TERMINAL)
        self.assertIs(instance.is_root, MyRootNode._IS_ROOT)
        self.assertIs(instance.max_num_children, MyRootNode._MAX_NUM_CHILDREN)
        self.assertIs(
            instance._possible_children_dict, 
            MyRootNode._POSSIBLE_CHILDREN_DICT
        )
        self.assertIs(
            instance._special_probs_dict, 
            MyRootNode._SPECIAL_CHILD_PROBS
        )
        

if __name__ == '__main__':
    unittest.main()