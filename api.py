from db import query, get_session
from models import Section
from sqlalchemy.orm.exc import NoResultFound

methods = {}


class StaticMetaclass(type):
    def __new__(cls, cls_name, cls_parents, cls_attr):
        attrs = {}

        attrs['model'] = cls_attr['model']
        cls_attr.pop('model')

        for name, val in cls_attr.items():
            if callable(val):
                attrs[name] = classmethod(val)
            else:
                attrs[name] = val

        return type.__new__(cls, cls_name, cls_parents, attrs)


class ApiMethod(object):
    __metaclass__ = StaticMetaclass
    list_attributes = []
    model = None

    def handlers(cls):
        return {
            'PUT': cls.put,
            'GET': cls.get,
            'POST': cls.post,
            'DELETE': cls.delete,
        }

    def __list(cls):
        obj_list = query(cls.model).all()

        return map(
            lambda obj: dict([(attr, getattr(obj, attr))
                              for attr in cls.list_attributes]),
            obj_list
        )

    def post(cls, id, data):
        pass

    def get(cls, id):
        try:
            if id:
                return (query(cls.model)
                        .filter_by(id=id)
                        .one()
                        .to_dict())
            else:
                return cls.__list()

        except NoResultFound:
            raise ApiError("No object with such id", 404)

    def delete(cls, id):
        try:
            query(cls.model).filter(cls.model.id == id).delete()
        except Exception as e:
            return error(e.message, 500)

    def put(cls, id, data):
        pass


class SectionMethod(ApiMethod):
    list_attributes = ['id', 'order', 'subject']
    model = Section

    def post(self, id, data):
        print 'SectionMethod::post'
        try:
            subject = data['subject']
            lection = data['lection']
            order = data['order']

            print subject, lection, order
        except KeyError as e:
            return error("Missing required parameter: {}".format(e.args[0]),
                         400)

        s = Section(subject=subject, lection=lection, order=order)

        session = get_session()
        session.add(s)
        session.commit()

        return s.id


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


class ApiError(Exception):
    def __init__(self, message, code):
        super(ApiError, self).__init__(message)
        self.code = code


def call(api_method, *args, **kwargs):
    """
    Calls specified method and returns tuple (json, code)
    """

    if api_method in methods:
        m = methods[api_method]

        if 'method' in kwargs:
            method = kwargs['method']
        else:
            method = 'GET'

        try:
            if method not in m['methods']:
                result = error("Unsupported method: {}".format(method))
            else:
                result = m['func'](*args, **kwargs), 200
        except ApiError as e:
            result = error(e.message, e.code)
        except Exception as e:
            result = error(e.message, 500)
    else:
        result = error("Method {} does not exist".format(api_method))

    return result


def nomethod(*args, **kwargs):
    return error("No method with such name exists")


@api_method(name='section', methods=['GET', 'POST', 'DELETE', 'PUT'])
def section(params, post_data, args, method):
    id = args['id']

    if method in ['GET', 'DELETE']:
        args = id,
    else:
        args = id, post_data

    return SectionMethod.handlers().get(method, nomethod)(*args)


@api_method(name='question', methods=['GET', 'POST', 'DELETE'])
def question(params, args, method):
    return []
