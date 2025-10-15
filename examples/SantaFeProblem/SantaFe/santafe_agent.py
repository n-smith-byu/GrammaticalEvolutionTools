from grammaticalevolutiontools.grid_based_tools import \
    GridBasedAgent, GridPosition

from .santafe_food import SantaFeFood

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .santafe_world import SantaFeWorld


class SantaFeAgent(GridBasedAgent):

    @classmethod
    def default_grammar(cls):
        if not cls._default_program_cls:
            from .Grammar import SantaFeGrammar
            cls._default_grammar = SantaFeGrammar

        return cls._default_grammar

    def __init__(self, program_tree=None):
        super(SantaFeAgent, self).__init__(program_tree)
        self._world: 'SantaFeWorld'

    def _set_world(self, world: 'SantaFeWorld'):
        return super()._set_world(world)

    def _set_position(self, pos: GridPosition):
        return super()._set_position(pos)
    
    def give_reward(self, amount):
        #print(f"<Reward: {self.position}, {amount}>")
        return super().give_reward(amount)

    def food_within(self, distance):
        for k in range(1, distance + 1):
            curr_dir = SantaFeAgent.direction_to_vec(self._curr_dir)
            space = self._pos + k * curr_dir

            obj = self._world.get_objects_at_position(space)
            if isinstance(obj, SantaFeFood):
                return True
            
        return False
    
    def wall_within(self, distance):
        for k in range(1, distance + 1):
            curr_dir = SantaFeAgent.direction_to_vec(self._curr_dir)
            space = self._pos + k * curr_dir

            if not self._world.space_within_map_bounds(space):
                return True
            if not self._world.position_passable(space):
                return True
            
        return False



