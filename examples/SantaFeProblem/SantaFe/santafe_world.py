from grammaticalevolutiontools.worlds.grid_world import \
    GridWorld, GridLayout, GridPosition
from .santafe_agent import SantaFeAgent
from .santafe_food import SantaFeFood

import importlib.resources
from pathlib import Path


# Defining a layout consisting of the Santa Fe Trail
class SantaFeLayout(GridLayout):

    def __init__(self):
        super(SantaFeLayout, self).__init__()
        
        # Loads the object layout from a file
        # See /Resources/Grid

        resource_path: Path = importlib.resources.files(__package__).joinpath('resources', 'GRID.txt')
        self.load_map_layout_from_file(file_path=resource_path.resolve(),
                                       obj_symbols=['#'], obj_classes=[SantaFeFood],
                                       empty_space_symbol='.')

class SantaFeWorld(GridWorld[SantaFeAgent, SantaFeLayout]):

    _layout = SantaFeLayout()

    def __init__(self, agent: 'SantaFeAgent'=None):
        
        super(SantaFeWorld, self).__init__(SantaFeWorld._layout)

        self._agent_start_pos = GridPosition((0,0))

        if agent is not None:
            self.reset_with_agent(agent)

    def reset_with_agent(self, agent: SantaFeAgent, start: GridPosition=GridPosition((0,0)), recording_on=False):
        return super().load_new_agents(
            {agent: (start, agent.Direction.RIGHT)},
            recording_on=recording_on
        )

    def get_agent(self):
        agents = list(super().get_all_agents())
        if len(agents) == 0:
            return None
        else:
            return agents[0]


