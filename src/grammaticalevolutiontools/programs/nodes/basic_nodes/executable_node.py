from .terminal_node import TerminalNode

from abc import abstractmethod

class ExecutableNode(TerminalNode):
    def _base_node_init(self, token: str):
        super()._base_node_init(token)

    def _custom_init(self):
        return super()._custom_init()

    @abstractmethod
    def execute(self):
        pass