from ...program_node import ProgramNode

class TerminalNode(ProgramNode):
    def _base_node_init(self, token: str):
        super()._base_node_init(
            token,
            is_terminal=True,
            is_root=False,
            num_children=0,
            possible_children_dict=None
        )

    def _custom_init(self):
        return super()._custom_init()
