from typing import Sequence, Union
import numpy as np


class GridPosition:

    __array_priority__ = 10     # for predence with __eq__ with numpy arrays on the left side of ==

    def __init__(self, coords:Union[Sequence, 'GridPosition']):
        if isinstance(coords, GridPosition):
            self._i, self._j = coords.coords
        elif self.__is_valid_coord(coords):
            self._i, self._j = list(coords)
        else:
            raise TypeError('x must be of type integer, an array-like object of integer values and length 2, or a Position object.')
            
        self._i = int(self._i)
        self._j = int(self._j)

    def __is_array_like(self, obj):
        if isinstance(obj, np.ndarray):
            if obj.ndim == 0:
                return False

        return (hasattr(obj, '__array__') or (hasattr(obj, '__iter__')) and not np.isscalar(obj))
    
    def __is_valid_coord(self, obj):    
        return self.__is_array_like(obj) and len(list(obj)) == 2 and np.issubdtype(np.array(obj).dtype, np.integer)
    
    @property
    def coords(self):
        return np.array(self)         # reverse to put in [i,j] form ([height, width])
    
    def __eq__(self, other):
        try:
            _other = GridPosition(other)
        except (ValueError, TypeError) as ex:
            return False
        
        return np.all(self.coords == _other.coords)
    
    def __iter__(self):
        return iter(self.coords)
    
    def __add__(self, other):
        _other = np.array(other)

        try:
            return GridPosition(self.coords + _other)
        except Exception as ex:
            raise TypeError(
                "'other' must be scalar or convertible to a Position object"
            )
        
        
        
    def __radd__(self, other):
        return self + other
    
    def __getitem__(self, index):
        return self.coords[index]
    
    def __array__(self):
        return np.array([self._i, self._j])
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return f'({self._i}, {self._j})'
    
    def __hash__(self):
        return hash((self._i, self._j))
    
