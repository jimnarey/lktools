from flask import Flask
from flask import render_template
from sysearch import node_set
app = Flask(__name__)


@app.route('/')
def list_devices():
    devices = node_set.by_type('device')
    print(devices)
    return render_template('devices.html', devices=devices)


@app.route('/device/<dev_id>')
def device(dev_id=None):
    if dev_id:
        device = node_set.get_by_id(dev_id)
        return render_template('device.html', device=device)
    return 'No query string'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
