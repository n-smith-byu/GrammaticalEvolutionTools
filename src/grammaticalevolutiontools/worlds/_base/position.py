import numpy as np

from collections.abc import Sequence
from numbers import Real


class WorldPosition(Sequence):

    __array_priority__ = 10     # for predence with __eq__ with numpy arrays on the left side of ==
    _required_length: int | None = None
    _dtype = Real

    def __init__(self, coords: Sequence):
        if self._required_length is None:
            raise TypeError("Can not instantiate a WorldPosition subclass without "
                            "defining `_required_length` class method")
        
        self._assert_coords_valid(coords)
        self._coords = tuple(int(i) for i in coords)

        super().__init__()

    def __init_subclass__(cls):
        super().__init_subclass__()
        if (cls._required_length is not None) and (not isinstance(cls._required_length, cls._dtype)):
            raise TypeError("`_required_length` must be an integer")

    def _is_array_like(self, obj):
        if isinstance(obj, np.ndarray):
            if obj.ndim == 0:
                return False

        return (hasattr(obj, '__array__') or (hasattr(obj, '__iter__')) and not np.isscalar(obj))
    
    def _assert_coords_valid(self, coords: Sequence):
        if not self._is_array_like(coords):
            raise TypeError("`coords` must be convertible to a numpy array")
        if len(coords) != self._required_length:
            raise ValueError(
                f"{type(self).__name__} requires coords of length {self._required_length}. "
                f"Found object of length {len(coords)}"
                )
        if not all(isinstance(x, self._dtype) for x in coords):
            raise ValueError(
                f"all element of `coords` must be of type {self._dtype.__name__}"
            )
        
    @property
    def coords(self):
        return np.array(self)        
    
    def __eq__(self, other):
        try:
            _other = type(self)(other)
        except (ValueError, TypeError) as ex:
            return False
        
        return np.all(self.coords == _other.coords)
    
    def __iter__(self):
        return iter(self._coords)
    
    def __add__(self, other):
        _other = np.array(other)

        try:
            return type(self)(self.coords + _other)
        except Exception as ex:
            raise TypeError(
                f"'other' must be scalar or convertible to a {type(self).__name__} object"
            )
        
    def __radd__(self, other):
        return self + other
    
    def __getitem__(self, index):
        return self.coords[index]
    
    def __array__(self):
        return np.array(self._coords)
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return str(self._coords)
    
    def __hash__(self):
        return hash(self._coords)
    
    def __len__(self):
        return len(self._coords)