from .grid_world_agent import GridWorldAgent
from ...animation import WorldAnimation

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyArrow
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from scipy.sparse import coo_matrix, lil_matrix

from itertools import chain
from typing import Union, Type, Tuple, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from grammaticalevolutiontools.worlds.grid_world import \
        GridWorld, GridWorldObject


# -- Type Annotations --

type Color = Union[str, Tuple[float, float, float], Tuple[int, int, int]]
type Arrow = Tuple[float, float, float, float, Color, float]         # Tuple[x, y, dx, dy, color, width]
type Frame = Tuple[coo_matrix, list[Arrow]]

# -- Animation Class -- 

class GridWorldAnimation(WorldAnimation):
    def __init__(self, world_dims: Tuple[int, int], 
                 world_obj_trace: 'GridWorld.ObjTrace', 
                 world_agent_trace: 'GridWorld.AgentTrace', 
                 obj_colors: dict[Type['GridWorldObject'], Color], 
                 agent_colors: dict[Type[GridWorldAgent], Color],
                 bg_color: Color, 
                 arrow_color: Union[Color, dict[Type[GridWorldAgent], Color]] = None):

        if arrow_color is None or isinstance(arrow_color, dict):
             _arrow_colors_dict = arrow_color
        else:
             _arrow_colors_dict = defaultdict(lambda : arrow_color)

        self._CMAP, _class_to_color_index = self._create_custom_cmap(bg_color, agent_colors, obj_colors)
        self._frames: list[Frame] = self._create_frames(world_dims, world_obj_trace, world_agent_trace,
                                                        _class_to_color_index, _arrow_colors_dict)
        super().__init__()

    # - - Private Helpers - -

    def _create_custom_cmap(self, bg: Color, agent_colors: dict[Type['GridWorldAgent'], Color], 
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
                        arrow_colors_dict: dict[Type[GridWorldAgent], Color]) -> list[Frame]:
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
        """
        Returns an Arrow tuple (x, y, dx, dy, color, width) for matplotlib.
        Starts at the front-middle of the agent's cell in the grid.
        """
        arrow_len = 0.5   # how long the arrow is
        start_offset = 0.25  # move arrow slightly forward from center

        # agent_pos = (row, col)
        row, col = agent_pos

        # center of the cell
        x = col
        y = row

        # direction vector (dy, dx) in cell coordinates
        dir_vec = GridWorldAgent.direction_to_vec(agent_dir)  # assume returns (dy, dx)
        dy, dx = dir_vec

        # move starting point forward slightly in the direction the agent is facing
        x += dx * start_offset
        y += dy * start_offset

        # scale the direction to the arrow length
        dx *= arrow_len
        dy *= arrow_len

        # return as (x, y, dx, dy, color, width)
        return (x, y, dx, dy, arrow_colors_dict[agent_class], 0.2)
    

    # - - Public Methods - -

    def play(self, pause=200) -> FuncAnimation:
        """
        Plays the animation in a notebook-friendly way using blitting for speed.
        Returns the FuncAnimation object. Keep a reference to it!
        """
        self.close()        # close previous animation if open

        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect('equal')

        # Initial grid
        first_grid, first_arrows = self._frames[0]
        img = self.ax.imshow(first_grid.toarray(), cmap=self._CMAP, vmin=0, vmax=1)

        # Create arrow artists
        arrow_artists = []
        for x, y, dx, dy, color, width in first_arrows:
            arrow = FancyArrow(x, y, dx, dy, color=color, width=width)
            self.ax.add_patch(arrow)
            arrow_artists.append(arrow)

        # Keep a title artist for blitting
        title_artist = self.ax.set_title("Frame 0")

        def update(frame_idx):
            grid, arrows = self._frames[frame_idx]

            # Update grid
            img.set_data(grid.toarray())

            # Update arrows
            # Remove old arrows
            for arrow in arrow_artists:
                arrow.remove()
            arrow_artists.clear()

            # Add new arrows
            for x, y, dx, dy, color, width in arrows:
                arrow = FancyArrow(x, y, dx, dy, color=color, width=width)
                self.ax.add_patch(arrow)
                arrow_artists.append(arrow)

            # Update title
            title_artist.set_text(f"Frame {frame_idx}")

            # Return all artists that need to be redrawn
            return [img, title_artist, *arrow_artists]

        anim = FuncAnimation(
            self.fig,
            update,
            frames=len(self._frames),
            interval=pause,
            blit=True
        )

        return anim


    # - - Magic Methods - -

    def __len__(self):
        return len(self._frames)