from grammaticalevolutiontools.worlds.rewards import Reward
from ...utilities_ import BasicWorld as bw

import pytest


class TestBaseReward:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.world = bw.BasicWorld()

    def test_base_reward_is_abstract(self):
        with pytest.raises(TypeError):
            Reward(total_amount=10, base_yield=1)

    def test_child_must_inherit_from_world_obj(self):
        with pytest.raises(TypeError):
            bw.RewardNotObject()

        bw.RewardObject(self.world)

    def test_reward_init(self):
        with pytest.raises(ValueError):
            bw.RewardObject(self.world, total_amount = -10)

        with pytest.raises(ValueError):
            bw.RewardObject(self.world, base_yield=-1)

        reward = bw.RewardObject(self.world, total_amount=10, base_yield=1)
        assert reward._remaining_amount == 10
        assert reward.remaining == 10
        assert reward._base_yield == 1

