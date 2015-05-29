from flask import Flask, jsonify, request
from exceptions import RuntimeError, ValueError
from base import SyncTree, Node


class Handler(object):
    def __init__(self, tree):
        self.tree = tree

    def _get_node(self, request):
        try:
            return self.tree.get_node(int(request.args.get('pk', None)))
        except (RuntimeError, ValueError) as e:
            return None

    def check(self, request):
        node = self._get_node(request)
        if node is None:
            return jsonify(success=False, error_message="Could not find pk")
        return jsonify(success=True, data=str(vars(node)))

    def fetch(self, request):
        pass

    def check_children(self, request):
        pass


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
        @self.app.route('/api/sync')
        def end_point():
            request_type = request.args.get('type', 'check')
            handle_request = {'check': self.handler.check,
                              'fetch': self.handler.fetch,
                              'check_children': self.handler.check_children}
            if request_type not in handle_request:
                return jsonify(success=False,
                               error_message="Unknown API call type.")
            return handle_request[request_type](request)

if __name__ == '__main__':
    example = Example()
    example.app.run()
