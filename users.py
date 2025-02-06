from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone


context = CryptContext(schemes=['bcrypt'])
user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token') 

SECRET_KEY = '2nXGNMkA_wye3VgbduZtd1YvttLXUrOF4p-qYxQr4lY='
ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME_MINUTES = 1 
REFRESH_TOKEN_FIFETIME_DAYS = 7

fake_db = {

}

class User(BaseModel):
    username: str
    password: str


class UserInDB(BaseModel):
    username: str
    hashed_password: str




def hash_password(password: str):
    return context.hash(password)

def verify_password(password: str, hashed_password: str):
    return context.verify(password, hashed_password)



def get_user(username: str):
    if username not in fake_db:
        return None
    
    user_object = fake_db[username]
    return UserInDB(**user_object)


def authenticate_user(username: str, password: str):
    user_object = get_user(username)

    if user_object is None:
        return None
    
    if not verify_password(password, user_object.hashed_password):
        return None
    
    return user_object



def create_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt



def get_user_token(token: Annotated[str, Depends(oauth2_scheme)]):
    
    credentials_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)

        username = payload.get('sub')


        username_object = get_user(username=username)
        if username is None:
            raise credentials_exceptions


    except JWTError:
        raise credentials_exceptions


    return  username_object



@user_router.post('/register')
def register(user: User):

    if get_user(user.username) is not None:
        return {'message': 'User already exists'}
    
    hashed_pass = hash_password(user.password)
    fake_db[user.username] = {
        "username": user.username,
        'hashed_password': hashed_pass
    }
    
    return {"message": "You have been registered successfully"}


@user_router.post('/token')
def login(login_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]):

    user = authenticate_user(username=login_data.username, password=login_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect login or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    access_token_lifetime = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
    data = {'sub': login_data.username, 'exp':access_token_lifetime, "type":"access_token"}
    access_token = create_token(data)


    refresh_token_lifetime = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_FIFETIME_DAYS)
    data = {'sub': login_data.username, 'exp':refresh_token_lifetime, "type":"refresh_token"}
    refresh_token = create_token(data)


    return {"tokens":{
        "access": access_token,
        "refresh": refresh_token
    }}



@user_router.post('/refresh')
def refresh_token(refresh_token: str):

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, ALGORITHM)
        username = payload.get('sub')
        type_token = payload.get('type')
        if username is None or type_token != 'refresh_token':
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        ) 



    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    access_token_lifetime = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)

    data = {'sub': username, 'exp': access_token_lifetime, 'type': 'access_token'}
    access_token = create_token(data)

    return {"tokens":{
        "access": access_token,
        "refresh": refresh_token
    }}



@user_router.get('/user/me')
def about_me(me: Annotated[str, Depends(get_user_token)]):
    return me

@user_router.get('/users/all')
def about_all():
    return {"base": fake_db}

    




