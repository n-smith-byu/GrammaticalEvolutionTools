from ..grid_based_agent import GridBasedAgent

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from scipy.sparse import coo_matrix, lil_matrix
import seaborn as sns
import numpy as np

from itertools import chain
from typing import Union, Type, Tuple, TYPE_CHECKING

from collections import defaultdict

if TYPE_CHECKING:
      from GrammaticalEvolutionTools.GridBasedTools import GridWorld, GridWorldObject, GridPosition


# -- Type Annotations --

Color = Union[str, Tuple[float, float, float], Tuple[int, int, int]]
Arrow = Tuple[float, float, float, float, Color, float]         # Tuple[x, y, dx, dy, color, width]
Frame = Tuple[coo_matrix, list[Arrow]]

# -- Animation Class -- 

class GridWorldAnimation:
    def __init__(self, world_dims: Tuple[int, int], 
                 world_obj_trace: 'GridWorld.ObjTrace', 
                 world_agent_trace: 'GridWorld.AgentTrace', 
                 obj_colors: dict[Type['GridWorldObject'], Color], 
                 agent_colors: dict[Type[GridBasedAgent], Color],
                 bg_color: Color, 
                 arrow_color: Union[Color, dict[Type[GridBasedAgent], Color]] = None):
        
        if arrow_color is None or isinstance(arrow_color, dict):
             _arrow_colors_dict = arrow_color
        else:
             _arrow_colors_dict = defaultdict(lambda : arrow_color)

        self._CMAP, _class_to_color_index = self._create_custom_cmap(bg_color, agent_colors, obj_colors)
        self._frames: list[Frame] = self._create_frames(world_dims, world_obj_trace, world_agent_trace,
                                                        _class_to_color_index, _arrow_colors_dict)
        
        self.fig = None
        self.ax = None


    # - - Private Helpers - -

    def _create_custom_cmap(self, bg: Color, agent_colors: dict[Type['GridBasedAgent'], Color], 
                            obj_colors: dict[Type['GridWorldObject'], Color]):
            all_colors = []
            class_to_color_index = {}

            all_colors.append((0, bg))
            N = len(agent_colors) + len(obj_colors)
            curr_ind = 0
            for cl, color in chain(agent_colors.items(), obj_colors.items()):
                curr_ind += 1
                color_ind = curr_ind / N
                all_colors.append((color_ind, to_rgb(color)))
                class_to_color_index[cl] = color_ind

            custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', all_colors)
            return custom_cmap, class_to_color_index
    
    def _create_frames(self, world_dims, obj_trace: 'GridWorld.ObjTrace', 
                             agent_trace: 'GridWorld.AgentTrace',
                             class_to_color_index,
                             arrow_colors_dict: dict[Type[GridBasedAgent], Color]) -> list[Frame]:
            frames = []
            for frame in zip(obj_trace, agent_trace):
                grid = lil_matrix(world_dims)
                objs_in_frame, agents_in_frame = frame

                for obj_cls, pos in objs_in_frame:
                    grid[*pos.coords] = class_to_color_index[obj_cls]

                arrows: list[Arrow] = []
                for agent_cls, pos, _dir in agents_in_frame:
                    grid[*pos.coords] = class_to_color_index[agent_cls]
                    if arrow_colors_dict is not None:
                        arrows.append(self._create_arrow(pos, _dir, agent_cls, arrow_colors_dict))

                frames.append((grid.tocoo(), arrows))
            
            return frames
    
    def _create_arrow(self, agent_pos, agent_dir, agent_class, arrow_colors_dict) -> Arrow:
        arrow_len = 0.5
        arrow_offset = 0.5
        # get arrow coordinates

        y, x = agent_pos
        dir_vec = GridBasedAgent.direction_to_vec(agent_dir)
        
        if agent_dir == GridBasedAgent.Direction.RIGHT:
            x += 2*arrow_offset
            y += arrow_offset
        elif agent_dir == GridBasedAgent.Direction.DOWN:
            x += arrow_offset
            y += 2*arrow_offset
        elif agent_dir == GridBasedAgent.Direction.LEFT:
            y += arrow_offset
        elif agent_dir == GridBasedAgent.Direction.UP:
            x += arrow_offset

        # draw arrow
        dy, dx = dir_vec*arrow_len

        return (x, y, dx, dy, arrow_colors_dict[agent_class], 0.2)


    # - - Public Methods - -

    def play(self, pause=200):
        if self.fig is not None:
            plt.close(self.fig)

        self.fig, self.ax = plt.subplots()

        def update(frame):
            self.ax.clear()

            grid, arrows = self._frames[frame]
            grid: coo_matrix
            arrows: list[Arrow]

            # drw grid
            sns.heatmap(grid.toarray(), ax=self.ax, annot=False, cmap=self._CMAP, vmin=0, vmax=1, fmt=".2f", linewidths=0,
                        cbar=False, xticklabels=False, yticklabels=False,
                        square=True)
            

            for x, y, dx, dy, color, width in arrows:
                self.ax.arrow(x, y, dx, dy, color=color, width=width)

            self.ax.set_title(str(frame))
        
        return FuncAnimation(self.fig, update, frames = len(self._frames), interval=pause)

    # - - Magic Methods - -

    def __len__(self):
        return len(self._frames)