from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import numpy as np

from MultiAgent import World
from MultiAgent import Agent

def run_agent(agent, world, T):
    world.reset(agent)
    food_positions = world.get_map_food_positions()

    # generate frames of animation
    frames = []
    for i in range(T):
        world.agent.execute_program()
        pos_trace, dir_trace, food_trace = agent.pop_traces()

        for i in range(len(pos_trace)):
            grid = np.zeros((world.height, world.width))
            if food_trace[i] is not None:
                food_positions.remove(food_trace[i])

            for food_pos in food_positions:
                grid[*food_pos] = 1

            grid[*pos_trace[i]] = 2
            agent_dir = dir_trace[i]

            frames.append((grid, agent_dir))
    
    return frames


def animate(animation_frames, pause=200):
    cell_size=0.4
    # fig_width = cell_size * world.width  # Number of columns
    # fig_height = cell_size * world.height  # Number of rows

    fig, ax = plt.subplots()
    def update(frame):
        ax.clear()
        grid, agent_dir = animation_frames[frame]
        agent_coords = np.unravel_index(np.argmax(grid), grid.shape)

        # drw grid
        sns.heatmap(grid, ax=ax, annot=False, cmap=World.CMAP, fmt=".2f", linewidths=0,
                    cbar=False, xticklabels=False, yticklabels=False,
                    square=True)
        
        # get arrow coordinates
        x = agent_coords[1]
        y = agent_coords[0]
        offset = 0.5
        if agent_dir == 0:                  # right
            x += 2*offset
            y += offset
        elif agent_dir == 1:                # down
            x += offset
            y += 2*offset
        elif agent_dir == 2:                # left
            y += offset
        else:                               # up
            x += offset

        # draw arrow
        dy, dx = Agent.DIRECTIONS[agent_dir]*cell_size
        plt.arrow(x, y, dx, dy, color='blue', width=0.05)
        
        plt.title(str(frame))

    return FuncAnimation(fig, update, frames = len(animation_frames), interval=pause)
