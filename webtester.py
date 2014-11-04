from flask import Flask, request

import api

app = Flask(__name__)


@app.route('/api/<method>/', defaults={'id': None}, methods=['GET', 'POST'])
@app.route('/api/<method>/<int:id>')
def call_api(method, **kwargs):
    return api.call(method, request.args, kwargs, request.method)


if __name__ == '__main__':
    app.run(debug=True)
