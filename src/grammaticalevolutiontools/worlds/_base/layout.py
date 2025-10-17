from abc import ABC, abstractmethod

from ..objects import WorldObject

from typing import Type, Self

class WorldLayout(ABC):
    class LayoutLockedError(RuntimeError):
        def __init__(self, msg: str):
            super(WorldLayout.LayoutLockedError, self).__init__(msg)

    class LayoutNotLockedError(RuntimeError):
        def __init__(self, msg: str):
            super(WorldLayout.LayoutNotLockedError, self).__init__(msg)

    class MapNotInitializedError(RuntimeError):
        def __init__(self, msg: str):
            super(WorldLayout.MapNotInitializedError, self).__init__(msg)

    class AlreadyInitializedError(RuntimeError):
        def __init__(self, msg: str):
            super(WorldLayout.AlreadyInitializedError, self).__init__(msg)

    def __init__(self):
        self._locked = False

        # -- Assertions --

    def _assert_initialized(self, msg = 'World has not been initialized.'):
        if not self.initialized():
            raise WorldLayout.MapNotInitializedError(msg)
        
    def _assert_not_initialized(self, msg = 'This world has already been initialized. Cannot initialize again.'):
        if self.initialized():
            raise WorldLayout.AlreadyInitializedError(msg)
        
    def _assert_locked(self, msg= 'Layout not locked.'):
        if not self._locked:
            raise WorldLayout.LayoutNotLockedError(msg)
        
    def _assert_not_locked(self, msg='Layout has been locked and is no longer mutable.'):
        if self._locked:
            raise WorldLayout.LayoutLockedError(msg)
        
    def _assert_valid_obj_class(self, obj_class: type):
        if not isinstance(obj_class, type) or not issubclass(obj_class, WorldObject):
            raise TypeError('Provided class not an instance of GrammaticalEvolutionTools.World.Objects.WorldObject')
        
    # - - - - 

    def lock(self) -> Self:
        self._assert_initialized(msg='Cannot lock layout before it has been initialized.')
        self._locked = True

        return self

    def locked(self):
        return self._locked
    
    @abstractmethod
    def initialized(self) -> bool:
        return NotImplemented
    
    @abstractmethod
    def copy(self, lock=True):
        return NotImplemented


