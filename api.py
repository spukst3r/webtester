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
        methods[name] = f

        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper
    return make_wrapper


def call(method, path, arguments):
    if method in methods:
        return methods[method](path, arguments)
    else:
        raise ValueError("Method {} does not exist".format(method))


def nomethod(*args, **kwargs):
    return error("No method with such name exists")


@api_method(name='theme')
def theme(path, arguments):
    def list():
        return []

    def get():
        pass

    actions = {
        'list': list,
    }

    return actions.get(path, nomethod)(path, arguments)
