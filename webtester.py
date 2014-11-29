from flask import Flask, request
from flask.ext.cors import cross_origin

import json
import yaml
import api

app = Flask('webtester')


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


if __name__ == '__main__':
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/<path:path>')
    def auth(path):
        return app.send_static_file(path)

    with open('config.yml') as cnf:
        config = yaml.load(cnf)['webtester']

    app.secret_key = config.pop('secret_key', None)
    app.config.update(config)

    app.run(debug=True)
