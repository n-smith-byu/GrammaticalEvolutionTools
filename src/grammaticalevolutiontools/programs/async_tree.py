from .nodes.asynchronous import AsyncProgramNode, AsyncRootNode
from .base import ProgramTree

class AsyncProgramTree(ProgramTree):

    Status = AsyncProgramNode.Status        # copy/adopt enums

    def __init__(self, root: AsyncProgramNode, autofill: bool=True):
        super().__init__(root, autofill)

        self._root: AsyncRootNode

    def _assert_root_valid(self):
        if self._root is None:
            raise ValueError(
                "`root` cannot be None. Must be either an instance or " \
                "subclass of RootNode"
            )
        if not isinstance(self._root, AsyncRootNode):
            raise TypeError(
                "Program root must be an instance of RootNode."
                f"Found object of type {type(self._root).__name__}"
                )

    def _assert_editable(self):
        if self.running():
            raise ProgramTree.ProgramInProgressError(
                "Cannot modify nodes in a program while it is running. " \
                "Please kill the program or run it to completion first."
            )
        
    def _assert_runnable(self):
        pass        # optional for addins and subclasses

    def tick(self) -> AsyncProgramNode.Status:
        return self._root.tick()
    
    def run(self, n=1):
        for _ in range(n):
            while self.tick() == AsyncProgramNode.Status.RUNNING:
                pass

    def kill(self):
        self._root.reset()
        self._status = AsyncProgramTree.Status.RESET

    def running(self) -> bool:
        return self._status == AsyncProgramTree.Status.RUNNING
    
    @property
    def status(self) -> AsyncProgramTree.Status:
        return self._status
