from ..world_object import WorldObject

from typing import TYPE_CHECKING
from abc import ABC
import numbers

if TYPE_CHECKING:
    from .....agents import Agent

class RewardObjectMixin(ABC):
    """
    A mixin class representing a Reward of some kind in a World. 
    
    This class is intended to be used alongside WorldObject to create concrete 
    reward classes (e.g., Food, Gold). It provides logic for tracking the 
    available amount of a resource and dispensing it to agents.

    Note:
        This class cannot be instantiated directly. A concrete subclass must 
        inherit from both RewardObjectMixin and WorldObject.

    Args:
        total_amount (numbers.Real): The total capacity of this reward source.
        base_yield (numbers.Real): The amount of reward given per interaction.

    Attributes:
        remaining (float): Read-only. The current amount left in this 
            reward source.
        base_yield (float): Read-only. The standard amount yielded 
            per interaction.
    """
    def __init__(self, total_amount: numbers.Real, base_yield: numbers.Real):
        """
        Initializes the Reward instance.

        Args:
            total_amount (numbers.Real): The numeric value of this reward. 
                Converted to float.
            base_yield (numbers.Real): The amount to yield every time an 
                agent interacts with this reward.

        Raises:
            ValueError: If total_amount or base_yield is negative.
        """
        if total_amount < 0:
            raise ValueError("Amount of Reward cannot be negative.")
        if base_yield < 0:
            raise ValueError("Base yield cannot be negative.")
        
        self._remaining_amount = float(total_amount)
        self._base_yield = float(base_yield)

    def __new__(cls, *args, **kwargs):
        # Prevents direct instantiation without creating a child class 
        # that inherits from both Reward and WorldObject

        if cls is RewardObjectMixin:
            raise TypeError("Cannot instantiate abstract base class directly")
        if not issubclass(cls, WorldObject):
            raise TypeError(
                "Cannot instantiate a Reward class that does not " \
                "also inherit from WorldObject."
            )
        
        return super().__new__(cls)
    
    def _give_reward(self, agent: 'Agent'):
        """
        Transfers reward to an agent and updates internal state.

        This method should be called inside the :meth:`~.base.WorldObject.trigger` 
        method of any class inheriting from both :class:`WorldObject` and 
        :class:`RewardObjectMixin`.

        Args:
            agent (Agent): The agent that triggered the interaction.

        Returns:
            float: The actual amount given (accounting for exhaustion).
        """
        _yield = min(self._base_yield, self._remaining_amount)
        agent.give_reward(_yield)
        self._remaining_amount -= _yield

    @property
    def remaining(self) -> float:
        """
        The amount of reward left to give.

        Returns:
            float: The current remaining quantity.
        """
        return self._remaining_amount