from grammaticalevolutiontools.worlds.grid_world import \
    GridWorldReward, GridPosition
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .santafe_world import SantaFeWorld

class SantaFeFood(GridWorldReward):
    def __init__(self, world: 'SantaFeWorld'):
        super(SantaFeFood, self).__init__(total_amount=1, yield_amount=1,
                                          world=world)
        
    
        