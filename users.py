from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from models import db_connect, UserModel, async_session
from sqlalchemy import select


context = CryptContext(schemes=['bcrypt'], deprecated="auto")
router = APIRouter()
SessionDept = Annotated[AsyncSession, Depends(db_connect)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token') 

SECRET_KEY = '2nXGNMkA_wye3VgbduZtd1YvttLXUrOF4p-qYxQr4lY='
ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME_MINUTES = 10 
REFRESH_TOKEN_FIFETIME_DAYS = 7

    
class User(BaseModel):
    username: str
    password: str


def hash_password(password: str):
    return context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return context.verify(password, hashed_password)



async def check_user(username: str, db: SessionDept):
        query = select(UserModel).where(UserModel.username==username)
        user = await db.execute(query)
        return user.scalar_one_or_none()


async def registration(user: User, db: SessionDept):

    user_object = await check_user(username=user.username, db=db)

    if user_object:
        return None
    
    try:   
        hashed_password = hash_password(user.password)
        db.add(UserModel(
            username=user.username,
            hashed_password=hashed_password
        ))
        await db.commit()
    except:
        return None

    return True


async def authenticate(username: str, password: str, db: SessionDept):

    user_object = await check_user(username=username, db=db)

    if user_object is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")


    to_verify_password = user_object.hashed_password
    print(to_verify_password)
    if not verify_password(password, to_verify_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return user_object
    


def create_token(payload: dict):
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return token


async def decode_token(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDept):
        credentials_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)
                                                    
        
        try:
            payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
            username = payload.get('sub')
            if username is None:
                raise credentials_exceptions
            
            user_object = await check_user(username=username, db=db)

            if user_object is None:
                raise credentials_exceptions
            
        except JWTError:    
            raise credentials_exceptions

        return user_object.username


@router.post('/registration')
async def register(user: User, db: SessionDept):

    registration_object = await registration(user=user, db=db)

    if registration_object is None:
        return {'Message': 'Invalid data'}

    return {'Message': 'You have been registered successfully'}

@router.post('/login')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDept):

   
    user_object = await authenticate(username=form_data.username, password=form_data.password, db=db)

    if user_object is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")


    to_verify_password = user_object.hashed_password
    print(to_verify_password)
    if not verify_password(form_data.password, to_verify_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    

    access_lifetime = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES) 
    payload = {'sub': form_data.username, 'exp':access_lifetime, 'type': 'access'}

    access_token = create_token(payload)

    refresh_lifetime = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_FIFETIME_DAYS) 
    payload = {'sub': form_data.username, 'exp':refresh_lifetime, 'type': 'refresh'}

    refresh_token = create_token(payload)


    return {"tokens":{
        "access_token": access_token,
        "refresh_token": refresh_token,
    }}


@router.post('/refresh')
async def refresh(refresh_token: str, db: SessionDept):

    refresh_except = HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Invalid refresh token"
        )
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, ALGORITHM)
        username = payload.get('sub')
        type_token = payload.get('type')

        if username is None or type_token != 'refresh':
            raise refresh_except
        
        user_object = await check_user(username=username, db=db)

        if user_object is None :
            raise refresh_except
        

    except JWTError:
        raise refresh_except
    
    new_access_lifetime = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
    new_payload = {'sub': username, 'exp': new_access_lifetime, 'type': 'access'}

    new_access_token = create_token(payload=new_payload)

    return {"tokens":{
        "access_token": new_access_token,
        "refresh_token": refresh_token,
    }}


@router.get('/users/me')
def my_page(me: Annotated[str, Depends(decode_token)]):
    return me
 










