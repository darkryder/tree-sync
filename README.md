# tree-sync

This is a simple proof of concept. In a lot of cases, where mobile apps are simply meant to show some static data, it
may be necessary to create an endpoint that the app could connect to and update its stale data.

Its unnecessary for the server to serve the complete data. What's needed is to serve only that subset of data that's
been changed after the client's last update. The concept works when the data can be logically arranged in a
hierarchical order.

The nodes of the tree can hold any information, and thus, this can be used as a generic API for syncing
elements with any kind of data. 

### Creating a hierarchical structure of data
1. Calling the `SyncTree(**root_info_data)` from  `base.py` will return a SyncTree
2. You can add a node to the parent by calling `tree.add_node(parent_node, **child_node_data)`. This
returns an `Node`
3. You can save any data in the attributes of the `Node` from `base.py`.
4. You can keep updating the data in any of the nodes. At the end, call `tree.refresh_tree()` so that the
`SyncTree` updates everything in one go, and doesn't need to traverse the tree for every update.
5. Every `Node` has a `_pk` attribute, and the node can be accessed using `tree.get_node(pk)`.
6. The node's childrens can be found by `node._children`
7. Every node has a hash assosiciated with it. It's a 3-tuple of hashes 
`(complete_hash, self_information_hash, children_hash)`

###### Example Code
```
# replace the "basic_example_tree_create" method in "serve.py"
from base import SyncTree

self.sync_tree = SyncTree(name="MyRetailStoreInformationAPI") # creates a root node
root = self.sync_tree.root

# realise that the nodes can contain _any_ information
info = self.sync_tree.add_node(root, name="Information",
                            description="About the app")
items_categories = self.sync_tree.add_node(root, type="Items categories holder",
                                      details="Stuff")
store_info = self.sync_tree.add_node(info, description="lorem ipsum",
                                  owner="Dohn Joe", branch_id=42)
pc_games = self.sync_tree.add_node(items_categories, discount=0.2)
console_games = self.sync_tree.add_node(items_categories, discount=0.5)

WoW = self.sync_tree.add_node(pc_games, reviews="wOw")
GoW3 = self.sync_tree.add_node(console_games, developers="Epic")

# That's enough sample data
self.sync_tree.refresh_tree()

# let's change something
WoW.price = 1200
WoW.currency = "INR"

store_info.manager = "Smith"

self.sync_tree.refresh_tree() # need to remember to do this.

```

So long as you use this sync_tree and refresh it finally, you can get the latest data from the server. Now let's
see how the client should understand the API responses.

### API Responses
You can start up the server by `python serve.py`

1. The first end point that the client app connects to is `/api/sync` with the GET parameter `updated_time`.
2. The server responds with the nodes that have been changed after that time. Example of a JSON format returned:
```
{
  "data": {
    "0": {
      "hash": [
        "3e9bd92dc32ed410c0558d7f94a39995",
        "0495dd1b6406ade2ceecb94508acb64d",
        "0a7c0e8cdbec85456071c611f0a7b99e"
      ],
      "updated_time": 1433082211.372208
    },
    ...
    "2": {
      "hash": [
        "2627d89cd762977b0175a9404b851898",
        "bd1707ea84f9ebeaa768cee3c32430e4",
        "b48e96208c0d0aa32a48aa4ea6bd38b2"
      ],
      "updated_time": 1433082211.372125
    },
  },
  "success": true
}
```
3. The data returned in the json is of the format `pk -> hash, updated_time`
4. The client should handle the following cases for each object returned in data. The client **should** should 
handle the objects according to the sorted order of pk.
  - The first hash matches. This means everything is up to date for that object. Simply update
  the updated_time of the corresponding object on the app.
  - The third hash doesn't match. This means a child has been changed. However the server sends the
  data of the child too. So simply update the hash and updated_time to the hash and updated_time sent by the server.
  - The second hash doesn't match. This means that data of that node has been changed.
  Append this object's pk to `pks_data_fetch_left = []`. Update the updated_time of the
  corresponding object on the app.
  - If a pk doesn't exist in the client side, this signifies a new node. Add it to a `new_children` list. Get its
  parent by calling the API endpoint `/api/sync/node/type=get_parents&pk=<pk>`. Create a new object and add the pk
  to `pks_data_fetch_left`.
5. Now call `api\sync\nodes` with GET params `type=fetch` and **multiple** `pk` params for each pk in
`pks_data_fetch_left`. For example `http://localhost:5000/api/sync/node?type=fetch&pk=1&pk=5&pk=2`
6. The returned JSON gives the complete data that's been added in the node. Update the data, hash and
updated_time on the client side. Example JSON response
```
{
  "data": {
    "1": {
      "data": {
        "description": "About the app",
        "name": "Information"
      },
      "hash": [
        "71d4ad2c887f5f932cf1eaed086c16ba",
        "f056140f9aab63cf3b388143b64c3a3a",
        "2c26891b91903f65b5cc0e427ed0a1b1"
      ]
    },
    "2": {
      "data": {
        "details": "Stuff",
        "type": "Items categories holder"
      },
      "hash": [
        "2627d89cd762977b0175a9404b851898",
        "bd1707ea84f9ebeaa768cee3c32430e4",
        "b48e96208c0d0aa32a48aa4ea6bd38b2"
      ]
    },
    "5": {
      "data": {
        "discount": 0.5
      },
      "hash": [
        "c4eba8badd0f23f3a55070dde8064522",
        "b899471983dd7e12f4ea656e78d68ca6",
        "699ff75480a6af339717756b0c578341"
      ]
    }
  },
  "success": true
}
```

### TODO
 - Create a django app that can keep the sync tree updated
 on receiving signals. Parent-Children relationships are defined between models.
