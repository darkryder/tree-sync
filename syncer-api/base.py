from exceptions import AttributeError, NotImplementedError, RuntimeError
from utils import hash_md5
# import pdb

DEFAULT_HASH_VALUE = '0'


class InformationNode(object):

    def __init__(self, pk, **info_data):
        if not info_data:
            info_data = {}
        self._set_base_attribute('_base_attributes',
            ['_data_holder', '_pk', '_info_hash',])
        self._set_base_attribute('_data_holder', info_data)
        self._set_base_attribute('_pk', pk)
        self._set_base_attribute('_info_hash', None)
        self._update_hash()

    def _set_base_attribute(self, name, value):
        """ Sets the base attributes of the InformationNode
        without stepping on the toes of setattr, which
        basically calls for updating hash on changes
        """
        super(InformationNode, self).__setattr__(name, value)

    def _update_hash(self):
        """Updates information hash and if update
        of whole tree is required adds the pk to
        the update hash queue"""
        new = hash_md5(str(self))
        if new != self._info_hash:
            self._info_hash = new

    def __setattr__(self, name, value):
        """Sets attribute and updates _info_hash"""
        if name in self._base_attributes:
            self._set_base_attribute(name, value)
        else:
            self._data_holder[name] = value
        if name == '_info_hash': return # to prevent recursion
        self._update_hash()

    def __getattr__(self, name):
        if name not in self._data_holder:
            raise AttributeError(name)
        return self._data_holder[name]

    def __delattr__(self, name):
        """ Deletes an attribute and updates hash
        """
        if name not in self._data_holder:
            raise AttributeError(name)
        del self._data_holder[name]
        self._update_hash()

    def __str__(self):
        return str(self._pk) + str(self._data_holder)


class Node(object):
    def __init__(self, pk, update_hash_queue, _depth=0, **info_data):
        self._set_base_attribute('_pk', pk)
        self._set_base_attribute('_parent', None)
        self._set_base_attribute('_update_hash_queue', update_hash_queue)
        self._set_base_attribute('_children', [])
        self._set_base_attribute('_number_of_children',
            lambda: len(self._children))
        self._set_base_attribute('_children_hash', DEFAULT_HASH_VALUE)
        self._set_base_attribute('_hash', DEFAULT_HASH_VALUE)
        self._set_base_attribute('_depth', _depth)
        self._set_base_attribute('_info',
            InformationNode(pk, **info_data))
        self._set_base_attribute('_base_attributes',[
            '_pk', '_parent', '_update_hash_queue', '_depth'
            '_children', '_children_hash', '_hash', '_info'])

        self._update_hash()

    def _set_base_attribute(self, name, value):
        """ Sets the base attributes of the Node
        without stepping on the toes of setattr, which
        basically calls for updating hash on changes
        """
        super(Node, self).__setattr__(name, value)

    def __setattr__(self, name, value):
        """ Sets pk, parent, children of self,
        else it passes other information to its info node.
        returns whether an update on hash is required for the tree
        """
        if name in self._base_attributes:
            self._set_base_attribute(name, value)
        else:
            setattr(self._info, name, value)
        if name in ['_hash', '_children_hash']: return # to prevent recursion
        self._update_hash()

    def __getattr__(self, name):
        return getattr(self._info, name)

    def __delattr__(self, name):
        self._info.__delattr__(name)
        self._update_hash()

    # never call this. Always call self._update_hash()
    def _update_children_hash(self):
        """ Updates children hash.
        """
        if not self._children:
            self._set_base_attribute('_children_hash', DEFAULT_HASH_VALUE)
            return
        temp = ''.join((x.get_hash() for x in self._children))
        self._children_hash = hash_md5(temp)

    def _update_hash(self):
        """ Updates hash of self, as well as of the tree.
        If hash has changed. Insert self pk into _update_hash_queue
        so as to inform that I have a new updated hash, and the
        corresponding parents should be updated too.
        """

        old = self.get_hash()
        self._info._update_hash()
        self._update_children_hash() # assumes that all children have clean hash
        self._hash = hash_md5(self.get_children_hash() + self.get_info_hash())
        new = self.get_hash()

        if new != old:
            # propogate hash upwards
            self._update_hash_queue.add(self._pk)

    def get_info_hash(self): return self._info._info_hash
    def get_children_hash(self): return self._children_hash
    def get_hash(self): return self._hash

    def get_sync_hash(self):
        return (self.get_hash(),
                self.get_info_hash(),
                self.get_children_hash(),
                )

    def add_child(self, node):
        if not isinstance(node, Node):
            raise NotImplementedError("Child should be of type " + type(self))
        node._parent = self
        self._children.append(node)
        self._update_hash()

    def remove_child(self, node):
        raise NotImplementedError(
            "Delete child by setting a deleted=True to its info, \
            and handle it")


class SyncTree(object):
    def __init__(self, **root_info_data):
        if not root_info_data:
            raise RuntimeError(
                "Tree should be initialised with root node data")
        self.update_hash_queue = set()
        self.root = Node(0, self.update_hash_queue, _depth=0, **root_info_data)
        self.root._parent = self.root
        self._last_pk = 0
        self._pk_to_node_mapper = {0: self.root}

    def add_node(self, parent, **info_data):
        self._last_pk += 1
        node = Node(self._last_pk, self.update_hash_queue,
                    _depth = parent._depth + 1, **info_data)
        parent.add_child(node)
        self._pk_to_node_mapper[self._last_pk] = node
        return node

    def remove_node(self, node):
        raise RuntimeError(
            "Delete node by setting a deleted=True to its info and all it's \
            children, and handle it")

    def get_node(self, pk):
        node = self._pk_to_node_mapper.get(pk, None)
        if node is None:
            raise RuntimeError(
                "Could not find node corresponding to pk: " + repr(pk))
        return node

    def refresh_tree(self):
        """ Refreshes the Sync tree hashes
        """
        final_recursive_parents = set(self.get_node(x) for x in self.update_hash_queue)

        for x in self.update_hash_queue:
            node = self.get_node(x)
            if node == node._parent: break
            final_recursive_parents.add(node._parent)

        progress = {node: False for node in final_recursive_parents}

        for node in sorted(list(final_recursive_parents),
                key=lambda x: x._depth, reverse=True):
            if progress[node]: continue
            node._update_hash()
            progress[node] = True

        self.update_hash_queue.clear()