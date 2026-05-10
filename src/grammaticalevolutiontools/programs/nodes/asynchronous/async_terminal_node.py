from .async_node import AsyncProgramNode

class AsyncTerminalNode(AsyncProgramNode):
    def _base_node_init(self, token: str):
        super()._base_node_init(
            token=token,
            is_terminal=True,
            is_root=False,
            num_children=0,
            possible_children_dict=None
        )