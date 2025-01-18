from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, create_engine


engine = create_engine('sqlite:///training_db.db')

class AbstractBase(DeclarativeBase):

    id = Column(Integer, primary_key=True, autoincrement=True)


class FilmModel(AbstractBase):

    __tablename__ = 'films'

    name = Column(String)





