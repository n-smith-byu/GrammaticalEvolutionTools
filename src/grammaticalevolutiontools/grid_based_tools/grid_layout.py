from ..worlds.layouts import WorldLayout
from .grid_world_object import GridWorldObject
from .grid_position import GridPosition

import numpy as np
from typing import Type
import numbers

class GridLayout(WorldLayout):

    class InvalidPositionError(ValueError):
        def __init__(self, msg):
            super(GridLayout.InvalidPositionError, self).__init__(msg)

    class DuplicateSymbolError(RuntimeError):
        def __init__(self, msg):
            super(GridLayout.DuplicateSymbolError, self).__init__(msg)

    class ParsingError(RuntimeError):
        def __init__(self, msg):
            super(GridLayout.ParsingError, self).__init__(msg)

    def __init__(self):
        super(GridLayout, self).__init__()

        self.__width: int = None
        self.__height: int = None

        self.__object_positions: dict[GridPosition, Type[GridWorldObject]]

    def initialized(self) -> bool:
        return self.__width is not None and self.__height is not None
    
    # -- Helper Functions --

    def space_within_map_bounds(self, pos: GridPosition) -> bool:
        """
        Checks if a Position object (or equivalent) has coordinates within the boundaries of the World.

        Arguments:
            pos (Position): A Position object or an equivalent tuple, array, etc. represening a pair of coordinates in the world. 

        Returns:
            bool: Whether or not the coordinates provided are within the boundaries of the World.
        """
        _pos = GridPosition(pos).coords
        return np.all(_pos >= 0) and _pos[0] < self.height and _pos[1] < self.width
    
    def position_taken(self, pos: GridPosition) -> bool:
        _pos = GridPosition(pos)
        return _pos in self.__object_positions
    
    # -- Assertions --

    def _assert_initialized(self, msg='Cannot modify objects until width and height are set.'):
        super()._assert_initialized(msg)
        
    def _assert_not_initialized(self):
        super()._assert_not_initialized()
        
    def _assert_space_available(self, pos: GridPosition):
        if self.position_taken(pos):
            raise GridLayout.InvalidPositionError('Position already claimed by another object.')
        
    def _assert_space_valid_and_open(self, pos: GridPosition):
        self.assert_space_within_map_bounds(pos)
        self._assert_space_available(pos)
        
    def _assert_symbol_valid(self, new_symbol, seen_symbols: set[str]) -> tuple[bool, Exception]: 
        if type(new_symbol) != str:
            raise TypeError(f'All symbols must be of type string. Found symbol of type {type(new_symbol).__name__}.')
        if len(new_symbol) != 1:
            raise ValueError(f'All symbols must be a string of length 1. Found symbol of length {len(new_symbol)}.')
        if new_symbol.isspace():
            raise ValueError(f"Symbols cannot be whitespace characters. Symbol at fault: '{new_symbol}'.")
        if new_symbol in seen_symbols:
            raise ValueError('Repeat symbols found. Each reward, and empty space symbols must be unique.')
        
    def _assert_width_and_height_valid(self, width, height):
        if not isinstance(width, numbers.Integral) or not isinstance(height, numbers.Integral):
            raise TypeError('height and width must be integers.')
        if height <= 0 or width <= 0:
            raise ValueError('height and width dimensions must be positive integers')
        
    def assert_space_within_map_bounds(self, pos: GridPosition):
        _pos = GridPosition(pos)
        if not self.space_within_map_bounds(pos):
            raise GridLayout.InvalidPositionError('pos not within the bounds of the World.')

    # -- Modifying the Layout

    def set_dims(self, width: int, height: int):
        self._assert_not_locked()
        self._assert_not_initialized()
        self._assert_width_and_height_valid(width, height)
        
        self.__width = int(width)
        self.__height = int(height)

        self.__object_positions = {}

    def add_object(self, obj_class: Type[GridWorldObject], pos: GridPosition):
        self._assert_not_locked()
        self._assert_initialized()
        self._assert_space_valid_and_open(pos)
        self._assert_valid_obj_class(obj_class)

        _pos = GridPosition(pos)
        self.__object_positions[_pos] = obj_class
    
    def get_object_positions(self) -> dict[GridPosition, Type[GridWorldObject]]:
        if self.__object_positions is not None:
            return self.__object_positions.copy()

    @property
    def width(self):
        if not self.initialized:
            raise GridLayout.MapNotInitializedError('width attribute has not been set')
        return self.__width
    
    @property
    def height(self):
        if not self.initialized:
            raise GridLayout.MapNotInitializedError('height attribute has not been set')
        return self.__height
    
    def copy(self, lock=True):

        self._assert_locked(msg='Creating a copy requires the GridLayout to be locked. The copy can be left unlocked by passing in lock=False')

        _dup = GridLayout()
        _dup.set_dims(self.__width, self.__height)

        for pos, obj_class in self.__object_positions.items():
            _dup.add_object(obj_class, pos)

        if lock:
            _dup.lock()

        return _dup

    
    # -- LOADING MAPS FROM FILES --

    def __create_symbol_map(self, obj_symbols: list[str], obj_classes: list[Type[GridWorldObject]],
                              empty_space_symbol: str):
        """
            Maps lists of symbol to object types for use in parsing a grid layout from a file.
            Populates two variables: self.__symbol_to_object_type_dict and self.__empty_space_symbol.
            Also verifies all symbols and object classees are valid. 

            Arguments:
                obj_symbols (list[str]): A list of single character strings corresponding to the list of WorldObject types (Including Reward types). 
                                         Each character should be unique and map to a single WorldObject type. 
                obj_classes (list[Type[WorldObject]]): A list of WorldObject classes that the symbols provided in obj_symbols should map to. The two lists will be zipped together. 
                empty_space_symbol (str): A single character string that will be used to represent where empty spaces with no WorldObjects will be in the World Layout. 
                
        """
        if len(obj_symbols) != len(obj_classes):
            raise ValueError(f'Size Mismatch. Size of obj_symbols list must match size of obj_classes ' + \
                             f'Found obj_symbols of size {len(obj_symbols)} and obj_classes of size {len(obj_classes)}.')

        self.__symbol_to_obj_class_dict: dict[str, Type[GridWorldObject]] = {}
        seen_symbols = set()

        for symbol in obj_symbols + [empty_space_symbol]:
            self._assert_symbol_valid(symbol, seen_symbols)            
            seen_symbols.add(symbol)

        for obj_class in obj_classes:
            self._assert_valid_obj_class(obj_class)

        for symbol, obj_class in zip(obj_symbols, obj_classes):
            # Map symbol to appropriate object
            self.__symbol_to_obj_class_dict[symbol] = obj_class
            
        self.__empty_space_symbol = empty_space_symbol

    def __parse_file(self, file_path: str):
        _temp_obj_pos_dict: dict[GridPosition, Type[GridWorldObject]] = {}

        with open(file_path, "r") as FILE:

            lines = [line.strip() for line in FILE]

            if not lines:
                _width = 0
            else:
                _width = None
            _height = 0
                
            # Parse file first, make sure everything valid
            for i, line in enumerate(lines):
                if _width is None:
                    _width = len(line)
                if len(line) != _width:
                        raise GridLayout.ParsingError('Inconsistent Row Widths')
                for j in range(len(line)):
                    curr_symbol = line[j]

                    if curr_symbol in self.__symbol_to_obj_class_dict:
                        object_type = self.__symbol_to_obj_class_dict[curr_symbol]
                        _temp_obj_pos_dict[GridPosition((i,j))] = object_type

                    elif curr_symbol == self.__empty_space_symbol:
                        continue
                    else:
                        raise GridLayout.ParsingError('Encountered a symbol not in the obj_symbol list provided.' + \
                                                     f'Unrecognized Symbol: {curr_symbol}')

                _height += 1

        return _width, _height, _temp_obj_pos_dict

    def load_map_layout_from_file(self, file_path: str, obj_symbols: list[str], obj_classes: list[Type[GridWorldObject]],
                                  empty_space_symbol: str, lock=True):
        
        self._assert_not_locked()
        self._assert_not_initialized()
        self.__create_symbol_map(obj_symbols, obj_classes, empty_space_symbol)

        width, height, temp_obj_pos_dict = self.__parse_file(file_path)

        # actually set all values
        self.set_dims(width, height)
        for pos, obj_class in temp_obj_pos_dict.items():
            self.add_object(obj_class, pos)

        if lock:
            self.lock()


    # -- LOADING MAP FROM DICTIONARY --

    def load_map_layout_from_dict(self, map_width: int, map_height: int, 
                                  obj_pos_dict: dict[Type[GridWorldObject], list[GridPosition]] = None,
                                  pos_obj_dict: dict[GridPosition, Type[GridWorldObject]] = None, 
                                  lock=True):
        
        self._assert_not_locked()
        self._assert_not_initialized()
        self.set_dims(map_width, map_height)

        if obj_pos_dict is not None and pos_obj_dict is not None:
            raise ValueError("obj_pos_dict and pos_obj_dict can't both be used. Use one or the other.")
        if obj_pos_dict is None and pos_obj_dict is None:
            raise ValueError("obj_pos_dict and pos_obj_dict can't both be None. Must specify one or the other, even if empty dict.")
        
        if obj_pos_dict is not None:
            for obj_class, pos_list in obj_pos_dict.items():
                for pos in pos_list:
                    self.add_object(obj_class, pos)
        else:
            for pos, obj_class in pos_obj_dict.items():
                self.add_object(obj_class, pos)

        if lock:
            self.lock()



