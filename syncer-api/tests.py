from time import time as time_now
from random import randint, choice
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
        self.assertSetEqual(parent._update_hash_queue, set([parent._pk, child._pk]))

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
        self.assertSetEqual(update_queue, set([root._pk, root_child1._pk]))
        new_root_hash = root.get_sync_hash()
        new_root_child1_hash = root_child1.get_sync_hash()

        self.assertTrue(TestNodeCore.check_sync_hash_old_new(old_root_hash, new_root_hash, False, True, False))
        self.assertTrue(TestNodeCore.check_sync_hash_old_new(old_root_child1_hash, new_root_child1_hash, True, True, True))

        root_child1.add_child(root_child1_child1)
        self.assertSetEqual(update_queue, set([root._pk, root_child1._pk, root_child1_child1._pk]))

        root.add_child(root_child2)
        self.assertSetEqual(update_queue, set([root._pk, root_child1._pk, root_child1_child1._pk, root_child2._pk]))

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

        self.assertEqual(len(update_queue), 8)

        self.assertIn(root_child1_child1_child1, root_child1_child1._children)

        # test that changing a child's description, changes its hash and adds self
        # pk in the update queue

        update_queue.remove(root_child2_child2._pk)
        old_sync_hash = root_child2_child2.get_sync_hash()
        root_child2_child2.something = "Sometihng"
        new_sync_hash = root_child2_child2.get_sync_hash()
        self.assertIn(root_child2_child2._pk, update_queue)
        self.assertTrue(TestNodeCore.check_sync_hash_old_new(
            old_sync_hash, new_sync_hash, False, False, True))

    def test_node_gets_present_time_as_updated_time_on_insertion(self):
        now = time_now()
        node = Node(0, set(), **temp_info)
        self.assertAlmostEqual(now, node.get_update_time(), places=0)


