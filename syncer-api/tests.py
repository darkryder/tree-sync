from random import randint
import unittest
from base import SyncTree, Node, InformationNode, RuntimeError, DEFAULT_HASH_VALUE, AttributeError, NotImplementedError
from utils import hash_md5, check_valid_hash

temp_info = {
    "name": "Byld",
    "cat": "CSE",
}

temp_info2 = {
    "name": "Something",
    "cat": "Some",
}

getRandomPK = lambda : randint(0, 1000)
randomPK = getRandomPK()

class TestInformationNodeCore(unittest.TestCase):

    def test_information_node_creation(self):
        info_node = InformationNode(randomPK, **temp_info)
        self.assertIsInstance(info_node, InformationNode)
        self.assertEqual(info_node._pk, randomPK)
        self.assertEqual(info_node._data_holder, temp_info)
        self.assertEqual(info_node._info_hash, hash_md5(str(info_node)))
        self.assertTrue(check_valid_hash(info_node._info_hash))

    def test_setting_getting_and_deleting_any_attributes(self):
        empty_info_node = InformationNode(randomPK)
        self.assertDictEqual(empty_info_node._data_holder, {})

        info_node = InformationNode(randomPK, **temp_info)

        # checking defaults
        for k,v in temp_info.iteritems():
            self.assertEqual(getattr(info_node, k), v)

        # setting anything
        info_node.one_var = "one_var"
        info_node.two_var = {'ab': '12'}
        info_node.two_var = 1251

        # getting vars
        self.assertEqual(info_node.one_var, "one_var")
        self.assertEqual(info_node.two_var, 1251)
        self.assertRaises(AttributeError, getattr,
            info_node, 'non_existent_attribute')

        # check for deleting
        info_node.abc = "123"
        self.assertIn('abc', info_node._data_holder)
        del info_node.abc
        self.assertNotIn('abc', info_node._data_holder)

        with self.assertRaises(AttributeError):
            del info_node.anything

        # check final data
        temp = temp_info.copy()
        temp.update({
            "one_var": "one_var",
            "two_var": 1251
            })
        self.assertDictEqual(info_node._data_holder, temp)

    def test_no_hash_change_on_get(self):
        info_node = InformationNode(randomPK, **temp_info)
        old_hash = info_node._info_hash
        temp = info_node.name
        self.assertEqual(old_hash, info_node._info_hash)

    def test_hash_changes_on_setting(self):
        info_node = InformationNode(randomPK)
        old_hash = info_node._info_hash

        info_node.abc = "abc"
        new_hash = info_node._info_hash

        self.assertTrue(check_valid_hash(new_hash))
        self.assertNotEqual(new_hash, old_hash)

    def test_hash_changes_on_changes(self):
        info_node = InformationNode(randomPK, **temp_info)
        old_hash = info_node._info_hash

        info_node.name = "something else"
        new_hash = info_node._info_hash
        self.assertNotEqual(old_hash, new_hash)
        self.assertTrue(check_valid_hash(new_hash))

    def test_hash_changes_on_delete(self):
        info_node = InformationNode(randomPK, **temp_info)
        old_hash = info_node._info_hash

        del info_node.name
        new_hash = info_node._info_hash

        self.assertTrue(check_valid_hash(new_hash))
        self.assertNotEqual(old_hash, new_hash)

    def test_hash_changes_on_changing_everything(self):
        info_node = InformationNode(randomPK, **temp_info)
        old_hash = info_node._info_hash

        info_node._pk = randint(1,1000)
        new_hash = info_node._info_hash

        self.assertTrue(check_valid_hash(new_hash))
        self.assertNotEqual(old_hash, new_hash)

        info_node._data_holder = {}
        old_hash, new_hash = new_hash, info_node._info_hash

        self.assertTrue(check_valid_hash(new_hash))
        self.assertNotEqual(old_hash, new_hash)


