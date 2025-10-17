from grammaticalevolutiontools.worlds.layouts import WorldLayout
from ...utilities_.BasicWorld import EmptyLayout

import pytest


class TestBaseAgent:
    """Test suite for BaseLayout functionality."""

    def test_base_world_layout_is_abstract(self):
        with pytest.raises(TypeError):
            WorldLayout()
    
    def test_initialized_assertions(self):
        layout1 = EmptyLayout(initialize=True)
        layout1._assert_initialized()

        with pytest.raises(WorldLayout.AlreadyInitializedError):
            layout1._assert_not_initialized()

        layout2 = EmptyLayout(initialize=False)
        layout2._assert_not_initialized()

        with pytest.raises(WorldLayout.MapNotInitializedError):
            layout2._assert_initialized()


    def test_locking(self):
        layout = EmptyLayout(lock=False)

        assert not layout._locked
        assert not layout.locked()
        layout._assert_not_locked()

        with pytest.raises(WorldLayout.LayoutNotLockedError):
            layout._assert_locked()

        layout.lock()

        assert layout._locked
        assert layout.locked()
        layout._assert_locked()

        with pytest.raises(WorldLayout.LayoutLockedError):
            layout._assert_not_locked()

