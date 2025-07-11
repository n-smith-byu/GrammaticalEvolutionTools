from .grid_world_object import GridWorldObject
from ..worlds.rewards import Reward

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .grid_world import GridWorld
    from .grid_position import GridPosition
    from .grid_based_agent import GridBasedAgent

class GridWorldReward(Reward, GridWorldObject):

    @classmethod
    def is_passable(self):
        return True
    
    def __init__(self, total_amount, yield_amount, world: 'GridWorld', pos: 'GridPosition'):
        Reward.__init__(self, total_amount, yield_amount)
        GridWorldObject.__init__(self, world, pos)

    def _give_reward(self, agent: 'GridBasedAgent'):
        _yield = min(self._base_yield, self._remaining_amount)
        agent.give_reward(_yield)
        self._remaining_amount -= _yield

    def trigger(self, agent: 'GridBasedAgent'):
        self._give_reward(agent)
        if self._remaining_amount < 1e-9:
            self._world.remove_object(self)
        