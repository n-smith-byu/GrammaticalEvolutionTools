from grammaticalevolutiontools.worlds.objects import WorldObject
from grammaticalevolutiontools.worlds.rewards import Reward
from grammaticalevolutiontools.agents import Agent

class BasicObject(WorldObject):
    def __init__(self, world):
        super(BasicObject, self).__init__(world)

    def trigger(self, agent: Agent):
        print(agent._uuid)

class RewardNotObject(Reward):
    def __init__(self):
        super().__init__(total_amount=10, base_yield=1)

class RewardObject(Reward, WorldObject):
    def __init__(self, world, total_amount=10, base_yield=1):
        Reward.__init__(self, total_amount, base_yield)
        WorldObject.__init__(self, world)

    def _give_reward(self, agent: Agent):
        _yield = min(self._base_yield, self._remaining_amount)
        agent.give_reward(_yield)
        self._remaining_amount -= _yield

    def trigger(self, agent: Agent):
        self._give_reward(agent)
        if self._remaining_amount < 1e-9:
            print(f"yielded")
