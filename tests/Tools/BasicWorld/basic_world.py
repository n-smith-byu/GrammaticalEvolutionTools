from grammaticalevolutiontools.worlds.layouts import WorldLayout
from grammaticalevolutiontools.worlds import World

from ..BasicGrammar import BasicWorldAgent

class EmptyLayout(WorldLayout):
    def __init__(self, lock=False, initialize=True):
        super(EmptyLayout, self).__init__()

        self._initialized = initialize

        if lock:
            self.lock()

    def initialized(self):
        return self._initialized
    
    def copy(self, lock=True):
        _dup = EmptyLayout()
        if lock:
            _dup.lock()

        return _dup

class BasicWorld(World):

    _LAYOUT = EmptyLayout(lock=True)

    def __init__(self):
        super(BasicWorld, self).__init__(agent_classes=[BasicWorldAgent], obj_types=[], 
                                         world_layout=BasicWorld._LAYOUT)
        
    def tick(self):
        for agent in self._agents:
            agent.tick()
    
    def load_new_agents(self):
        pass

class BasicWorldNoLayout(World):

    def __init__(self, agent_classes, obj_types, layout):
        super(BasicWorldNoLayout, self).__init__(agent_classes=agent_classes, obj_types=obj_types, 
                                         world_layout=layout)
        
    def tick(self):
        for agent in self._agents:
            agent.tick()
    
    def load_new_agents(self):
        pass