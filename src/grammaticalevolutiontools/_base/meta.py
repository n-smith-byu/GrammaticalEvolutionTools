from abc import ABCMeta
import inspect


class BaseNodeMeta(ABCMeta):
    def __call__(cls, *args, **kwargs):
        if cls._init_has_extra_args():
            raise TypeError("Cannot instantiate abstract node class "
                            f"{cls.__name__}. All concrete node classes "
                            "must not require any arguments in their "
                            "__init__ function besides self.")
        
        return ABCMeta.__call__(cls, *args, **kwargs)
    
    def _defines_init_(cls):
        return '__init__' in cls.__dict__

    def _has_abstract_methods(cls):
        try:
            return len(cls.__abstractmethods__) > 0
        except AttributeError:
            return False

    def _init_has_extra_args(cls) -> bool:        
        # Check if __init__ takes args besides self
        init = cls.__init__
        sig = inspect.signature(init)
        params = list(sig.parameters.values())
        
        return len(params) > 1
    
    def is_abstract_class(cls):
        return (
            cls._has_abstract_methods()
            or (
                cls._defines_init_() and
                cls._init_has_extra_args()
            )
        )

    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            return True
        elif isinstance(type(instance), InheritingNodeMeta):
            original_class = type(instance)._ORIGINAL_NODE_CLS
            return (
                isinstance(original_class, type) and 
                issubclass(original_class, cls) 
            )
        else:
            return False
        
    def __subclasscheck__(cls, subclass):
        if super().__subclasscheck__(subclass):
            return True
        elif isinstance(subclass, InheritingNodeMeta):
            original_class = subclass._ORIGINAL_NODE_CLS
            return (
                isinstance(original_class, type) and 
                issubclass(original_class, cls)
            )
        else:
            return False   
    

class InheritingNodeMeta(BaseNodeMeta):

    _ORIGINAL_NODE_CLS = NotImplemented

    def __new__(mcs, name, bases, attrs):
        
        # Create the class
        cls = super().__new__(mcs, name, bases, attrs)
        
        # Verify inherits_from is set and to a valid value
        if cls._ORIGINAL_NODE_CLS is NotImplemented:
            raise TypeError(f"Class {cls.__name__} must implement "
                            f"_ORIGINAL_NODE_CLS property")
        
        if not isinstance(cls._ORIGINAL_NODE_CLS, BaseNodeMeta):
            raise TypeError(
                "_ORIGINAL_NODE_CLS must be an instance of "
                f"{BaseNodeMeta.__name__}."
            )

        return cls
    
