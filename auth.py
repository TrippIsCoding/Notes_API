from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import jwt, JWTError, ExpiredSignatureError
from config import SECRET_KEY, ALGORITHM
from models import User, UserCreate
from database import get_db

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

def verify_token(token: str):
    try:
        decode = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return decode
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired')
    except JWTError:
        raise HTTPException(status_code=401, detail='Unauthorzed')

auth_router = APIRouter()

@auth_router.post('/CreateAccount')
async def user_create(user: UserCreate, db: Session = Depends(get_db)):   
    try:
        new_user = User(
            username=user.username,
            hashed_password=hash_password(user.password),
            email=user.email,
            full_name=user.full_name
        )
    
        db.add(new_user)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail='Username or Email already being used')
    return {'User': user}

@auth_router.post('/token')
async def authorize_user(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if not db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=401, detail='Incorrect Username')
    if not verify_password(user.password, db.query(User).filter(User.username == user.username).first().hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect Password')
    payload = {'sub': user.username, 'exp': datetime.now(timezone.utc) + timedelta(minutes=30)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {'token': token}

@auth_router.get('/ShowUsers')
async def list_users(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token)
    users = db.query(User).order_by(User.id).all()
    return {'Users': users}