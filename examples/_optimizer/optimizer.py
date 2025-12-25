
from grammaticalevolutiontools.evolution import cross_over_programs, mutate_terminals, replace_random_branch
import numpy as np
import random

from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from grammaticalevolutiontools.worlds.base import World
    from grammaticalevolutiontools.agents import Agent

class Optimizer:
    def __init__(self, N, T, k, r, m, p_mutate_old, p_mutate_new, 
                 p_prune, score_func, world_class:Type[World], 
                 agent_classes:list[Type[World]]):

        self.score_func = score_func

        self.N = N          # population_size
        self.T = T          # num_time_steps to run
        self.k = k          # keep top k agents
        self.r = r          # num new randomly generated agents per generation
        self.m = m          # max number of mutations per agent
        self.p_mutate_old = p_mutate_old
        self.p_mutate_new = p_mutate_new
        self.p_prune = p_prune

        self.world = World()
        self.population:list[Agent] = []
        self.new_generation = []
        self.scores_over_time = []
        self.food_over_time = []

    def create_new_population(self):
        self.population = []
        self.add_random_agents()
    
    def test_generation(self):
        for agent in self.population:
            self.world.reset(agent)

            for t in range(self.T):
                agent.tick()

            try:
                assert agent.num_actions > 0
            except AssertionError as ex:
                print('Error')

    def prune(self):
        self.population = sorted(self.population, key=self.score_func, reverse=True)
        self.scores_over_time.append(self.score_func(self.population[0]))
        self.food_over_time.append(self.population[0].food)
        self.population = self.population[:self.k]          # keep only top k scores

    def mutate_agents(self):
        for agent in self.population:
            if agent in self.new_generation:
                if np.random.uniform(0,1) < self.p_mutate_new:
                    if np.random.uniform(0,1) < self.p_prune:
                        replace_random_branch(agent, )
                        
                    mutate_terminals(agent, num_mutations=np.random.choice(self.m))
                        
            else:
                if np.random.uniform(0,1) < self.p_mutate_old:
                    mutate_terminals(agent, num_mutations=np.random.choice(self.m))

    def create_next_generation(self):
        self.add_random_agents(n=self.r)

        self.new_generation = []
        while len(self.population) + len(self.new_generation) < self.N:
            agent1 = random.choice(self.population)
            agent2 = random.choice(self.population)

            new_children = cross_over_programs(agent1, agent2)
            self.new_generation += new_children

        self.population += self.new_generation

        self.mutate_agents()

    def add_random_agents(self, n=np.inf):         # adds up to n new agents to the population
        i = 0
        while i < n and len(self.population) < self.N:
            self.population.append(Agent(world=self.world))
            i += 1

    def run(self, num_generations):
        self.scores_over_time = []
        self.food_over_time = []

        self.create_new_population()
        self.test_generation()
        for i in tqdm(range(1, num_generations + 1)):
            self.prune()
            self.create_next_generation()
            self.test_generation()

        return self.scores_over_time, self.food_over_time
    
    @property
    def best_agent(self):
        sorted_agents = sorted(self.population, key=self.score_func, reverse=True)
        return sorted_agents[0]

    