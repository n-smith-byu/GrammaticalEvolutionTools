from ...base import ProgramNode

from enum import IntEnum
from abc import abstractmethod

class AsyncProgramNode(ProgramNode):
    class Status(IntEnum):
        """An enumeration representing the execution status of a program."""
        FAILURE = -1
        RUNNING = 0
        SUCCESS = 1
        RESET = 2

    def _base_node_init(self, token, is_terminal,
                        is_root, num_children,
                        possible_children_dict,
                        special_child_probs):
        super()._base_node_init(
            token=token,
            is_terminal=is_terminal,
            is_root=is_root,
            num_children=num_children,
            possible_children_dict=possible_children_dict,
            special_child_probs=special_child_probs)
        
    def _custom_init(self):
        self._status: AsyncProgramNode.Status = AsyncProgramNode.Status.RESET
        ProgramNode._custom_init(_async=True)

    def _assert_editable(self):
        ProgramNode._assert_editable(self)

    @abstractmethod
    def tick(self) -> AsyncProgramNode.Status:
        pass