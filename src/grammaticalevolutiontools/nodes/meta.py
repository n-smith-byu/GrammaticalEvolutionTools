from abc import ABCMeta
import inspect


class BaseNodeMeta(ABCMeta):
    """
    Metaclass for BaseNode, enforcing custom abstractness rules for node classes.

    This metaclass extends `abc.ABCMeta` to provide additional checks beyond
    Python's standard abstract base class mechanism. It ensures that concrete
    (non-abstract) subclasses of `BaseNode` adhere to specific initialization
    constraints and correctly implement all required abstract properties and methods.

    It also customizes `isinstance()` and `issubclass()` checks to properly
    handle classes created with :class:`InheritingNodeMeta`. This allows instances
    and subclasses of "aliased" node classes to be correctly recognized as instances
    or subclasses of their `_ORIGINAL_NODE_CLS` within the `BaseNode` hierarchy.
    """

    def __call__(cls, *args, **kwargs):
        """
        Custom `__call__` method for class instantiation.

        This method is invoked when an attempt is made to create an instance
        of a class using this metaclass. It prevents the instantiation of
        concrete `BaseNode` subclasses if their `__init__` method
        requires arguments other than `self`, ensuring a consistent
        instantiation pattern across the node hierarchy.

        Parameters
        ----------
        *args : tuple
            Positional arguments passed to the class constructor.
        **kwargs : dict
            Keyword arguments passed to the class constructor.

        Returns
        -------
        object
            An instance of the class if it passes the abstraction checks.

        Raises
        ------
        TypeError
            If attempting to instantiate an abstract class or a concrete class
            whose `__init__` method takes extra arguments.
        """
        if cls._init_has_extra_args():
            raise TypeError("Cannot instantiate abstract node class "
                            f"{cls.__name__}. All concrete node classes "
                            "must not require any arguments in their "
                            "__init__ function besides self.")
        
        return ABCMeta.__call__(cls, *args, **kwargs)
    
    def _defines_init_(cls):
        """
        Checks if the class directly defines an `__init__` method.

        This method looks at the class's own dictionary (`__dict__`) to determine
        if `__init__` is explicitly defined within the class itself, rather than
        being inherited from a parent class.

        Returns
        -------
        bool
            `True` if `__init__` is defined in the class's `__dict__`, `False` otherwise.
        """
        return '__init__' in cls.__dict__

    def _has_abstract_methods(cls):
        """
        Checks if the class has any unimplemented abstract methods.

        This method leverages Python's built-in `__abstractmethods__` attribute
        (managed by `abc.ABCMeta`) to determine if a class is still abstract.

        Returns
        -------
        bool
            `True` if the class has one or more abstract methods, `False` otherwise.
        """
        try:
            return len(cls.__abstractmethods__) > 0
        except AttributeError:
            return False

    def _init_has_extra_args(cls) -> bool:
        """
        Determines if the class's `__init__` method accepts arguments beyond `self`.

        This is a custom abstractness check. A concrete `BaseNode` subclass
        is considered "abstract" by this metaclass if it requires arguments
        in its `__init__` method beyond the mandatory `self` parameter. This
        enforces that all instantiable node types have a simple, parameterless
        constructor (after `self`).

        Returns
        -------
        bool
            `True` if `__init__` has parameters other than `self`, `False` otherwise.
        """ 
        # Check if __init__ takes args besides self
        init = cls.__init__
        sig = inspect.signature(init)
        params = list(sig.parameters.values())
        
        return len(params) > 1
    
    def is_abstract_class(cls):
        """
        Determines if a class is considered abstract by this metaclass's rules.

        A class is abstract if:

        1. It has standard `abc` abstract methods that haven't been implemented.
        2. It defines its own `__init__` method and that `__init__` method
           requires arguments other than `self`.

        Returns
        -------
        bool
            `True` if the class is abstract according to `BaseNodeMeta`'s rules,
            `False` otherwise.
        """
        return (
            cls._has_abstract_methods()
            or (
                cls._defines_init_() and
                cls._init_has_extra_args()
            )
        )

    def __instancecheck__(cls, instance):
        """
        Customizes `isinstance()` behavior for BaseNode and its derivatives.

        This method is called when `isinstance(instance, BaseNode)` or
        `isinstance(instance, SomeBaseNodeSubclass)` is evaluated.
        It extends the default `abc.ABCMeta` behavior to correctly handle
        instances of classes created with `InheritingNodeMeta`. If an instance's
        type is an `InheritingNodeMeta`-derived class, this method checks if
        its `_ORIGINAL_NODE_CLS` is a subclass of `cls`, effectively allowing
        the instance to be recognized as an instance of `cls` via type-aliasing.

        Parameters
        ----------
        instance : object
            The object to check.

        Returns
        -------
        bool
            `True` if the instance is considered an instance of `cls`, `False` otherwise.
        """
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
        """
        Customizes `issubclass()` behavior for BaseNode and its derivatives.

        This method is called when `issubclass(subclass, BaseNode)` or
        `issubclass(subclass, SomeBaseNodeSubclass)` is evaluated.
        It extends the default `abc.ABCMeta` behavior to correctly handle
        classes created with `InheritingNodeMeta`. If `subclass` itself is
        an `InheritingNodeMeta`-derived class, this method checks if its
        `_ORIGINAL_NODE_CLS` is a subclass of `cls`, effectively allowing
        the `subclass` to be recognized as a subclass of `cls` via type-aliasing.

        Parameters
        ----------
        subclass : type
            The class to check.

        Returns
        -------
        bool
            `True` if `subclass` is considered a subclass of `cls`, `False` otherwise.
        """
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
    """
    Metaclass that allows a class to register as subclass of another
    `BaseNode`-derived class, regardless of direct inheritance or behavioral implementation.

    This metaclass provides a mechanism for **aliasing** or **type-masking** within
    the `BaseNode` hierarchy. When a class uses `InheritingNodeMeta`, it can declare
    itself to be treated as a subclass of `_ORIGINAL_NODE_CLS` for
    `isinstance()` and `issubclass()` checks, even if its actual methods and logic
    are entirely different. This is useful for creating specialized node types
    that need to satisfy type checks for a different `BaseNode` type without
    inheriting its full implementation.

    Subclasses using this metaclass **must** specify the target `BaseNode`-derived
    class via the `_ORIGINAL_NODE_CLS` attribute.
    """

    _ORIGINAL_NODE_CLS = NotImplemented
    """
    Class attribute required for `InheritingNodeMeta` classes.

    This should be set to the `BaseNode`-derived class type that this new class
    should "register as" for `isinstance()` and `issubclass()` checks. It's used
    by `BaseNodeMeta`'s type-checking methods to enable this custom type recognition.
    """

    def __new__(mcs, name, bases, attrs):
        """
        Custom `__new__` method for class creation.

        This method is called before the class `__init__` method. It first
        creates the new class using the parent metaclass's `__new__`, then
        performs validation to ensure that `_ORIGINAL_NODE_CLS` is correctly
        set to a valid `BaseNode`-derived class.

        Parameters
        ----------
        mcs : type
            The metaclass itself.
        name : str
            The name of the new class being created.
        bases : tuple
            A tuple of base classes for the new class.
        attrs : dict
            A dictionary of attributes for the new class.

        Returns
        -------
        type
            The newly created class.

        Raises
        ------
        TypeError
            If `_ORIGINAL_NODE_CLS` is not set or is not an instance of `ABCMeta`
            (implying it's not a proper `BaseNode`-derived class).
        """
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
    
