from GrammaticalEvolutionTools.AbstractProgramTree import Program
from .grammar import CodeNode
import numpy as np

class Agent:

    DIRECTIONS = [np.array([0,1]), 
                  np.array([1,0]), 
                  np.array([0,-1]), 
                  np.array([-1,0])]

    def __init__(self, world, program_tree=None):
        self.world = world
        self.food = 0
        self.pos = np.array([0,0])
        self.curr_dir = 0
        self.num_actions = 0

        # track position and direction for animation
        self.__pos_trace = []
        self.__dir_trace = []
        self.__food_trace = []

        if program_tree is None:
            self.program_tree = Program(root=CodeNode())
        else:
            self.program_tree = program_tree

    def reset(self):
        self.food = 0
        self.pos = np.array([0,0])
        self.num_actions = 0
        self.curr_dir = 0

        self.pop_traces()

    def execute_program(self):
        self.program_tree.run(agent=self)

    def move(self):
        new_pos = self.pos + Agent.DIRECTIONS[self.curr_dir]
        if self.world.is_valid_space(new_pos):
            self.pos = new_pos

        self.num_actions += 1
        self.record_state()

        if tuple(self.pos) in self.world.food_locations:
            self.__food_trace.append(tuple(self.pos))
            self.world.remove_food(tuple(self.pos))
            self.food += 1
        else:
            self.__food_trace.append(None)

    def turn_left(self):
        self.curr_dir = (self.curr_dir - 1) % 4
        self.__food_trace.append(None)
        self.num_actions += 1
        self.record_state()

    def turn_right(self):
        self.curr_dir = (self.curr_dir + 1) % 4
        self.__food_trace.append(None)
        self.num_actions += 1
        self.record_state()

    def food_within(self, distance):
        for k in range(1, distance + 1):
            space = self.pos + k * Agent.DIRECTIONS[self.curr_dir]

            if tuple(space) in self.world.food_locations:
                return True
            
        return False
    
    def wall_within(self, distance):
        for k in range(1, distance + 1):
            space = self.pos + k * Agent.DIRECTIONS[self.curr_dir]

            if space[0] < 0 or space[0] >= self.world.height:
                return True
            if space[1] < 0 or space[1] >= self.world.width:
                return True
            
        return False

    
    def record_state(self):
        self.__pos_trace.append(tuple(self.pos))
        self.__dir_trace.append(self.curr_dir)

    def pop_traces(self):
        traces = self.__pos_trace, self.__dir_trace, self.__food_trace
        self.__dir_trace = []
        self.__pos_trace = []
        self.__food_trace = []

        return traces



