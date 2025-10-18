from grammaticalevolutiontools.nodes import BaseNodeMeta, InheritingNodeMeta
from ..utilities_ import BasicGrammar as bg

from abc import abstractmethod

import pytest


# - - BaseNodeMeta - - 

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
    def test_defines_init():
        class ClassNoInit(metaclass=BaseNodeMeta):
            pass

        class ClassWithInit(metaclass=BaseNodeMeta):
            def __init__(self):
                pass

        assert not ClassNoInit._defines_init_()
        assert ClassWithInit._defines_init_()

    @staticmethod
    def test_has_abstract_methods():
        class ClassNoAbsMethods(metaclass=BaseNodeMeta):
            pass

        class ClassWithAbsMethods(metaclass=BaseNodeMeta):
            @abstractmethod
            def abstract_method(self):
                pass

        assert not ClassNoAbsMethods._has_abstract_methods()
        assert ClassWithAbsMethods._has_abstract_methods()

    @staticmethod
    def test_init_has_extra_args():
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
    def test_is_abstract_class():
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
    def test_custom_isinstance_normal():
        node = TestBaseNodeMeta.get_test_node()

        assert isinstance(node, TestBaseNodeMeta.NewClassAbsMethod)
        assert not isinstance("NotANode", TestBaseNodeMeta.NewClassAbsMethod)

    @staticmethod
    def test_custom_isinstance_inheriting_node():

        class BasicInheritingNode(metaclass=InheritingNodeMeta):
                _ORIGINAL_NODE_CLS = TestBaseNodeMeta.NewClassNoParams

                def __init__(self):
                    pass

        instance = BasicInheritingNode()
        
        assert isinstance(instance, TestBaseNodeMeta.NewClassNoParams)

    @staticmethod
    def test_custom_issubclass_normal():
        assert issubclass(TestBaseNodeMeta.NewClassNoParams, 
                          TestBaseNodeMeta.NewClassAbsMethod)
        
        assert not issubclass(TestBaseNodeMeta.NewClassAbsMethod, 
                              TestBaseNodeMeta.NewClassNoParams)

    @staticmethod
    def test_custom_issubclass_inheriting_node():
        class BasicInheritingNode(metaclass=InheritingNodeMeta):
                _ORIGINAL_NODE_CLS = TestBaseNodeMeta.NewClassNoParams

                def __init__(self):
                    pass

        assert issubclass(BasicInheritingNode, 
                          TestBaseNodeMeta.NewClassNoParams) 


# - - InheritingNodeMeta - - 

class TestInheritingNodeMeta:

    _VALID_CLASS = None
    
    @staticmethod
    def get_valid_class():
        if TestInheritingNodeMeta._VALID_CLASS is None:
            class InheritingNodeValid(metaclass=InheritingNodeMeta):
                _ORIGINAL_NODE_CLS = bg.CodeNode

                def __init__(self):
                    pass
            
            TestInheritingNodeMeta._VALID_CLASS = InheritingNodeValid

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
        TestInheritingNodeMeta.get_valid_class()