class TestNodeCore(unittest.TestCase):

    @staticmethod
    def check_sync_hash_old_new(old_hash, new_hash, should_match_first, should_match_second, should_match_third):
        comparisons = map(lambda x, y: x == y, old_hash, new_hash)
        return all([comparisons[0] == should_match_first,
            comparisons[1] == should_match_second,
            comparisons[2] == should_match_third
            ])

    def test_node_creation(self):
        node = Node(randomPK, set())

        self.assertEqual(node._pk, randomPK)
        self.assertIsNone(node._parent)
        self.assertSetEqual(node._update_hash_queue ,set([node._pk]))
        self.assertListEqual(node._children, [])

    def test_setting_getting_deleting_data(self):
        node = Node(randomPK, set())

        self.assertDictEqual(node._info._data_holder, {})
        for k, v in temp_info.iteritems():
            setattr(node, k, v)
            self.assertEqual(getattr(node, k), v)

        node.abc = 124
        self.assertEqual(node.abc, 124)
        node.abc += 1
        self.assertEqual(node.abc, 125)

        del node.abc
        with self.assertRaises(AttributeError):
            temp = node.abc

        new_node = Node(randomPK, set(), **temp_info)
        for k,v in temp_info.iteritems():
            self.assertEqual(getattr(new_node, k), v)

    def test_hash_changes_on_setting_getting_deleting_data(self):
        node = Node(randomPK, set())

        old_hash = node.get_hash()
        node.abc = "abc"
        new_hash = node.get_hash()
        self.assertTrue(check_valid_hash(new_hash))
        self.assertNotEqual(old_hash, new_hash)

        temp = node.abc
        old_hash, new_hash = new_hash, node.get_hash()
        self.assertEqual(new_hash, old_hash)

        del node.abc
        new_hash = node.get_hash()
        self.assertTrue(check_valid_hash(new_hash))
        self.assertNotEqual(old_hash, new_hash)

    def test_add_child(self):
        update_queue = set()
        parent = Node(randomPK, update_queue)

        childPK = randomPK + 1
        old_sync_hash = parent.get_sync_hash()
        child = Node(childPK, set())
        parent.add_child(child)
        new_sync_hash = parent.get_sync_hash()

        self.assertEqual(child._parent, parent)
        self.assertIn(child, parent._children)
        self.assertEqual(parent._number_of_children(), 1)

        for x in sum((old_sync_hash, new_sync_hash), ()):
            if x != DEFAULT_HASH_VALUE:
                self.assertTrue(check_valid_hash(x))

        self.assertTrue(TestNodeCore.check_sync_hash_old_new(old_sync_hash, new_sync_hash, False, True, False))

        with self.assertRaises(NotImplementedError):
            parent.remove_child(childPK)

        # update_queue should have only parent added.
        self.assertSetEqual(parent._update_hash_queue, set([parent._pk]))

    def test_hash_and_queue_changes_in_a_complex_tree(self):
        update_queue = set()

        root = Node(randomPK, update_queue)
        root_child1 = Node(getRandomPK(), update_queue)
        root_child2 = Node(getRandomPK(), update_queue)
        root_child1_child1 = Node(getRandomPK(), update_queue)
        root_child1_child2 = Node(getRandomPK(), update_queue)
        root_child2_child1 = Node(getRandomPK(), update_queue)
        root_child2_child2 = Node(getRandomPK(), update_queue)
        root_child1_child1_child1 = Node(getRandomPK(), update_queue)

        all_nodes = [locals()[x] for x in locals().keys() if 'root' in x]

        # Each new node announces its presence in the update queue
        self.assertSetEqual(update_queue, set([x._pk for x in all_nodes]))

        update_queue = set()
        for x in all_nodes:
            x._update_hash_queue = update_queue


        #start creating relationships
        old_root_hash = root.get_sync_hash()
        old_root_child1_hash = root_child1.get_sync_hash()
        root.add_child(root_child1)
        self.assertSetEqual(update_queue, set([root._pk]))
        new_root_hash = root.get_sync_hash()
        new_root_child1_hash = root_child1.get_sync_hash()

        self.assertTrue(TestNodeCore.check_sync_hash_old_new(old_root_hash, new_root_hash, False, True, False))
        self.assertTrue(TestNodeCore.check_sync_hash_old_new(old_root_child1_hash, new_root_child1_hash, True, True, True))

        root_child1.add_child(root_child1_child1)
        self.assertSetEqual(update_queue, set([root._pk, root_child1._pk]))

        root.add_child(root_child2)
        self.assertSetEqual(update_queue, set([root._pk, root_child1._pk]))

        #create complete relationship
        root_child1.add_child(root_child1_child2)
        root_child2.add_child(root_child2_child1)
        root_child2.add_child(root_child2_child2)
        root_child1_child1.add_child(root_child1_child1_child1)

        self.assertEqual(root._number_of_children(), 2)
        self.assertEqual(root_child1._number_of_children(), 2)
        self.assertEqual(root_child2._number_of_children(), 2)
        self.assertEqual(root_child1_child1._number_of_children(), 1)
        self.assertEqual(root_child1_child2._number_of_children(), 0)
        self.assertEqual(root_child2_child1._number_of_children(), 0)
        self.assertEqual(root_child2_child2._number_of_children(), 0)

        self.assertEqual(len(update_queue), 4)

        self.assertIn(root_child1_child1_child1, root_child1_child1._children)

        # test that changing a child's description, changes its hash and adds self
        # pk in the update queue

        self.assertNotIn(root_child2_child2._pk, update_queue)
        old_sync_hash = root_child2_child2.get_sync_hash()
        root_child2_child2.something = "Sometihng"
        new_sync_hash = root_child2_child2.get_sync_hash()
        self.assertIn(root_child2_child2._pk, update_queue)
        self.assertTrue(TestNodeCore.check_sync_hash_old_new(
            old_sync_hash, new_sync_hash, False, False, True))

# class TestTreeAndNodeCreations(unittest.TestCase):

    # def test_tree_created(self):
    #     tree = SyncTree(**temp_info)
    #     self.assertIsInstance(tree, SyncTree)
    #     self.assertRaises(RuntimeError, callableObj=SyncTree)
    #     self.assertEqual(tree.root, tree.root.parent)
    #     self.assertEqual(tree.root.pk, 0)
    #     self.assertEqual(tree.get_node(0), tree.root)

    # def test_node_created(self):
    #     node = Node(0, **temp_info)
    #     self.assertIsInstance(node,Node)
    #     self.assertListEqual(node.children, [])
    #     self.assertNotEqual(self._hash, DEFAULT_HASH_VALUE)

    # def test_node_info_on_creation(self):
    #     node = Node(0, **temp_info)
    #     self.assertIsInstance(node._info, InformationNode)

    #     for k,v in temp_info.iteritems():
    #         self,assertEqual(getattr(node, k), v)

    #     # test setting and retrieving fake data
    #     node.some_anything_really_attribute = "some_data"
    #     self.assertEqual(node.some_anything_really_attribute, "some_data")
    #     self.assertEqual(node._info.some_anything_really_attribute, "some_data")
    #     self.assertEqual(node._info._data_holder['some_anything_really_attribute'], "some_data")
    #     self.assertRaises(AttributeError, getattr, args=[node, "nonexistent"])

if __name__ == '__main__':
    unittest.main()