class TestSyncTreeCore(unittest.TestCase):

    def test_tree_created(self):
        tree = SyncTree(**temp_info)
        self.assertIsInstance(tree, SyncTree)

        with self.assertRaises(RuntimeError):
            temp = SyncTree()

        self.assertEqual(tree.root, tree.root._parent)
        self.assertEqual(tree.root._pk, 0)
        self.assertEqual(tree.get_node(0), tree.root)

    def test_setting_and_getting_node(self):
        tree = SyncTree(**temp_info)
        root = tree.root
        root_child1 = tree.add_node(root, **temp_info2)
        root_child2 = tree.add_node(root, **temp_info2)
        root_child1_child1 = tree.add_node(root_child1, **temp_info)

        self.assertEqual(tree.get_node(root_child2._pk), root_child2)
        self.assertEqual(tree.get_node(root_child1_child1._pk),
            root_child1_child1)

        self.assertSetEqual(tree.update_hash_queue, {
            root._pk, root_child1._pk, root_child2._pk,
            root_child1_child1._pk})

    def test_adding_node_adds_parent_to_update_queue(self):
        tree = SyncTree(**temp_info)
        root = tree.root

        tree.update_hash_queue.clear()
        node = tree.add_node(root, **temp_info2)
        self.assertIn(root._pk, tree.update_hash_queue)
        for x in range(10):
            child = tree.add_node(node, **temp_info)
            node = child

        tree.update_hash_queue.clear()
        new = tree.add_node(child, **temp_info2)

        self.assertIn(child._pk, tree.update_hash_queue)

    def test_tree_depth(self):
        tree = SyncTree(**temp_info)
        root = tree.root
        root_child1 = tree.add_node(root, **temp_info2)
        root_child2 = tree.add_node(root, **temp_info2)
        root_child1_child1 = tree.add_node(root_child1, **temp_info)

        self.assertEqual(root._depth, 0)
        self.assertEqual(root_child1._depth, 1)
        self.assertEqual(root_child2._depth, 1)
        self.assertEqual(root_child1_child1._depth, 2)


    def test_add_node_changes_hash(self):
        tree = SyncTree(**temp_info)
        root = tree.root
        old_root_hash = root.get_hash()
        root_child1 = tree.add_node(root, **temp_info2)
        new_root_hash = root.get_hash()

        self.assertTrue(TestNodeCore.check_sync_hash_old_new(old_root_hash, new_root_hash,
            False, False, False))

    def test_refresh_hash_works(self):
        tree = SyncTree(**temp_info)
        root = tree.root
        root_child1 = tree.add_node(root, **temp_info2)
        root_child2 = tree.add_node(root, **temp_info2)
        root_child1_child1 = tree.add_node(root_child1, **temp_info)

        tree.refresh_tree()

        old_sync_hashes = {x: x.get_sync_hash() for x in tree._pk_to_node_mapper.values()}
        for x in sorted(tree._pk_to_node_mapper.values(), key=lambda x: x._depth, reverse=True):
            x._update_hash()
        new_sync_hashes = {x: x.get_sync_hash() for x in tree._pk_to_node_mapper.values()}

        self.assertDictEqual(old_sync_hashes, new_sync_hashes)

    # test for recursive tree hash bug
    def test_tree_refreshes_properly_on_adding_node_way_down(self):
        tree = SyncTree(**temp_info)
        root = tree.root # pk 0
        root_child1 = tree.add_node(root, **temp_info) # pk 1
        root_child2 = tree.add_node(root, **temp_info) # pk 2
        root_child1_child1 = tree.add_node(root_child1, **temp_info) # pk 3
        root_child2_child1 = tree.add_node(root_child2, **temp_info) # pk 4

        tree.refresh_tree()

        old_sync_hashes = {x: tree.get_node(x).get_sync_hash() for x in range(5)}
        root_child1_child1_child1 = tree.add_node(root_child1_child1, **temp_info)
        tree.refresh_tree()
        new_sync_hashes = {x: tree.get_node(x).get_sync_hash() for x in range(5)}

        # root should have total hash and children hash changed
        self.assertTrue(TestNodeCore.check_sync_hash_old_new(
            old_sync_hashes[0], new_sync_hashes[0],
            False, True, False))

        # root_child1 should have total hash and children hash changed
        self.assertTrue(TestNodeCore.check_sync_hash_old_new(
            old_sync_hashes[1], new_sync_hashes[1],
            False, True, False))

        # root_child2 should have no hash change
        self.assertTrue(TestNodeCore.check_sync_hash_old_new(
            old_sync_hashes[2], new_sync_hashes[2],
            True, True, True))

        # root_child1_child1 should have total hash and children hash changed
        self.assertTrue(TestNodeCore.check_sync_hash_old_new(
            old_sync_hashes[3], new_sync_hashes[3],
            False, True, False))

        # root_child2_child1 should have no hash change
        self.assertTrue(TestNodeCore.check_sync_hash_old_new(
            old_sync_hashes[4], new_sync_hashes[4],
            True, True, True))

        self.assertTrue(TestSyncTreeCore.validate_last_updated_relationship(tree))

    def test_updated_time_gets_touched_on_adding_info(self):
        tree = SyncTree(**temp_info)
        root = tree.root # pk 0

        tree.refresh_tree()

        old = root.get_update_time()
        tree.refresh_tree()             # no change should not cause time updating
        new = root.get_update_time()
        self.assertEqual(old, new)

        root.abc = "Something"
        tree.refresh_tree()
        new = root.get_update_time()
        self.assertNotEqual(old, new)

        old = root.get_update_time()

        root_child1 = tree.add_node(root, **temp_info) # pk 1
        root_child2 = tree.add_node(root, **temp_info) # pk 2
        root_child1_child1 = tree.add_node(root_child1, **temp_info) # pk 3
        root_child2_child1 = tree.add_node(root_child2, **temp_info) # pk 4

        tree.refresh_tree()
        new = root.get_update_time()
        self.assertNotEqual(old, new)

        temp = tree.add_node(root_child1_child1, **temp_info) # pk5
        old_times = [tree.get_node(x).get_update_time() for x in range(5)]
        tree.refresh_tree()
        new_times = [tree.get_node(x).get_update_time() for x in range(5)]

        self.assertEqual(map(lambda x, y: x == y, old_times, new_times),[
            False,  # update time of root should have changed
            False,  # update time of root_child1 should have changed
            True,   # update time of root_child2 should not have changed
            False,  # update time of root_child1_child1 should have changed
            True,   # update time of root_child2_child1 should not have changed
            ]
        )
        self.assertTrue(TestSyncTreeCore.validate_last_updated_relationship(tree))

        random_tree = TestSyncTreeCore.create_random_tree(1000)
        random_tree.refresh_tree()
        self.assertTrue(TestSyncTreeCore.validate_last_updated_relationship(random_tree))

    @staticmethod
    def validate_last_updated_relationship(tree):
        nodes = tree._pk_to_node_mapper.values()
        for node in sorted(nodes, key=lambda x: x._depth, reverse=True):
            if node._parent == node: continue
            if not (node.get_update_time() <= node._parent.get_update_time()): return False
        return True

    # note to self: Isn't introducing randomness in tests horrendous?
    @staticmethod
    def create_random_tree(number_of_nodes, initial_nodes_to_randomly_create_subtrees_under=None, parent_tree=None):
        init_given = initial_nodes_to_randomly_create_subtrees_under

        if (init_given is None and parent_tree is not None) or \
            (init_given is not None and parent_tree is None): raise RuntimeError(
                "You should give parent_tree param if initial_nodes_to_randomly_create_subtrees_under is given")

        if parent_tree:
            parent_nodes_options = init_given
        else:
            parent_tree = SyncTree(**temp_info)
            parent_nodes_options = [parent_tree.root]

        for x in xrange(number_of_nodes - 1): # subtract root
            parent = choice(parent_nodes_options)
            node = parent_tree.add_node(parent, **temp_info2)
            parent_nodes_options.append(node)

        return parent_tree

    def test_that_the_time_relationship_holds(self):

        random_tree = TestSyncTreeCore.create_random_tree(1000)
        old_timings = [x.get_update_time() for x in random_tree._pk_to_node_mapper.values()]
        random_tree.refresh_tree()
        new_timings = [x.get_update_time() for x in random_tree._pk_to_node_mapper.values()]
        self.assertTrue(TestSyncTreeCore.validate_last_updated_relationship(random_tree))
        self.assertNotEqual(old_timings, new_timings)

        random_tree.refresh_tree()
        old_timings, new_timings = new_timings, [x.get_update_time() for x in random_tree._pk_to_node_mapper.values()]
        self.assertListEqual(old_timings, new_timings)

        for x in range(100):
            temp = choice(random_tree._pk_to_node_mapper.values())
            temp.abc = x
            random_tree.refresh_tree()
            old_timings, new_timings = new_timings, [x.get_update_time() for x in random_tree._pk_to_node_mapper.values()]
            self.assertNotEqual(old_timings, new_timings)


    def test_get_nodes_after_time(self):

        now = time_now()

        tree = SyncTree(**temp_info)
        root = tree.root # pk 0
        root_child1 = tree.add_node(root, **temp_info) # pk 1
        root_child2 = tree.add_node(root, **temp_info) # pk 2
        root_child1_child1 = tree.add_node(root_child1, **temp_info) # pk 3
        root_child2_child1 = tree.add_node(root_child2, **temp_info) # pk 4
        root_child2_child1_child1 = tree.add_node(root_child2_child1, **temp_info) # pk 5
        set_all = set([root, root_child1, root_child2, root_child1_child1, root_child2_child1, root_child2_child1_child1])
        empty = set()

        tree.refresh_tree()

        changed_nodes = tree.get_nodes_after_time(now)
        self.assertSetEqual(changed_nodes, set_all)

        now = time_now()
        changed_nodes = tree.get_nodes_after_time(now)
        self.assertSetEqual(changed_nodes, empty)

        root_child1_child1.abc = "asg"
        tree.refresh_tree()
        changed_nodes = tree.get_nodes_after_time(now)
        self.assertSetEqual(changed_nodes, set([root_child1_child1, root_child1, root]))

        root.abd = "asg"
        tree.refresh_tree()
        changed_nodes = tree.get_nodes_after_time(now)
        self.assertSetEqual(changed_nodes, set([root_child1_child1, root_child1, root]))

        now = time_now()
        changed_nodes = tree.get_nodes_after_time(now)
        self.assertSetEqual(changed_nodes, empty)

        root_child2_child1_child1.abc = "def"
        root_child1.abc = "def"
        tree.refresh_tree()
        self.assertEqual(tree.get_nodes_after_time(now), set([root, root_child1, root_child2, root_child2_child1, root_child2_child1_child1]))


if __name__ == '__main__':
    unittest.main()
