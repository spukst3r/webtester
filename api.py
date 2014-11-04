import json

methods = {}


def error(message, code=400):
    return {
        'error': message
    }, code


def api_method(**kwargs):
    if 'name' not in kwargs:
        raise ValueError("'name' argument is required")

    def make_wrapper(f):
        name = kwargs['name']
        methods[name] = {
            'func': f,
            'methods': kwargs.get('methods', ['GET']),
        }

        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper
    return make_wrapper


def call(api_method, path, arguments, method='GET'):
    if api_method in methods:
        m = methods[api_method]

        try:
            if method not in m['methods']:
                return error("Unsupported method: {}".format(method))

            return json.dumps(m['func'](path, arguments,
                                        method))
        except Exception as e:
            return error(e.message, 500)
    else:
        return error("Method {} does not exist".format(method))


def nomethod(*args, **kwargs):
    return error("No method with such name exists")


@api_method(name='theme', methods=['GET', 'POST'])
def theme(path, args, method):
    def list():
        return []

    def get(id):
        return id

    id = args['id']

    if not id:
        return list()
    else:
        return {'id': get(id)}
