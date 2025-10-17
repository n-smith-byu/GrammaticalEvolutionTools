from grammaticalevolutiontools._base_node import BaseNode

import warnings
import numpy as np

import pytest

class MockRootNode(BaseNode):
    @property
    def _possible_children_dict(self):
        return {
            0: [MockChildNode, MockChildNode],
            1: [MockMiddleNode, MockChildNode]
        }
    @property
    def _special_probs_dict(self):
        return {1: [3, 10]}
    @property
    def _all_possible_children(self):
        return {MockChildNode, MockMiddleNode}
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

class MockChildNode(BaseNode):
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
        return "child2"
    @property
    def token(self):
        return "C2"
    @property
    def is_terminal(self):
        return True
    @property
    def is_root(self):
        return False
    
class MockMiddleNode(BaseNode):
    @property
    def _possible_children_dict(self):
        return {0: [MockChildNode, MockMiddleNode]}
    @property
    def _special_probs_dict(self):
        return {}
    @property
    def _all_possible_children(self):
        return {MockChildNode, MockMiddleNode}
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

# ---------------------
# Assertion Method Tests
# ---------------------

# Testing Basic Assertions

def test_assert_token_valid():
    BaseNode._assert_token_valid("abc")
    with pytest.raises(ValueError):
        BaseNode._assert_token_valid("")
    with pytest.raises(TypeError):
        BaseNode._assert_token_valid(123)

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

def test_assert_label_valid():
    BaseNode._assert_label_valid("label")
    BaseNode._assert_label_valid("")
    BaseNode._assert_label_valid(None)
    with pytest.raises(TypeError):
        BaseNode._assert_label_valid(5)

def test_assert_tags_valid():
    BaseNode._assert_tags_valid(is_terminal=False, is_root=True)
    with pytest.raises(TypeError):
        BaseNode._assert_tags_valid("yes", True)
    with pytest.raises(TypeError):
        BaseNode._assert_tags_valid(True, "yes")
    with pytest.raises(ValueError):
        BaseNode._assert_tags_valid(is_terminal=True, is_root=True)


# Testing Complex Assertions

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


class TestChildProbsAssertions:

    """test assert_child_probs_valid"""

    def test_assert_child_probs_valid_success(self):
        BaseNode._assert_child_probs_valid(np.array([0.5, 0.5]), [int, str])

    def test_assert_child_probs_valid_non_1d_array(self):
        with pytest.raises(ValueError, 
                           match="Could not convert to a 1-D numpy array"):
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


# ---------------------
# Probabilities and Static Utils
# ---------------------

def test_probs_to_numpy():
    arr = BaseNode.probs_to_numpy([0.2, 0.8])
    assert isinstance(arr, np.ndarray)
    assert arr.shape == (2,)
    assert arr.dtype == np.float64

def test_convert_probs_dict_to_numpy():
    probs_dict = {
        0: [0.3, 0.7],
        1: [0.5, 0.5]
    }
    converted = BaseNode.convert_probs_dict_to_numpy(probs_dict)
    assert all(isinstance(v, np.ndarray) for v in converted.values())
    assert all((key in converted) for key in probs_dict)
    assert all(np.all(probs_dict[key] == converted[key]) for key in probs_dict)

def test_get_possible_children_and_probs():
    node = MockRootNode()
    children, probs = node.get_possible_children_and_probs(0)
    assert isinstance(children, list)
    assert isinstance(probs, np.ndarray)
    assert np.isclose(probs.sum(), 1.0)

# ---------------------
# Child Management Tests
# ---------------------

