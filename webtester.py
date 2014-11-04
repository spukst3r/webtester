from flask import Flask, request

import api

app = Flask(__name__)


@app.route('/api/<method>/', defaults={'path': ''})
@app.route('/api/method/<int:id>')
@app.route('/api/<method>/<path:args>')
def call_api(method, **kwargs):
    return api.call(method, request.args, kwargs)


if __name__ == '__main__':
    app.run(debug=True)
