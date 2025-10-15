from .grammar_node import GrammarNode
from ..programs.nodes import ProgramNode
from .._base_node import InheritingNodeMeta

from typing import Type


_custom_attribute_cache: dict[type, list[str]] = {}

# Decorator: Converts a ProgramNode subclass into a GrammarNode-compatible class
def as_grammar_node(node_cls: Type[ProgramNode]):

    if node_cls.is_abstract_class():
        raise TypeError("Cannot Create GrammarNode from an abstract class. "
                       f"Class at fault: {node_cls}")
    
    _METHODS_TO_EXCLUDE = {"_base_node_init", 
                           "_custom_init",
                           "_init_possible_children",
                           "_set_possible_children",
                           "_set_child_probs",
                           "_assert_vals_valid",
                           "_assert_possible_child_type_is_valid"}
    
    # These are class attributes the ProgramNode class cannot have defined
    # because they will conflict with GrammarNode
    invalid_attributes = {"_ORIGINAL_NODE_CLS",
                          "_MAX_NUM_CHILDREN",
                          "_POSSIBLE_CHILDREN_DICT",
                          "_SPECIAL_CHILD_PROBS",
                          "_IS_TERMINAL",
                          "_IS_ROOT",
                          "_TOKEN",
                          "_LABEL",
                          "_GRAMMAR",
                          "_RESOLVED",
                          "_ALL_POSSIBLE_CHILDREN"}

    # These are methods the user is allowed to override
    overridable_methods = {"add_child",
                           "pop_child",
                           "replace_child",
                           "remove_all_children",
                           "_get_properties_to_pass_to_children",
                           "_get_properties_for_removed_child",
                           "_on_collect_descendants_add",
                           "_on_collect_descendants_pop",
                           "_rollback_add",
                           "_rollback_pop",
                           "get_probs",
                           "__str__",
                           "__repr__"}
    
    # Create the new GrammarNode class
    class ProgramNodeWrapper(node_cls):
            
        # Overwrites the logic to check if possible children are valid.
        # This check will now be done by the GrammarNode class.
        # This allows strings to pass the check and be 
        # resolved later.
        @staticmethod
        def _assert_possible_child_type_is_valid(node_type: Type):
            return True    

        def __init__(self):
            super()._base_node_init()

            # creates a list to track attributes set by _custom_init
            # and caches them for efficiency
            if node_cls not in _custom_attribute_cache:
                _custom_attribute_cache[node_cls] = []
                
                old_self_dict = self.__dict__.copy()

                super()._custom_init()
                for key in self.__dict__:
                    if key not in old_self_dict:
                        _custom_attribute_cache[node_cls].append(key)

            else:
                super()._custom_init()

    attr_generator = ProgramNodeWrapper()

    class NewNodeClass(GrammarNode, metaclass=InheritingNodeMeta):

        _MAX_NUM_CHILDREN = attr_generator._max_num_children
        _POSSIBLE_CHILDREN_DICT = attr_generator._possible_children_dict
        _SPECIAL_CHILD_PROBS = attr_generator._special_probs_dict
        _IS_TERMINAL = attr_generator._is_terminal
        _IS_ROOT = attr_generator._is_root
        _TOKEN = attr_generator._token
        _LABEL = attr_generator._label

        _ORIGINAL_NODE_CLS = node_cls        # ensures new class will register as 
                                             # a subclass of node_cls

        # function to get around the issue of _custom_init calling super()
        def _extract_custom_behavior(self):
            # calls _custom_init on the instance created earlier
            attr_generator._custom_init()

            # copies attributes set by _custom_init to this instance
            new_attributes = {}
            for attr in _custom_attribute_cache[node_cls]:
                new_attributes[attr] = attr_generator.__dict__[attr]

            return new_attributes

        def __init__(self):
            GrammarNode.__init__(self)

            # copy the behavior of _custom_init from the original node class
            custom_attributes = self._extract_custom_behavior()
            self.__dict__.update(custom_attributes)
                

    # Copy over class methods and properties
    overridden = set()
    for base_class in node_cls.__mro__:
        for attr_name, src_attr in base_class.__dict__.items():
            if attr_name in invalid_attributes:
                # throws an error if new class tries to define class-level properties 
                # explcitly in conflict with key GrammarNode properties.
                raise AttributeError("node_cls defines attributes that "
                                     "conflict with GrammarNode attributes.\n"
                                     f"Attribute at fault: {attr_name}")
            
            # Conflicting methods are simply not copied over, 
            # unless listed in overridable_methods. 
            if attr_name in _METHODS_TO_EXCLUDE \
                    or (hasattr(NewNodeClass, attr_name) 
                        and attr_name not in overridable_methods) \
                    or attr_name in overridden:
            
                continue
            else:
                setattr(NewNodeClass, attr_name, src_attr)
                overridden.add(attr_name)

    # Ensures new class has the same name and other properties as the original 
    NewNodeClass.__name__ = node_cls.__name__
    NewNodeClass.__qualname__ = node_cls.__qualname__
    NewNodeClass.__module__ = node_cls.__module__
    NewNodeClass.__doc__ = node_cls.__doc__

    return NewNodeClass