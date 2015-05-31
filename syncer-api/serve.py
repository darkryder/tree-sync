from flask import Flask, jsonify, request
from exceptions import RuntimeError, ValueError
from base import SyncTree


class Handler(object):
    def __init__(self, tree):
        self.tree = tree

    def _get_nodes(self, request):
        try:
            values = []
            for x in request.args.getlist('pk'):
                values.append(self.tree.get_node(
                    int(x)))
            return values
        except (RuntimeError, ValueError):
            return None

    def check(self, request):
        nodes = self._get_nodes(request)
        if nodes is None:
            return jsonify(success=False, error_message="Could not find pk")
        return jsonify(success=True, data={
            node._pk: node.get_sync_hash() for node in nodes})

    def fetch(self, request):
        nodes = self._get_nodes(request)
        if nodes is None:
            return jsonify(success=False, error_message="Could not find pk")
        response = {"success": True,
                    "data": {node._pk: {
                        "hash": node.get_sync_hash(),
                        "data": node._info._data_holder
                        }
                        for node in nodes}
                    }

        return jsonify(**response)

    def _get_parent(self, node):
        answer = []
        while node._parent != node:
            answer.append(node._parent._pk)
            node = node._parent
        return answer

    def get_parents(self, request):
        nodes = self._get_nodes(request)
        if nodes is None:
            return jsonify(success=False, error_message="Could not find pk")
        return jsonify(success=True,
                       data={node._pk: self._get_parent(node)
                             for node in nodes})


class Example(object):

    def __init__(self):
        self.app = Flask(__name__)
        self.app.debug = True
        self.basic_example_tree_create()
        self.handler = Handler(self.tree)
        self.set_up()

    def basic_example_tree_create(self):
        self.tree = SyncTree(name="root_node")
        root = self.tree.root
        CSE = self.tree.add_node(root, category_name="CSE events")
        ECE = self.tree.add_node(root, category_name="ECE events")

        hackathon = self.tree.add_node(CSE, event_name="Esya Hackathon", hours=16)
        prosort = self.tree.add_node(CSE, event_name="Foobar Prosort", prizes=10000)
        hackOn = self.tree.add_node(CSE, event_name="HackOn", organisers=["a", "b"])
        IOT_hackathon = self.tree.add_node(ECE, event_name="IOT", food=True)

        self.tree.refresh_tree()

    def set_up(self):
        @self.app.route('/api/sync/node')
        def end_point():
            request_type = request.args.get('type', 'check')
            handle_request = {'check': self.handler.check,
                              'fetch': self.handler.fetch,
                              'get_parents': self.handler.get_parents}
            if request_type not in handle_request:
                return jsonify(success=False,
                               error_message="Unknown API call type.")
            return handle_request[request_type](request)

        @self.app.route('/api/sync')
        def refresh_point():
            DEFAULT_STARTING_TIME = 0
            try:
                client_time = float(request.args.get(
                    'updated_time', DEFAULT_STARTING_TIME))
            except ValueError:
                client_time = DEFAULT_STARTING_TIME
            nodes = self.tree.get_nodes_after_time(client_time)
            return jsonify(success=True,
                           data={node._pk: {
                                  "hash": node.get_sync_hash(),
                                  "updated_time": node.get_update_time()}
                                 for node in nodes})


if __name__ == '__main__':
    example = Example()
    example.app.run()
