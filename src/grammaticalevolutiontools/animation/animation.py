from matplotlib.animation import FuncAnimation
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from abc import ABC, abstractmethod


class WorldAnimation(ABC):
    def __init__(self):
        self.fig: Figure = None
        self.ax: Axes = None

    def close(self):
        if self.fig is not None:
            self.ax.clear()
            plt.close(self.fig)

            self.fig = None
            self.ax = None

    @abstractmethod
    def _create_frames(self):
        pass

    @abstractmethod
    def play(self) -> FuncAnimation:
        pass