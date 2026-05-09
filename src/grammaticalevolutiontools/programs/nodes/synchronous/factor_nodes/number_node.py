from .factor_node import FactorNode

from numbers import Number

class NumberNode(FactorNode):
    def _assert_val_is_valid(self, val):
        if not isinstance(val, Number):
            raise TypeError("Value in a NumberNode must be of type Number. "
                            f"Found val of type {type(val).__name__}")

    def _base_node_init(self, custom_token=None):
        token = "Number" if custom_token is None else custom_token
        super()._base_node_init(token)

    def _custom_init(self, num: Number):
        super()._custom_init(val=num)


        

        

        