from random import randint
import unittest
from base import SyncTree, Node, InformationNode, RuntimeError, DEFAULT_HASH_VALUE, AttributeError
from utils import hash_md5, check_valid_hash

temp_info = {
    "name": "Byld",
    "cat": "CSE",
}

temp_info2 = {
    "name": "Something",
    "cat": "Some",
}

randomPK = randint(0, 1000)

class TestInformationNode(unittest.TestCase):

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


class TestNode(unittest.TestCase):

    def test_node_creation(self):
        pass



# class TestTreeAndNodeCreations(unittest.TestCase):

    # def test_tree_created(self):
    #     tree = SyncTree(**temp_info)
    #     self.assertIsInstance(tree, SyncTree)
    #     self.assertRaises(RuntimeError, callableObj=SyncTree)
    #     self.assertEqual(tree.root, tree.root.parent)
    #     self.assertEqual(tree.root.pk, 0)
    #     self.assertEqual(tree.get_node(0), tree.root)

    # def test_node_created(self):
    #     node = Node(0, None, **temp_info)
    #     self.assertIsInstance(node,Node)
    #     self.assertListEqual(node.children, [])
    #     self.assertNotEqual(self._hash, DEFAULT_HASH_VALUE)

    # def test_node_info_on_creation(self):
    #     node = Node(0, None, **temp_info)
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