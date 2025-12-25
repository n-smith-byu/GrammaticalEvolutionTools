from grammaticalevolutiontools.meta import BaseNode

import numpy as np
import pytest

import warnings


class MockNode2Children(BaseNode):

    def __init__(self):
        super().__init__()
        self._possible_children = {
            0: [MockNodeNoChildren],
            1: [MockNode1Child, MockNodeNoChildren]
        }

        self._list = []

    def _on_collect_descendants_attach(self):
        self._list.append(1)
        return super()._on_collect_descendants_attach()
    
    def _rollback_attach(self):
        return self._on_collect_descendants_detach()
    
    def _on_collect_descendants_detach(self):
        self._list.remove(1)
        return super()._on_collect_descendants_detach()
    
    def _rollback_detach(self):
        return self._on_collect_descendants_attach()

    @property
    def _possible_children_dict(self):
        return self._possible_children
    @property
    def _special_probs_dict(self):
        return {1: [3, 10]}
    @property
    def _all_possible_children(self):
        return {MockNodeNoChildren, MockNode1Child}
    @property
    def max_num_children(self):
        return 2
    @property
    def label(self):
        return "root"
    @property
    def token(self):
        return "R"
    @property
    def is_terminal(self):
        return False
    @property
    def is_root(self):
        return True
    
class MockNode1Child(BaseNode):
    def __init__(self):
        super().__init__()

        self._list = []

    def _on_collect_descendants_attach(self):
        self._list.append(1)
        return super()._on_collect_descendants_attach()
    
    def _rollback_attach(self):
        return self._on_collect_descendants_detach()
    
    def _on_collect_descendants_detach(self):
        self._list.remove(1)
        return super()._on_collect_descendants_detach()
    
    def _rollback_detach(self):
        return self._on_collect_descendants_attach()

    @property
    def _possible_children_dict(self):
        return {0: [MockNodeNoChildren, MockNode1Child, MockNode2Children]}
    @property
    def _special_probs_dict(self):
        return {}
    @property
    def _all_possible_children(self):
        return {MockNodeNoChildren, MockNode1Child}
    @property
    def max_num_children(self):
        return 1
    @property
    def label(self):
        return "child1"
    @property
    def token(self):
        return "C1"
    @property
    def is_terminal(self):
        return False
    @property
    def is_root(self):
        return False

class MockNodeNoChildren(BaseNode):
    def __init__(self):
        super().__init__()

        self._list = []

    def _on_collect_descendants_attach(self):
        self._list.append(1)
        return super()._on_collect_descendants_attach()
    
    def _rollback_attach(self):
        return self._on_collect_descendants_detach()
    
    def _on_collect_descendants_detach(self):
        self._list.remove(1)
        return super()._on_collect_descendants_detach()
    
    def _rollback_detach(self):
        return self._on_collect_descendants_attach()

    @property
    def _possible_children_dict(self):
        return {}
    @property
    def _special_probs_dict(self):
        return {}
    @property
    def _all_possible_children(self):
        return set()
    @property
    def max_num_children(self):
        return 0
    @property
    def label(self):
        return "child"
    @property
    def token(self):
        return "Moc"
    @property
    def is_terminal(self):
        return True
    @property
    def is_root(self):
        return False
    



# - - - - - - - - - - - -
# - - - - Tests - - - - - 
# - - - - - - - - - - - -


# ---- Static Assertion Method Tests ----


# Basic Assertions
class TestBasicStaticAssertions:
    @staticmethod
    def test_assert_token_valid():
        BaseNode._assert_token_valid("abc")
        with pytest.raises(ValueError):
            BaseNode._assert_token_valid("")
        with pytest.raises(TypeError):
            BaseNode._assert_token_valid(123)

    @staticmethod
    def test_assert_max_num_children_valid():
        BaseNode._assert_max_num_children_valid(3)
        BaseNode._assert_max_num_children_valid(0)
        BaseNode._assert_max_num_children_valid(0, is_terminal=True)
        with pytest.raises(ValueError):
            BaseNode._assert_max_num_children_valid(3, is_terminal=True)
        with pytest.raises(ValueError):
            BaseNode._assert_max_num_children_valid(-1)
        with pytest.raises(TypeError):
            BaseNode._assert_max_num_children_valid("3")

    @staticmethod
    def test_assert_label_valid():
        BaseNode._assert_label_valid("label")
        BaseNode._assert_label_valid("")
        BaseNode._assert_label_valid(None)
        with pytest.raises(TypeError):
            BaseNode._assert_label_valid(5)

    @staticmethod
    def test_assert_tags_valid():
        BaseNode._assert_tags_valid(is_terminal=False, is_root=True)
        with pytest.raises(TypeError):
            BaseNode._assert_tags_valid("yes", True)
        with pytest.raises(TypeError):
            BaseNode._assert_tags_valid(True, "yes")
        with pytest.raises(ValueError):
            BaseNode._assert_tags_valid(is_terminal=True, is_root=True)


