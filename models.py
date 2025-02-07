from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine('sqlite+aiosqlite:///training_db.db')

async_session = async_sessionmaker(engine, expire_on_commit=False)



async def db_connect():
    async with async_session() as db:
        yield db




class AbstractBase(DeclarativeBase):

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 


class FilmModel(AbstractBase):

    __tablename__ = 'films'

    name:  Mapped[str] = mapped_column(nullable=True)



class UserModel(AbstractBase):

    __tablename__ = 'users'

    username: Mapped[str]
    hashed_password: Mapped[str]





