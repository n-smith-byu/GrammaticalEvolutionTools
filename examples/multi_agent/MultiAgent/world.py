from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import numpy as np
from scipy.sparse import csr_matrix

from MultiAgent import Agent


class World:
    SPACE = 0
    FOOD = 1
    AGENT = 2
    CMAP = LinearSegmentedColormap.from_list("my_cmap", ["black", "lime", "blue", "red"])

    def __init__(self, grid_layout_file_path = "Resources/GRID.txt",
                 agent=None):
        
        (self.width, self.height, 
         self.__basic_food_positions, 
         self.__complex_food_positions) = self.__load_grid(grid_layout_file_path)
        if agent is None:
            agent = Agent(world=self)

        self.reset(agent)

    def reset(self, agent=None):
        if agent is not None:
            self.agent = agent
            agent.world = self

        self.food_locations = set([pos for pos in self.__basic_food_positions])   # reset food in world
        self.multi_agent_food_locations = set([pos for pos in self.__complex_food_positions])
        self.agent.reset()
             
    def __load_grid(self, file_path):
        basic_food_locations = set()
        complex_food_locations = set()
        with open(file_path, "r") as file:
            i = 0
            for raw_line in file:
                line = raw_line.strip()
                for j in range(len(line)):
                    if line[j] == '1':
                        basic_food_locations.add((i,j))
                    elif line[j] == '2':
                        complex_food_locations.add((i,j))
                i += 1
            
            grid_height = j
            grid_width = i
            
        return grid_width, grid_width, basic_food_locations, complex_food_locations
    
    def is_valid_space(self, pos:np.array):
        if np.any(pos < 0):
            return False
        
        if pos[0] >= self.height or pos[1] >= self.width:
            return False
        
        return True

    def remove_food(self, pos:tuple[int]):
        self.food_locations.remove(pos)
    
    def get_map_food_positions(self):
        return set([pos for pos in self.__basic_food_positions])
    
    @property
    def num_agents(self):
        return len(self.agents)
    
