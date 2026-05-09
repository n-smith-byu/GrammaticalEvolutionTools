from .number_node import NumberNode

from numbers import Integral

class IntegerNode(NumberNode):
    def _assert_val_is_valid(self, val):
        if not isinstance(val, Integral):
            raise TypeError("Value in an IntegerNode must be "
                            "of type Integral. Found val of type "
                            f"{type(val).__name__}")
        
    def _base_node_init(self, custom_token=None):
        token = "Integer" if custom_token is None else custom_token
        super()._base_node_init(token)

    def _custom_init(self, num: Integral):        
        super()._custom_init(num)
        

        
