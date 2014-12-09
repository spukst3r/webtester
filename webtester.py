from flask import Flask, request
from flask.ext.cors import cross_origin
from werkzeug import exceptions
from models import JSONSerializer

import json
import yaml
import api

app = Flask('webtester')


@app.route('/api/<method>/', defaults={'id': None}, methods=['GET', 'POST'])
@app.route('/api/<method>/<int:id>', methods=['GET', 'DELETE', 'PUT', 'PATCH'])
@cross_origin()
def call_api(method, **kwargs):
    post_data = request.form

    try:
        j = request.get_json()

        if j:
            post_data = j
    except exceptions.BadRequest:
        pass

    result, code = api.call(method,
                            request.args,
                            post_data,
                            kwargs,
                            request.method)

    return json.dumps(result, ensure_ascii=False, cls=JSONSerializer), code


with open('config.yml') as cnf:
    config = yaml.load(cnf)['webtester']

app.secret_key = config.pop('secret_key', None)
app.config.update(config)

if __name__ == '__main__':
    @app.route('/')
    @app.route('/index.html')
    @app.route('/<path:path>')
    def index(path=''):
        return app.send_static_file('index.html')

    @app.route('/js/<path:path>')
    @app.route('/css/<path:path>')
    @app.route('/img/<path:path>')
    @app.route('/bower_components/<path:path>')
    def static_components(path):
        return app.send_static_file(request.path.replace('/', '', 1))

    app.run(debug=True, host='0.0.0.0')