# Complex Assertions
class TestPossibleChildrenDictAssertions:

    """test assert_possible_children_dict_valid"""
    
    def test_assert_possible_children_dict_valid_success(self):
        valid_dict = {
            0: [int],
            1: [str]
        }
        # Should not raise
        BaseNode._assert_possible_children_dict_valid(valid_dict, 2)

    def test_assert_possible_children_dict_valid_type_error(self):
        with pytest.raises(TypeError):
            BaseNode._assert_possible_children_dict_valid(["not", "a", "dict"], 2)

    def test_assert_possible_children_dict_valid_missing_key(self):
        with pytest.raises(KeyError):
            BaseNode._assert_possible_children_dict_valid({0: [int]}, 2)  # missing key 1

    def test_assert_possible_children_dict_valid_non_list_value(self):
        with pytest.raises(TypeError):
            BaseNode._assert_possible_children_dict_valid({0: int, 1: [str]}, 2)

    def test_assert_possible_children_dict_valid_unused_key_warns(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            BaseNode._assert_possible_children_dict_valid({0: [int], 1: [str], 3: [float]}, 2)
            assert any("Unused inds" in str(warning.message) for warning in w)


class TestSpecialChildProbsDictAssertions:

    """test assert_child_probs_dict_valid"""

    def test_assert_child_probs_dict_valid_success(self):
        children_dict = {
            0: [int, str],
            1: [float]
        }
        probs_dict = {
            0: np.array([0.5, 0.5]),
            1: [1.0]
        }
        # Should not raise
        BaseNode._assert_child_probs_dict_valid(probs_dict, children_dict)

    def test_assert_child_probs_dict_valid_non_dict_type(self):
        with pytest.raises(TypeError):
            BaseNode._assert_child_probs_dict_valid("not a dict", {0: [int]})

    def test_assert_child_probs_dict_valid_bad_probs_raises(self):
        children_dict = {0: [int, str]}
        bad_probs = {0: [0.1, 0.2, 0.7]}  # too many probs

        with pytest.raises(ValueError, match="Error at index 0"):
            BaseNode._assert_child_probs_dict_valid(bad_probs, children_dict)

    def test_assert_child_probs_dict_valid_with_unused_key_warns(self):
        children_dict = {
            0: [int],
        }
        probs_dict = {
            0: [1.0],
            1: [1.0]  # Unused
        }

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            BaseNode._assert_child_probs_dict_valid(probs_dict, children_dict)
            assert any("Unused inds" in str(warning.message) for warning in w)


class TestChildProbsValsAssertions:

    """test assert_child_probs_valid"""

    def test_assert_child_probs_valid_success(self):
        BaseNode._assert_child_probs_valid(np.array([0.5, 0.5]), [int, str])

    def test_assert_child_probs_valid_non_1d_array(self):
        with pytest.raises(ValueError, 
                           match="`child_probs` must be an 1d array. Found an array with 2 dimensions."):
            BaseNode._assert_child_probs_valid(
                child_probs=[[0.5, 0.5], 
                             [0.4, 0.7]], 
                possible_children=[int, str])

    def test_assert_child_probs_valid_length_mismatch(self):
        with pytest.raises(ValueError, 
                           match="Size mismatch"):
            BaseNode._assert_child_probs_valid([0.3, 0.3, 0.4], [int, str])

    def test_assert_child_probs_valid_nonconvertible_type(self):
        with pytest.raises(ValueError, 
                           match="Could not convert to a 1-D numpy array"):
            BaseNode._assert_child_probs_valid("not a valid array", [int, str])



# ---- Probabilities and Static Utils Tests ----

class TestStaticUtils:
    @staticmethod
    def test_probs_to_numpy():
        arr = BaseNode.probs_to_numpy([0.2, 0.8])
        assert isinstance(arr, np.ndarray)
        assert arr.shape == (2,)
        assert arr.dtype == np.float64

    @staticmethod
    def test_convert_probs_dict_to_numpy():
        probs_dict = {
            0: [0.3, 0.7],
            1: [0.5, 0.5]
        }
        converted = BaseNode.convert_probs_dict_to_numpy(probs_dict)
        assert all(isinstance(v, np.ndarray) for v in converted.values())
        assert all((key in converted) for key in probs_dict)
        assert all(np.all(probs_dict[key] == converted[key]) for key in probs_dict)

    @staticmethod
    def test_get_possible_children_and_probs():
        node = MockNode2Children()
        children, probs = node.get_possible_children_and_probs(0)
        assert isinstance(children, list)
        assert isinstance(probs, np.ndarray)
        assert np.isclose(probs.sum(), 1.0)



# ---- Test Basic Methods ----

class TestBaseNodeBasicBehavior:

    # - - Test init and property methods - -

    @staticmethod
    def test_init_function():
        node1 = MockNode2Children()
        
        assert node1.children == [None, None]
        assert node1._num_children == 0
        assert node1._depth == 0
        assert node1._attr_cache == {}
        assert node1._parent is None

        node2 = MockNode2Children()
        assert node2._identifier != node1._identifier

    @staticmethod
    def test_basic_property_methods():
        node = MockNode2Children()
        node._children[0] == MockNode2Children()
        node._children[1] == MockNodeNoChildren()

        assert node.num_children == node._num_children
        assert node.child_depth == node._depth + 1
        assert node.children is not node._children
        assert node.children == node._children

    @staticmethod
    def test_possible_children_dict_property_method():
        node = MockNode2Children()
        pc = node.possible_children_dict

        assert pc is not node._possible_children_dict
        assert isinstance(pc, dict)

        # test 
        for ind, chld_list in node._possible_children_dict.items():
            assert ind in pc
            assert isinstance(pc[ind], list)
            assert pc[ind] is not chld_list
            assert pc[ind] == chld_list

    @staticmethod
    def test_child_probs_dict_property_method():
        node = MockNode2Children()
        sp = node.special_probs_dict

        assert sp is not node._special_probs_dict
        assert isinstance(sp, dict)

        # test 
        for ind, probs_list in node._special_probs_dict.items():
            assert ind in sp
            assert isinstance(sp[ind], list)
            assert sp[ind] is not probs_list
            assert sp[ind] == probs_list

    @staticmethod
    def test_get_next_available_slot():
        node = MockNode2Children()

        # tet with one possible node type
        node._possible_children = {
            0: [int],
            1: [int]
            }

        node._children = [None, None]
        assert node.get_next_available_slot(int) == 0

        node._children = [None, 1]
        assert node.get_next_available_slot(int) == 0

        node._children = [1, None]
        assert node.get_next_available_slot(int) == 1

        node._children = [1, 2]
        assert node.get_next_available_slot(int) is None


        # test with mixed node types 
        node._possible_children = {
            0: [MockNodeNoChildren],
            1: [MockNodeNoChildren, int]}
        
        node._children = [MockNodeNoChildren(), None]
        assert node.get_next_available_slot(int) == 1

        node._children = [None, MockNodeNoChildren()]
        assert node.get_next_available_slot(int) is None

    @staticmethod
    def test_get_child_at_index():
        node = MockNode2Children()
        node._possible_children = {
            0: [int],
            1: [int]
            }
        
        node._children = [1, 2]
        assert node.get_index_of_child(1) == 0
        assert node.get_index_of_child(2) == 1

    @staticmethod
    def test_get_parent():
        parent = MockNode2Children()
        child = MockNode1Child()

        parent._children = [None, child]
        child._parent = parent

        assert child.get_parent() == (parent, 1)


# ---- Child Management (Removing, Adding, etc.)

class TestBaseNodeChildManagement:

    @staticmethod
    def test_collect_descendants_basic_success():
        root = MockNode2Children()
        inter = MockNode1Child()
        c1 = MockNodeNoChildren()
        c2 = MockNodeNoChildren()

        root._children = [c1, inter]
        inter._children = [c2]

        # test root get descendants
        assert root.collect_descendants(traversal_mode='collect') == set([root, inter, c1, c2])
        assert inter.collect_descendants(traversal_mode='collect') == set([inter, c2])
        assert c1.collect_descendants(traversal_mode='collect') == set([c1])

    @staticmethod
    def test_collect_descendants_basic_failure__repeat_children():
        root = MockNode2Children()
        inter1 = MockNode1Child()
        inter2 = MockNode1Child()
        child = MockNodeNoChildren()

        # test failure because of cycle
        inter1._children[0] = inter2
        inter2._children[0] = inter1
        with pytest.raises(BaseNode.CycleDetectedError):
            inter2.collect_descendants(traversal_mode='collect')

        # test failure because child appears twice in two separate branches. 
        inter1._children[0] = child
        root._children[1] = inter1
        root._children[0] = child

        with pytest.raises(BaseNode.CycleDetectedError):
            root.collect_descendants(traversal_mode='collect')

    @staticmethod
    def test_collect_descendants_attach_mode_success__children_updated_correctly():
        root = MockNode2Children()
        inter1 = MockNode1Child()
        inter2 = MockNode1Child()
        child1 = MockNodeNoChildren()
        child2 = MockNodeNoChildren()
        
        root._children[0] = child1
        root._children[1] = inter1
        inter1._children[0] = inter2
        inter2._children[0] = child2

        # verify actual collection still works
        assert root.collect_descendants(traversal_mode='attach') == set([root, inter1, inter2, child1, child2])

        # verify properties updated correctly
        assert root._parent is None
        assert root._depth == 0
        assert child1._parent is root
        assert child1._depth == root._depth + 1
        assert inter1._parent is root
        assert inter1._depth == root._depth + 1
        assert inter2._parent is inter1
        assert inter2._depth == inter1._depth + 1
        assert child2._parent is inter2
        assert child2._depth == inter2._depth + 1

    @staticmethod
    def test_collect_descendants_attach_mode_success__hook_called_correctly():
        root = MockNode2Children()
        inter1 = MockNode1Child()
        inter2 = MockNode1Child()
        child1 = MockNodeNoChildren()
        child2 = MockNodeNoChildren()
        
        root._children[0] = child1
        root._children[1] = inter1
        inter1._children[0] = inter2
        inter2._children[0] = child2

        # verify actual collection still works
        assert root.collect_descendants(traversal_mode='attach') == set([root, inter1, inter2, child1, child2])
        # verify hook called correctly
        assert 1 in root._list
        assert 1 in child1._list
        assert 1 in inter1._list
        assert 1 in inter2._list
        assert 1 in child2._list

    @staticmethod
    def test_collect_descendants_attach_mode_failure__changes_rolled_back():
        root = MockNode2Children()
        inter1 = MockNode1Child()
        inter2 = MockNode1Child()
        inter3 = MockNode1Child()
        child1 = MockNodeNoChildren()
        
        root._children[0] = child1
        root._children[1] = inter1
        inter1._children[0] = inter2
        inter2._children[0] = inter3

        assert root.collect_descendants(traversal_mode='attach') == set([root, child1, inter1, inter2, inter3])
        # NOTE: 1 should be added to all lists

        # before
        assert root._parent is None
        assert root._depth == 0
        assert child1._parent is root
        assert child1._depth == root._depth + 1
        assert inter1._parent is root
        assert inter1._depth == root._depth + 1
        assert inter2._parent is inter1
        assert inter2._depth == inter1._depth + 1

        # create cycle
        inter3._children[0] = inter1
        try:
            # should throw an error and rollback changes
            inter3.collect_descendants(traversal_mode='attach')
            # NOTE: Should attempt to add 1 to all lists, but should get rolled back
        except BaseNode.CycleDetectedError as e:
            pass

        # after (should be same as before)
        assert root._parent is None
        assert root._depth == 0
        assert child1._parent is root
        assert child1._depth == root._depth + 1
        assert inter1._parent is root
        assert inter1._depth == root._depth + 1
        assert inter2._parent is inter1
        assert inter2._depth == inter1._depth + 1

    @staticmethod
    def test_collect_descendants_attach_mode_failure__hook_rolled_back_correctly():
        root = MockNode2Children()
        inter1 = MockNode1Child()
        inter2 = MockNode1Child()
        inter3 = MockNode1Child()
        child1 = MockNodeNoChildren()
        
        root._children[0] = child1
        root._children[1] = inter1
        inter1._children[0] = inter2
        inter2._children[0] = inter3

        assert root.collect_descendants(traversal_mode='attach') == set([root, child1, inter1, inter2, inter3])
        # NOTE: 1 should be added to all lists

        # create cycle
        inter3._children[0] = inter1
        try:
            # should throw an error and rollback changes
            inter3.collect_descendants(traversal_mode='attach')
            # NOTE: Should attempt to add 1 to all lists, but should get rolled back
        except BaseNode.CycleDetectedError as e:
            pass

        # assert on_collect_descendants_attach() rolled back
        assert root._list == [1]
        assert child1._list == [1]
        assert inter1._list == [1]
        assert inter2._list == [1]
        assert inter3._list == [1]

    @staticmethod
    def test_collect_descendants_detach_mode_success__children_updated_correctly():
        root = MockNode2Children()
        inter1 = MockNode1Child()
        inter2 = MockNode1Child()
        child1 = MockNodeNoChildren()
        child2 = MockNodeNoChildren()
        
        root._children[0] = child1
        root._children[1] = inter1
        inter1._children[0] = inter2
        inter2._children[0] = child2

        root.collect_descendants(traversal_mode='attach')

        inter1._children[0] = None
        inter2._depth = 0
        inter2._parent = None
        assert inter2.collect_descendants(traversal_mode='detach') == set([inter2, child2])

        assert inter2._depth == 0
        assert inter2._parent is None
        assert child2._depth == inter2._depth + 1
        assert child2._parent is inter2

    @staticmethod
    def test_collect_descendants_detach_mode_success__hook_called_correctly():
        root = MockNode2Children()
        inter1 = MockNode1Child()
        inter2 = MockNode1Child()
        child1 = MockNodeNoChildren()
        child2 = MockNodeNoChildren()
        
        root._children[0] = child1
        root._children[1] = inter1
        inter1._children[0] = inter2
        inter2._children[0] = child2

        root.collect_descendants(traversal_mode='attach')

        inter1._children[0] = None
        inter2._depth = 0
        inter2._parent = None
        assert inter2.collect_descendants(traversal_mode='detach') == set([inter2, child2])

        # verify on_collect_descendant_detach was called, removing 1 from _list
        assert 1 not in inter2._list
        assert 1 not in child2._list

    # - - Test add_child - -

    @staticmethod
    def test_basic_add_child_success():
        root = MockNode2Children()
        child = MockNodeNoChildren()

        index = root.add_child(child, index=0)
        assert index == 0

        assert root._children[index] is child
        assert all((root._children[i] is None) for i in range(len(root._children)) if i != index)
        assert root.num_children == 1

        assert child._depth == root.child_depth

    @staticmethod
    def test_add_child_auto_index_success():
        root = MockNode2Children()
        child = MockNode1Child()

        # should automatically be added to first slot capable of taking MockChild1 nodes,
        # in this case, at index 1
        index = root.add_child(child)
        assert index == 1           
        assert root._children[index] is child
        assert all((root._children[i] is None) for i in range(len(root._children)) if i != index)

    @staticmethod
    def test_add_child_recursively_sets_properties():
        root = MockNode2Children()
        inter = MockNode1Child()
        child = MockNodeNoChildren()

        inter.add_child(child, index=0)
        root.add_child(inter)

        assert root._depth == 0
        assert inter._depth == root._depth + 1
        assert child._depth == root._depth + 2

    @staticmethod
    def test_add_child_failure__child_already_in_node_child_list():
        root = MockNode2Children()
        child = MockNodeNoChildren()

        root.add_child(child)

        with pytest.raises(ValueError, match="new_child already in list of children"):
            root.add_child(child)
            
    @staticmethod
    def test_add_child_failure__index_occupied():
        root = MockNode2Children()
        child1 = MockNode1Child()
        child2 = MockNodeNoChildren()

        root.add_child(child2, 1)

        # test explicit attempt to overwrite an index
        with pytest.raises(IndexError, match="Another child already exists at index"):
            root.add_child(child1, 1)

        # test attempt to find an available slot when none are open
        with pytest.raises(IndexError, match="No available indeces available"):
            root.add_child(child1)            # MockNode1 only valid at index 1, which is occupied, so should fail to find a slot

    @staticmethod
    def test_add_child_failure__invalid_type():
        root = MockNode2Children()
        child1 = MockNode1Child()
        child2 = MockNode2Children()

        with pytest.raises(TypeError, match="new_child does not match possible child types"):
            root.add_child(child1, 0)         # MockChild1 only acceptable at index 1

        with pytest.raises(TypeError, 
                           match="not in the possible_children list for any child index"):
            root.add_child(child2)

    @staticmethod
    def test_add_child_failure__child_already_has_parent():
        root1 = MockNode1Child()
        root2 = MockNode1Child()
        child = MockNodeNoChildren()

        root1._children[0] = child
        child._parent = root1

        with pytest.raises(ValueError,
                           match="New child already has a parent."):
            root2.add_child(child)

    @staticmethod
    def test_add_child_failure__node_causes_cycle():
        root = MockNode2Children()
        inter1 = MockNode1Child()
        inter2 = MockNode1Child()

        # immediate cycle
        root._children[0] = inter1
        inter1._parent = root
        with pytest.raises(ValueError,
                           match='New child caused a cycle.'):
            inter1.add_child(root)

        # three layer cycle
        inter1._children[0] = inter2
        inter2._parent = inter1
        with pytest.raises(ValueError,
                           match='New child caused a cycle.'):
            inter2.add_child(root)

    @staticmethod
    def test_roll_back_success_after_add_child_failure():
        root = MockNode2Children()
        inter1 = MockNode1Child()
        inter2 = MockNode1Child()
        inter3 = MockNode1Child()
        
        inter2.add_child(inter3)
        inter1.add_child(inter2)
        root.add_child(inter1)

        assert inter1._depth == root._depth + 1
        try:
            inter3.add_child(inter1)
        except ValueError:
            assert inter1 not in inter3.children
            assert inter1._depth != inter3._depth + 1
            assert inter1._depth == root._depth + 1
            assert inter1._parent is root
        

    # - - Other child functions- -

    @staticmethod
    def test_pop_children():
        root = MockNode2Children()
        inter = MockNode1Child()
        child = MockNodeNoChildren()

        inter.add_child(child, index=0)
        root.add_child(inter, index=1)

        popped = root.pop_child(1)
        assert popped is inter
        assert root._children[1] is None
        assert root.num_children == 0

        assert inter._depth == 0
        assert inter._parent is None
        assert child in inter._children

        assert child._depth == inter._depth + 1        

    @staticmethod
    def test_remove_all_children():
        root = MockNode2Children()
        
        for _ in range(2):
            root.add_child(MockNodeNoChildren())

        children_cpy= root.children

        root.remove_all_children()
        assert len(root._children) == root.max_num_children
        assert root.num_children == 0
        assert all(c is None for c in root.children)

        assert all([(child._depth == 0) for child in children_cpy])
        assert all([(child._parent is None) for child in children_cpy])


    @staticmethod
    def test_replace_child():
        root = MockNode2Children()
        child = MockNodeNoChildren()

        index = root.add_child(child)

        # test replacing a child with itself (should work)
        old_child = root.replace_child(index, child)      
        assert old_child._depth != 0

        # test replacing a child with another node
        new_child = MockNodeNoChildren()
        old_child = root.replace_child(index, new_child)

        assert root._children[index] is new_child
        assert new_child._depth == root.child_depth

        assert old_child is child
        assert old_child not in root._children
        assert old_child._depth == 0

    @staticmethod
    def test_get_index_of_child():
        root = MockNode2Children()
        child = MockNodeNoChildren()
        root.add_child(child, index=0)
        assert root.get_index_of_child(child) == 0
        assert root.get_index_of_child(MockNodeNoChildren()) == -1
        

if __name__ == '__main__':
    tests = TestBaseNodeChildManagement()
    tests.test_collect_descendants_attach_mode_failure__hook_rolled_back_correctly()