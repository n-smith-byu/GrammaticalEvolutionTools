from .grid_world_object import GridWorldObject
from ...worlds.objects import Reward

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .grid_world import GridWorld
    from .grid_world_agent import GridWorldAgent

class GridWorldReward(Reward, GridWorldObject):

    @classmethod
    def is_passable(self):
        return True
    
    def __init__(self, total_amount, yield_amount, world: 'GridWorld'):
        Reward.__init__(self, total_amount, yield_amount)
        GridWorldObject.__init__(self, world)

    def trigger(self, agent: 'GridWorldAgent'):
        self._give_reward(agent)
        if self._remaining_amount < 1e-9:
            self._world.remove_object(self)
        