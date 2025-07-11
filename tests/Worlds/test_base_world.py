import pytest

from grammaticalevolutiontools.worlds.layouts import WorldLayout
from grammaticalevolutiontools.worlds import World
from ..Tools import BasicWorld as bw
from ..Tools import BasicGrammar as bg

class TestBasicWorld:
    """Test suite for BaseWorld functionality."""

    def test_base_world_is_abstract(self):
        with pytest.raises(TypeError):
            World()


    def test_init_agent_type_assertions(self):

        # agent classes valid
        with pytest.raises(TypeError):
            bw.BasicWorldNoLayout(agent_classes=["invalid_type"], obj_types=[bw.BasicObject],
                                  layout=bw.EmptyLayout())
            
        with pytest.raises(TypeError):
            bw.BasicWorldNoLayout(agent_classes=[bg.BasicWorldAgent, "invalid_type"], obj_types=[bw.BasicObject],
                                  layout=bw.EmptyLayout())
            
        with pytest.raises(TypeError):
            bw.BasicWorldNoLayout(agent_classes=None, obj_types=[bw.BasicObject],
                                  layout=bw.EmptyLayout())
            

    def test_init_object_type_assertions(self):
        with pytest.raises(TypeError):
            bw.BasicWorldNoLayout(agent_classes=[bg.BasicWorldAgent], obj_types=["invalid_type"],
                                  layout=bw.EmptyLayout())
            
        with pytest.raises(TypeError):
            bw.BasicWorldNoLayout(agent_classes=[bg.BasicWorldAgent], obj_types=[bw.BasicObject, "invalid_type"],
                                  layout=bw.EmptyLayout())
            
        with pytest.raises(TypeError):
            bw.BasicWorldNoLayout(agent_classes=[bg.BasicWorldAgent], obj_types=None,
                                  layout=bw.EmptyLayout())
            

    def test_init_layout_assertions(self):
        with pytest.raises(TypeError):
            bw.BasicWorldNoLayout(agent_classes=[bg.BasicWorldAgent], obj_types=[bw.BasicObject],
                                  layout="invalid_type")
            
        with pytest.raises(TypeError):
            bw.BasicWorldNoLayout(agent_classes=[bg.BasicWorldAgent], obj_types=[bw.BasicObject],
                                  layout=None)
            
        
        with pytest.raises(WorldLayout.LayoutNotLockedError):
            bw.BasicWorldNoLayout(agent_classes=[bg.BasicWorldAgent], obj_types=[bw.BasicObject],
                                  layout=bw.EmptyLayout(lock=False))

    def test_base_world_inits_correctly(self):

        world = bw.BasicWorldNoLayout(agent_classes=[], obj_types=[],
                                      layout=bw.EmptyLayout(lock=True))
        
        
        agent_classes = [bg.BasicWorldAgent, bg.BasicWorldAgent]
        object_classes = [bw.BasicObject, bw.RewardObject]
        layout = bw.EmptyLayout(lock=True)
        world = bw.BasicWorldNoLayout(agent_classes=agent_classes, obj_types=object_classes,
                                      layout=layout)
        
        for cls in agent_classes:
            assert cls in world._valid_agent_classes

        for cls in object_classes:
            assert cls in world._valid_object_classes

        assert world._layout is layout

        
        
        
