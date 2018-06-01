from flask import Flask, render_template, request
from sysearch import node_set
app = Flask(__name__)


@app.route('/')
def list_devices():
    devices = node_set.by_type('device')
    if request.args.get('haschildren') == 'true':
        devices = [device for device in devices if device.children]
    return render_template('devices.html', devices=devices)


@app.route('/device/<node_id>')
def node(node_id=None):
    if node_id:
        node = node_set.get_by_id(node_id)
        return render_template('node.html', node=node)
    return 'No query string'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
