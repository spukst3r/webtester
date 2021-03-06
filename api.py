from http import client as http
from handlers import (
    SectionHandler,
    QuestionHandler,
    StatsHandler,
    AnswerHandler,
    QuizHandler,
    error,
    ApiError,
)

methods = {}


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


def call(api_method, *args, **kwargs):
    """
    Calls specified method and returns tuple (json, code)
    """

    if api_method not in methods:
        return error("Method {} does not exist".format(api_method),
                     http.BAD_REQUEST)

    m = methods[api_method]

    if 'method' in kwargs:
        method = kwargs['method']
    else:
        method = 'GET'

    try:
        if method not in m['methods']:
            result = error("Unsupported method: {}".format(method))
        else:
            result = m['func'](*args, **kwargs)
    except ApiError as e:
        result = error(str(e), e.code)
    except Exception as e:
        result = error(str(e), http.INTERNAL_SERVER_ERROR)

    return result


def nomethod(*args, **kwargs):
    return error("Unsupported method for this action")


@api_method(name='sections', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def sections(params, post_data, args, method):
    id = args['id']

    if method in ['GET', 'DELETE']:
        args = id,
    else:
        args = id, post_data

    return SectionHandler.handlers().get(method, nomethod)(*args)


@api_method(name='questions', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def questions(params, post_data, args, method):
    id = args['id']

    if method in ['GET', 'DELETE']:
        args = id,
    else:
        args = id, post_data

    return QuestionHandler.handlers().get(method, nomethod)(*args)


@api_method(name='answers', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def answers(params, post_data, args, method):
    id = args['id']

    if method in ['GET', 'DELETE']:
        args = id,
    else:
        args = id, post_data

    return AnswerHandler.handlers().get(method, nomethod)(*args)


@api_method(name='quiz', methods=['GET', 'PUT'])
def quiz(params, post_data, args, method):
    id = args['id']

    if method == 'GET':
        args = id,
    else:
        args = id, post_data

    return QuizHandler.handlers().get(method, nomethod)(*args)


@api_method(name='stats', methods=['GET'])
def stats(params, post_data, args, method):
    return StatsHandler.handlers().get(method, nomethod)()