class TestBaseNodeBehavior:

    # - - Test init and property methods - -

    @staticmethod
    def test_init_function():
        node1 = MockRootNode()
        
        assert node1.children == [None, None]
        assert node1._num_children == 0
        assert node1._depth == 0

        node2 = MockRootNode()
        assert node2._identifier != node1._identifier

    @staticmethod
    def test_basic_property_methods():
        node = MockRootNode()
        node._children[0] == MockMiddleNode()
        node._children[1] == MockChildNode()

        assert node.num_children == node._num_children
        assert node.child_depth == node._depth + 1
        assert node.children is not node._children
        assert node.children == node._children

    @staticmethod
    def test_possible_children_dict_property_method():
        node = MockRootNode()
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
        node = MockRootNode()
        sp = node.special_probs_dict

        assert sp is not node._special_probs_dict
        assert isinstance(sp, dict)

        # test 
        for ind, probs_list in node._special_probs_dict.items():
            assert ind in sp
            assert isinstance(sp[ind], list)
            assert sp[ind] is not probs_list
            assert sp[ind] == probs_list


    # - - Test add_child - -

    @staticmethod
    def test_basic_add_child_success():
        root = MockRootNode()
        child = MockChildNode()

        index = root.add_child(child, index=0)
        assert index == 0

        assert root._children[index] is child
        assert all((root._children[i] is None) for i in range(len(root._children)) if i != index)
        assert root.num_children == 1

        assert child._depth == root.child_depth

    @staticmethod
    def test_add_child_auto_index_success():
        root = MockRootNode()
        child = MockMiddleNode()

        # should automatically be added to first slot capable of taking MockChild1 nodes,
        # in this case, at index 1
        index = root.add_child(child)
        assert index == 1           
        assert root._children[index] is child
        assert all((root._children[i] is None) for i in range(len(root._children)) if i != index)

    @staticmethod
    def test_add_child_recursive_properties():
        root = MockRootNode()
        inter = MockMiddleNode()
        child = MockChildNode()

        inter.add_child(child, index=0)
        root.add_child(inter)

        assert root._depth == 0
        assert inter._depth == root._depth + 1
        assert child._depth == root._depth + 2

    @staticmethod
    def test_add_child_failure_child_already_a_child():
        root = MockRootNode()
        child = MockChildNode()

        root.add_child(child)

        with pytest.raises(ValueError, match="new_child already in list of children"):
            root.add_child(child)

    @staticmethod
    def test_roll_back_success_after_add_child_failure():
        root = MockRootNode()
        inter1 = MockMiddleNode()
        inter2 = MockMiddleNode()
        inter3 = MockMiddleNode()
        
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
            
    @staticmethod
    def test_add_child_failures_index_occupied():
        root = MockRootNode()
        child1 = MockMiddleNode()
        child2 = MockChildNode()

        root.add_child(child2, 1)

        # test explicit attempt to overwrite an index
        with pytest.raises(IndexError, match="Another child already exists at index"):
            root.add_child(child1, 1)

        # test attempt to find an available slot when none are open
        with pytest.raises(IndexError, match="No available indeces available"):
            root.add_child(child1)            # MockNode1 only valid at index 1, which is occupied, so should fail to find a slot

    @staticmethod
    def test_add_child_failures_invalid_type():
        root = MockRootNode()
        child1 = MockMiddleNode()
        child2 = MockRootNode()

        with pytest.raises(TypeError, match="new_child does not match possible child types"):
            root.add_child(child1, 0)         # MockChild1 only acceptable at index 1

        with pytest.raises(TypeError, 
                           match="not in the possible_children list for any child index"):
            root.add_child(child2)

    @staticmethod
    def test_add_child_failures_repeat_node():
        root = MockRootNode()
        inter1 = MockMiddleNode()
        inter2 = MockMiddleNode()
        child = MockChildNode()

        inter1.add_child(inter2)
        with pytest.raises(ValueError, 
                           match="Node could not be added because it will cause a cycle to form."):
            inter2.add_child(inter1)

        inter2.add_child(child)
        root.add_child(child, index=0)
        root.add_child(inter1, index=1)
        


    # - - Other child functions- -

    @staticmethod
    def test_pop_children():
        root = MockRootNode()
        inter = MockMiddleNode()
        child = MockChildNode()

        inter.add_child(child, index=0)
        root.add_child(inter, index=1)

        popped = root.pop_child(1)
        assert popped is inter
        assert root._children[1] is None
        assert root.num_children == 0

        assert inter._depth == 0
        assert child in inter._children

        assert child._depth == inter._depth + 1        

    @staticmethod
    def test_remove_all_children():
        root = MockRootNode()
        
        for _ in range(2):
            root.add_child(MockChildNode())

        children_cpy= root.children

        root.remove_all_children()
        assert len(root._children) == root.max_num_children
        assert root.num_children == 0
        assert all(c is None for c in root.children)

        assert all([(child._depth == 0) for child in children_cpy])


    @staticmethod
    def test_replace_child():
        root = MockRootNode()
        child = MockChildNode()

        index = root.add_child(child)

        # test replacing a child with itself (should work)
        old_child = root.replace_child(index, child)      
        assert old_child._depth != 0

        # test replacing a child with another node
        new_child = MockChildNode()
        old_child = root.replace_child(index, new_child)

        assert root._children[index] is new_child
        assert new_child._depth == root.child_depth

        assert old_child is child
        assert old_child not in root._children
        assert old_child._depth == 0

    @staticmethod
    def test_get_index_of_child():
        root = MockRootNode()
        child = MockChildNode()
        root.add_child(child, index=0)
        assert root.get_index_of_child(child) == 0
        assert root.get_index_of_child(MockChildNode()) == -1


    # - - Test Collect Descendants - - 

    @staticmethod
    def test_collect_descendants_success():
        root = MockRootNode()
        inter = MockMiddleNode()
        c1 = MockChildNode()
        c2 = MockChildNode()

        inter.add_child(c2)
        root.add_child(c1)
        root.add_child(inter)

        # test root get descendants
        assert root.collect_descendants() == set([root, inter, c1, c2])
        assert root.collect_descendants(include_self=False) == set([inter, c1, c2])

        assert inter.collect_descendants() == set([inter, c2])

    @staticmethod
    def test_collect_descendants_failures_repeat_children():
        root = MockRootNode()
        inter1 = MockMiddleNode()
        inter2 = MockMiddleNode()
        child = MockChildNode()

        # test failure because of cycle
        inter1._children[0] = inter2
        inter2._children[0] = inter1
        with pytest.raises(ValueError, match="Error in recursively collecting descendants."):
            inter2.collect_descendants(inter1)

        # test failure because child appears twice in two separate branches. 
        inter1._children[0] = child
        root._children[1] = inter1
        root._children[0] = child

        with pytest.raises(ValueError, match="Error in recursively collecting descendants."):
            root.collect_descendants(child)
        

if __name__ == '__main__':
    tests = TestBaseNodeBehavior()
    tests.test_add_child_failures_repeat_node()