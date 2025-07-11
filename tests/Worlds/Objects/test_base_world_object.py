from grammaticalevolutiontools.worlds.objects import WorldObject
from ...Tools import BasicWorld as bw

import pytest


class TestBaseWorldObject:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.world = bw.BasicWorld()

    def test_base_world_object_is_abstract(self):
        with pytest.raises(TypeError):
            WorldObject(self.world)

    def test_base_world_object_init(self):
        with pytest.raises(TypeError):
            bw.BasicObject("none")

        obj = bw.BasicObject(self.world)
        assert obj._world is self.world


    