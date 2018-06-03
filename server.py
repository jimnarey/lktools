from flask import Flask, render_template, request
from sysearch import node_set
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/list/')
def list_nodes():
    node_type = request.args.get('node_type', None)
    if node_type and node_type != 'all':
        nodes = node_set.type_contains(node_type)
    else:
        # This probably isn't necessary
        nodes = list(node_set.nodes)
    if request.args.get('haschildren') == 'true':
        nodes = [node for node in nodes if node.children]
    if request.args.get('hasparent') == 'true':
        nodes = [node for node in nodes if node.parent]
    elif request.args.get('hasparent') == 'false':
        nodes = [node for node in nodes if node.parent is None]

    node_rows = []
    for node in nodes:
        node_rows.append([node.id,
                          node.base_path,
                          node.type,
                          node.file_contents.get('path'),
                          node.file_contents.get('hid'),
                          node.file_contents.get('modalias'),
                          node.fspath])

    return render_template('nodelist.html', node_rows=node_rows)


@app.route('/node/<node_id>')
def node(node_id=None):
    if node_id:
        node = node_set.get_by_id(node_id)
        return render_template('node.html', node=node)
    return 'No query string'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
