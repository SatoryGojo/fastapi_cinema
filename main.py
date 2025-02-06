from typing import Annotated
import secrets
from sqlalchemy import select
from models import FilmModel, engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from users import user_router




app = FastAPI()
app.include_router(user_router)

class FilmScheme(BaseModel):
    name: str


async_session = async_sessionmaker(engine, expire_on_commit=False)

async def db_connect():
    async with  async_session() as db:
        yield db


SessionDept = Annotated[AsyncSession, Depends(db_connect)]

@app.post('/films/add_new')
async def add_new(film: FilmScheme, session: SessionDept):
    
    session.add(FilmModel(
        name = film.name  
    ))

    await session.commit()
    return {"name": film.name}


@app.get('/films')
async def all_films(session: SessionDept):

    query = select(FilmModel) 
    films = await session.execute(query)

    return {"films": films.scalars().all()}


if __name__ == '__main__':

    uvicorn.run('main:app', 
                host="127.0.0.1", 
                port=80, 
                reload=True)
    

