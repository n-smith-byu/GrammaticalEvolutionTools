from ..basic_nodes import TerminalNode

class FactorNode(TerminalNode):
    def _assert_val_is_valid(self, val):
        pass

    def _base_node_init(self, custom_token=None):
        token = "Factor" if custom_token is None else custom_token
        super()._base_node_init(token)

    def _custom_init(self, val):
        self._assert_val_is_valid(val)
        self._val = val

        super()._custom_init()

    def __init__(self):
        self._base_node_init()
        self._custom_init()

        self._token = f"<{self._token}: {self._val}>"

    @property
    def value(self):
        return self._val

    def __call__(self):
        return self._val
    
    def __str__(self):
        return str(self._val)
    
    def __repr__(self):
        return f'<Factor: {self._val}>'