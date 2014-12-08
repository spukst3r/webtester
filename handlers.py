from sqlalchemy.orm.exc import NoResultFound
from http import client as http

from db import query, get_session
from models import Section, Question, Answer


def ok(data, code=http.OK):
    return data, code


def error(message, code=http.BAD_REQUEST):
    return {
        'error': message
    }, code


class ApiError(Exception):
    def __init__(self, message, code=http.BAD_REQUEST):
        super(ApiError, self).__init__(message)
        self.code = code


class StaticMetaclass(type):
    def __new__(cls, cls_name, cls_parents, cls_attr):
        attrs = {}

        attrs['model'] = cls_attr.pop('model', None)

        for name, val in cls_attr.items():
            if callable(val):
                attrs[name] = classmethod(val)
            else:
                attrs[name] = val

        return type.__new__(cls, cls_name, cls_parents, attrs)


class MethodHandler(metaclass=StaticMetaclass):
    list_attributes = []
    block_update_attributes = []
    model = None

    def handlers(cls):
        return {
            'PUT': cls.put,
            'GET': cls.get,
            'POST': cls.post,
            'PATCH': cls.patch,
            'DELETE': cls.delete,
        }

    def get(cls, id):
        try:
            if id:
                return ok(*cls._get(id))
            else:
                return ok(*cls._list())

        except NoResultFound:
            raise ApiError("No object with such id", http.NOT_FOUND)

    def delete(cls, id):
        if not id:
            raise ApiError("Missing required parameter: id")

        return ok(*cls._delete(id))

    def post(cls, id, data):
        if id:
            raise ApiError("Invalid parameter for method: id")

        return ok(*cls._add(id, data))

    def put(cls, id, data):
        if not id:
            raise ApiError("Missing required parameter: id")

        return ok(*cls._update(id, data))

    def patch(cls, id, data):
        if not id:
            raise ApiError("Missing required parameter: id")

        return ok(*cls._update(id, data))

    def _list(cls):
        obj_list = query(cls.model).all()
        attributes = cls.list_attributes

        if not attributes:
            name = lambda o: getattr(o, 'name')

            attributes = list(map(name, cls.model.__table__.columns))

        return list(
            map(
                lambda obj: dict((attr, getattr(obj, attr))
                                 for attr in attributes),
                obj_list
            )
        ),

    def _add(cls, id, data):
        required = []
        optional = []

        for column in cls.model.__table__.columns:
            if column.name != 'id':
                if not column.nullable:
                    required.append(column.name)
                else:
                    optional.append(column.name)

        try:
            h = dict((attr, data[attr])
                     for attr in required)
        except KeyError as e:
            raise ApiError("Missing required parameter: {}".format(e.args[0]))

        if id:
            h['id'] = id

        for o in optional:
            if o in data:
                h.update({o: data[o]})

        obj = cls.model(**h)
        session = get_session()

        session.add(obj)
        session.commit()

        return obj.to_dict(), http.CREATED

    def _get(cls, id):
        return (query(cls.model)
                .filter_by(id=id)
                .one()
                .to_dict()),

    def _delete(cls, id):
        session = get_session()

        try:
            s = session.query(cls.model).filter(cls.model.id == id).one()
        except NoResultFound:
            return None, http.NO_CONTENT

        session.delete(s)
        session.commit()

        return None, http.ACCEPTED

    def _update(cls, id, data):
        session = get_session()

        try:
            s = session.query(cls.model).filter(cls.model.id == id).one()
        except NoResultFound:
            return cls._add(id, data)

        for key, val in data.items():
            if key not in cls.block_update_attributes:
                setattr(s, key, val)

        session.add(s)
        session.commit()

        return s.to_dict(),


class SectionHandler(MethodHandler):
    model = Section


class QuestionHandler(MethodHandler):
    model = Question


class AnswerHandler(MethodHandler):
    model = Answer


class StatsHandler(MethodHandler):
    def handlers(cls):
        return {
            'GET': cls.get
        }

    def get(cls):
        return ok({
            'admin': True,
        })
