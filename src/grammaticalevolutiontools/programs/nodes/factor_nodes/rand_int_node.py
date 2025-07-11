from .integer_node import IntegerNode

import random

class RandIntegerNode(IntegerNode):
    def _base_node_init(self, custom_token=None):
        token = "RandInt" if custom_token is None else custom_token
        super()._base_node_init(token)

    def _custom_init(self, a, b):
        num = random.randint(a, b)
        super()._custom_init(num)
