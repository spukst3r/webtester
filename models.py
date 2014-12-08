import json

from sqlalchemy.ext.declarative import declarative_base, AbstractConcreteBase
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.inspection import inspect


Base = declarative_base()


class JSONSerializer(json.JSONEncoder):
    def default(self, obj):
        if callable(getattr(obj, 'to_dict')):
            return obj.to_dict()

        return json.JSONEncoder.default(self, obj)


class JsonBase(AbstractConcreteBase, Base):
    def to_dict(self):
        d = {}

        for col in self.__table__.columns:
            d[col.name] = getattr(self, col.name)

        for relation in inspect(self.__class__).relationships:
            rel_name = relation.key
            d[rel_name] = getattr(self, rel_name)

        return d


class Section(JsonBase):
    __tablename__ = 'sections'

    id = Column(Integer, primary_key=True)
    subject = Column(String, nullable=False)
    lection = Column(Text)
    order = Column(Integer, nullable=False)
    summary = Column(String, nullable=True)
    questions = relationship('Question')

    def __repr__(self):
        lect = (self.lection[:22] + '...'
                if len(self.lection) > 25
                else self.lection)

        return u'<Section(id={}, subject={}, lection={})>'.format(
            self.id, self.subject, lect
        )


class Question(JsonBase):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    section_id = Column(Integer, ForeignKey('sections.id'))
    answers = relationship('Answer')

    def __repr__(self):
        return u'<Question(id={}, question={}, section_id={})>'.format(
            self.id, self.question, self.section_id
        )


class Answer(JsonBase):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    text = Column(String, nullable=False)
    correct = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return u'<Answer(id={}, question_id={}, text={}, correct={})>'.format(
            self.id, self.question_id, self.text, self.correct
        )


class UserAnswer(JsonBase):
    __tablename__ = 'user_answers'

    id = Column(Integer, primary_key=True)
    answer_id = Column(Integer, ForeignKey('answers.id'))
    user_id = Column(Integer, ForeignKey('users.id'))


class User(JsonBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
