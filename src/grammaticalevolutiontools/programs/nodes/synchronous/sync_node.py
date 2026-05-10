from ...base.program_node import ProgramNode

from typing import Type, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...sync_tree import SyncProgramTree

class SyncProgramNode(ProgramNode):
    def _base_node_init(
        self, 
        token: str, 
        is_terminal: bool, 
        is_root: bool, 
        num_children: int, 
        label: Optional[str] = None,
        possible_children_dict: Optional[
                dict[int, list[Type['SyncProgramNode']]]
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
        super()._custom_init(_async=False)

        self._program: 'SyncProgramTree'
        self._parent: SyncProgramNode

    def _assert_editable(self):
        ProgramNode._assert_editable(self)