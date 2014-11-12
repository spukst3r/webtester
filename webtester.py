from flask import Flask, request
from flask.ext.cors import cross_origin

import json
import api

app = Flask(__name__)


@app.route('/api/<method>/', defaults={'id': None}, methods=['GET', 'POST'])
@app.route('/api/<method>/<int:id>', methods=['GET', 'DELETE', 'PUT'])
@cross_origin()
def call_api(method, **kwargs):
    result, code = api.call(method,
                            request.args,
                            request.form,
                            kwargs,
                            request.method)

    return json.dumps(result, ensure_ascii=False), code


@app.route('/')
def auth():
    return app.send_static_file('../tester-webui/auth.html')


if __name__ == '__main__':
    app.run(debug=True)
