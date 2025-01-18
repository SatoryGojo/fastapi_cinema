from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


engine = create_async_engine('sqlite+aiosqlite:///training_db.db')



class AbstractBase(DeclarativeBase):

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 


class FilmModel(AbstractBase):

    __tablename__ = 'films'

    name:  Mapped[str] = mapped_column(nullable=True)





