from grammaticalevolutiontools.meta import BaseNodeMeta, InheritingNodeMeta
from grammaticalevolutiontools.meta import BaseNode

from abc import abstractmethod

import pytest


# - - Utilities - - 


class MockNode(BaseNode):
    def __init__(self):
        super().__init__()

    @property
    def _possible_children_dict(self):
        return {}
    @property
    def _special_probs_dict(self):
        return {}
    @property
    def _all_possible_children(self):
        return set()
    @property
    def max_num_children(self):
        return 0
    @property
    def label(self):
        return "child"
    @property
    def token(self):
        return "C2"
    @property
    def is_terminal(self):
        return True
    @property
    def is_root(self):
        return False

# ---------------------------|
# - - - - - TESTS - - - - - -|
# ---------------------------|

# ----------------------
# ---- BaseNodeMeta ----
# ----------------------

class TestBaseNodeMeta:

    class NewClassAbsMethod(metaclass=BaseNodeMeta):
        def __init__(self):
            pass
        
        @abstractmethod
        def get_val(self):
            return NotImplemented
        
    class NewClassParamsInInit(NewClassAbsMethod):
        def __init__(self, val):
            self.val = val
        
        def get_val(self):
            return self.val
        
    class NewClassDefaultParamsInInit(NewClassAbsMethod):
        def __init__(self, val=None):
            self.val = val
        
        def get_val(self):
            return self.val
        
    class NewClassNoParams(NewClassParamsInInit):
        def __init__(self):
            super(TestBaseNodeMeta.NewClassNoParams, self).__init__(val=None)

    _TEST_NODE = None

    # - - Test Class Utility Methods - -

    @staticmethod
    def test_method__defines_init():
        class ClassNoInit(metaclass=BaseNodeMeta):
            pass

        class ClassWithInit(metaclass=BaseNodeMeta):
            def __init__(self):
                pass

        assert not ClassNoInit._defines_init_()
        assert ClassWithInit._defines_init_()

    @staticmethod
    def test_method__has_abstract_methods():
        class ClassNoAbsMethods(metaclass=BaseNodeMeta):
            pass

        class ClassWithAbsMethods(metaclass=BaseNodeMeta):
            @abstractmethod
            def abstract_method(self):
                pass

        assert not ClassNoAbsMethods._has_abstract_methods()
        assert ClassWithAbsMethods._has_abstract_methods()

    @staticmethod
    def test_method__init_has_extra_args():
        class BaseClassNoExtraArgs(metaclass=BaseNodeMeta):
            def __init__(self):
                pass

        class BaseClassExtraArgs(metaclass=BaseNodeMeta):
            def __init__(self, extra_arg):
                pass

        class ClassInheritedExtraArgs(BaseClassExtraArgs):
            pass

        class ClassInheritedNoExtraArgs(BaseClassNoExtraArgs):
            pass

        assert not BaseClassNoExtraArgs._init_has_extra_args()
        assert not ClassInheritedNoExtraArgs._init_has_extra_args()
        assert BaseClassExtraArgs._init_has_extra_args()
        assert ClassInheritedExtraArgs._init_has_extra_args()

    @staticmethod
    def test_method__is_abstract_class():
        assert TestBaseNodeMeta.NewClassAbsMethod.is_abstract_class()
        assert TestBaseNodeMeta.NewClassParamsInInit.is_abstract_class()
        assert TestBaseNodeMeta.NewClassDefaultParamsInInit.is_abstract_class()
        assert not TestBaseNodeMeta.NewClassNoParams.is_abstract_class()

    # - - Test MetaClass Behavior

    @staticmethod
    def get_test_node():
        if TestBaseNodeMeta._TEST_NODE is None:
            TestBaseNodeMeta._TEST_NODE = TestBaseNodeMeta.NewClassNoParams()
        
        return TestBaseNodeMeta._TEST_NODE

    @staticmethod
    def test_abstract_classes_cannot_be_instantiated():
        with pytest.raises(TypeError):
            TestBaseNodeMeta.NewClassAbsMethod()

        with pytest.raises(TypeError):
            TestBaseNodeMeta.NewClassParamsInInit()

        with pytest.raises(TypeError):
            TestBaseNodeMeta.NewClassDefaultParamsInInit()

    @staticmethod
    def test_non_abstract_class_can_be_instantiated():
        TestBaseNodeMeta.get_test_node()

    @staticmethod
    def test_custom_isinstance__normal_case():
        node = TestBaseNodeMeta.get_test_node()

        assert isinstance(node, TestBaseNodeMeta.NewClassAbsMethod)
        assert not isinstance("NotANode", TestBaseNodeMeta.NewClassAbsMethod)

    @staticmethod
    def test_custom_issubclass__normal_case():
        assert issubclass(TestBaseNodeMeta.NewClassNoParams, 
                          TestBaseNodeMeta.NewClassAbsMethod)
        
        assert not issubclass(TestBaseNodeMeta.NewClassAbsMethod, 
                              TestBaseNodeMeta.NewClassNoParams)


# ----------------------------
# ---- InheritingNodeMeta ----
# ----------------------------

class TestInheritingNodeMeta:

    _VALID_CLASS = None
    
    @staticmethod
    def get_valid_class():
        if TestInheritingNodeMeta._VALID_CLASS is None:
            class ValidInheritingNode(metaclass=InheritingNodeMeta):
                _ORIGINAL_NODE_CLS = MockNode

                def __init__(self):
                    pass
            
            TestInheritingNodeMeta._VALID_CLASS = ValidInheritingNode

        return TestInheritingNodeMeta._VALID_CLASS

    @staticmethod
    def test_inheriting_node_must_define_original_node_class():
        with pytest.raises(TypeError):
            class InvalidClass(metaclass=InheritingNodeMeta):
                def __init__(self):
                    pass

    @staticmethod
    def test_original_node_class_must_be_subclass_of_base_node():
        with pytest.raises(TypeError):
            class InvalidClass(metaclass=InheritingNodeMeta):
                _ORIGINAL_NODE_CLS = "Invalid Type"
                def __init__(self):
                    pass

    @staticmethod
    def test_class_inheriting_from_base_node_is_valid():
        # if doesn't throw an error, then class is valid
        TestInheritingNodeMeta.get_valid_class()


class TestInheritingNodeIntegration:
    @staticmethod
    def get_valid_class():
        if TestInheritingNodeMeta._VALID_CLASS is None:
            class ValidInheritingNode(metaclass=InheritingNodeMeta):
                _ORIGINAL_NODE_CLS = MockNode

                def __init__(self):
                    pass
            
            TestInheritingNodeMeta._VALID_CLASS = ValidInheritingNode

        return TestInheritingNodeMeta._VALID_CLASS
            
    @staticmethod
    def test_issubclass__inheriting_node():
        node_cls = TestInheritingNodeMeta.get_valid_class()

        assert issubclass(node_cls, MockNode)
        assert not issubclass(MockNode, node_cls)

    @staticmethod
    def test_isinstance__inheriting_node():
        node_cls = TestInheritingNodeMeta.get_valid_class()
        node = node_cls()

        assert isinstance(node, MockNode)
        assert not isinstance(MockNode(), node_cls)
        
    