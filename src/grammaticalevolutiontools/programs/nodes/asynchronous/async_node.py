from ...base import ProgramNode

from enum import IntEnum
from abc import abstractmethod

from typing import Optional, Type

class AsyncProgramNode(ProgramNode):
    class Status(IntEnum):
        """An enumeration representing the execution result/status of an AsyncProgramNode."""
        FAILURE = -1
        RUNNING = 0
        SUCCESS = 1
        RESET = 2

    def _base_node_init(
        self, 
        token: str, 
        is_terminal: bool, 
        is_root: bool, 
        num_children: int, 
        label: Optional[str] = None,
        possible_children_dict: Optional[
                dict[int, list[Type['AsyncProgramNode']]]
            ] = None,
        special_child_probs: Optional[
                dict[int, list[float]]
            ] = None
        ):

        super()._base_node_init(
            token=token,
            is_terminal=is_terminal,
            is_root=is_root,
            num_children=num_children,
            possible_children_dict=possible_children_dict,
            special_child_probs=special_child_probs,
            label=label
            )
        
    def _custom_init(self):
        self._status: AsyncProgramNode.Status = AsyncProgramNode.Status.RESET
        ProgramNode._custom_init(_async=True)

    def _assert_editable(self):
        ProgramNode._assert_editable(self)

    def is_running(self):
        return self._status == AsyncProgramNode.Status.RUNNING

    @abstractmethod
    def tick(self) -> AsyncProgramNode.Status:
        pass