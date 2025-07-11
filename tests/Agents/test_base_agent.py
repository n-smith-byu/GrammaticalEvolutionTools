from grammaticalevolutiontools.programs import ProgramTree
from grammaticalevolutiontools.agents import Agent

from ..Tools import BasicGrammar as bg
from ..Tools import BasicWorld as bw

import pytest


class TestBaseAgent:
    """Test suite for BaseAgent functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up a fresh agent and program for each test."""

        # Create a basic program that prints "test" twice, 
        # no spaces or newlines in between
        self.root = bg.CodeNode()
        mid = bg.MidNode()
        for _ in range(2):
            mid.add_child(bg.ChildNode())

        self.root.add_child(mid)
        self.program = ProgramTree(self.root)

        self.world = bw.BasicWorld()

    def get_worldless_agent(self) -> bg.BasicWorldlessAgent:
        return bg.BasicWorldlessAgent(self.program.copy())
    
    def get_world_agent(self) -> bg.BasicWorldAgent:
        return bg.BasicWorldAgent(self.program.copy())

    # -- Tests -- 

    def test_base_agent_class_is_abstract(self):
        with pytest.raises(TypeError):
            Agent()

    def test_new_agent_not_assigned_world(self):
        agent: Agent = bg.BasicWorldAgent()

        assert not agent.assigned_to_world()
        assert agent._world is None

    def test_init_with_program(self):

        program = self.program.copy()
        agent = bg.BasicWorldlessAgent(program)

        assert agent._program is program
        assert program.agent is agent

        with pytest.raises(TypeError):
            bg.BasicWorldAgent(program = 'hello')

    def test_requires_world(self):
        agent1 = self.get_worldless_agent()
        agent2 = self.get_world_agent()

        assert not agent1.requires_world
        assert agent2.requires_world

    def test_adding_to_world(self):
        agent = self.get_world_agent()
        assert agent._world is None
        assert not agent.assigned_to_world()

        with pytest.raises(TypeError):
            agent._set_world("Not a World")

        agent._set_world(self.world)
        assert agent.assigned_to_world()
        assert agent._world is self.world
        
        with pytest.raises(Agent.AgentAlreadyInWorldError):
            agent._set_world(bw.BasicWorld())

    def test_tick_no_loop(self, capsys: pytest.CaptureFixture):

        agent = self.get_worldless_agent()

        # should print out "testtest"
        for _ in range(2):
            agent.tick(loop=False)
            assert agent._program.status == ProgramTree.Status.RUNNING

        # should end the program
        agent.tick(loop=False)
        assert agent._program.status == ProgramTree.Status.EXITED

        captured = capsys.readouterr()  # Capture stdout
        assert captured.out.strip() == bg.ChildNode.PRINT_STR*2

        # should run the program 1 and a half times, 
        # printing out "test" three times
        for _ in range(4):
            agent.tick(loop=False)

        captured = capsys.readouterr()  # Capture stdout
        assert captured.out.strip() == bg.ChildNode.PRINT_STR*3

        self.program.kill()

    def test_tick_with_loop(self, capsys: pytest.CaptureFixture):
        N = 3
        agent = self.get_worldless_agent()
        # shouldn't exit on the third tick, but rather should restart. 
        for _ in range(N):
            agent.tick()
            assert agent._program.status == ProgramTree.Status.RUNNING

        # should print out "test" once for each iter of the loop
        captured = capsys.readouterr()  
        assert captured.out.strip() == bg.ChildNode.PRINT_STR * N

        self.program.kill()


    def test_execute_program(self, capsys: pytest.CaptureFixture):
        agent = self.get_worldless_agent()
        # run the entire program
        agent.execute_program()

        # ensure program has exited and all terminal nodes were run.
        assert agent._program.status == ProgramTree.Status.EXITED

        captured = capsys.readouterr()
        assert captured.out.strip() == bg.ChildNode.PRINT_STR * 2

        # tick once to begin with
        agent.tick(loop=False)

        # should kill program then run the entire program
        agent.execute_program()

        captured = capsys.readouterr()
        assert captured.out.strip() == bg.ChildNode.PRINT_STR * 3

    def test_tick_requires_world(self):
        agent = self.get_world_agent()
        
        with pytest.raises(Agent.WorldNotSetError):
            agent.tick()

        agent._set_world(self.world)
        agent.tick()

    def test_record_actions(self):
        agent = self.get_worldless_agent()
        assert agent.num_actions == 0

        agent._record_action()

        assert agent.num_actions == 1

    def test_giving_rewards(self):
        agent = self.get_worldless_agent()
        assert agent.score == 0

        agent.give_reward(10)
        assert agent.score == 10

    def test_resetting(self):
        agent = self.get_world_agent()
        agent._set_world(self.world)
        agent._record_action()
        agent.give_reward(10)
        agent.tick(loop=False)

        agent._reset()

        assert agent._world is None
        assert agent.num_actions == 0
        assert agent.score == 0
        assert agent._program.status == ProgramTree.Status.EXITED

    def test_copying_program(self):
        agent = self.get_worldless_agent()
        program_cpy = agent.copy_program()

        assert program_cpy is not agent._program
        assert program_cpy is not None

        bg.BasicWorldlessAgent(program_cpy)
