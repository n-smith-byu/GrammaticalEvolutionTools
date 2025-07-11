from ...worlds.objects import WorldObject

from typing import TYPE_CHECKING
from abc import ABC
import numbers

if TYPE_CHECKING:
    from ...agents import Agent

class Reward(ABC):
    """
    A class representing a Reward of some kind in a GrammaticalEvolution World.

    Attributes:
        type (str): A read-only property. The string label for the type of this reward.
        amount (float): A read-only property. The amount of this reward.
        pos (Position): A read-only property. The position of this reward in the world. 
        __world (World): A private property. The world to which this reward belongs. 
    """
    def __init__(self, total_amount: numbers.Real, base_yield: numbers.Real):
        """
        Initializes the Reward instance.

        Args:
            total_amount(numbers.Real): The numeric value of this reward. Gets converted to float.
            base_yield(numbers.Real): The amount to yield every time an agent interacts with this reward.
        """
        if total_amount < 0:
            raise ValueError("Amount of Reward cannot be negative.")
        if base_yield < 0:
            raise ValueError("Base yield cannot be negative.")
        
        self._remaining_amount = float(total_amount)
        self._base_yield = float(base_yield)

    def __new__(cls, *args, **kwargs):
        # This prevents direct instantiation without creating a child class that inherits from both Reward and WorldObject

        if cls is Reward:
            raise TypeError("Cannot instantiate abstract base class directly")
        if not issubclass(cls, WorldObject):
            raise TypeError("Cannot instantiate a Reward class that does not also inherit from WorldObject.")
        
        return super().__new__(cls)

    @property
    def remaining(self) -> float:
        """
        Gets the amount of this reward.

        Returns:
            float: the amount of this reward.
        """
        return self._remaining_amount

    
    