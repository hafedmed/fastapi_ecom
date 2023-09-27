from passlib.context import CryptContext
from fastapi.exceptions import HTTPException
from fastapi import status
import jwt
from dotenv import dotenv_values
from models.models import User

config_credentiel = dotenv_values(".env")
pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

def get_hashed_passord(password):
    return pwd_context.hash(password)


async def very_token(token:str):
    try:
        payload= jwt.decode(token,config_credentiel["SECRET"],algorithm='HS256')
        user = await User.get(id=payload.get("id"))
    except:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token ",
            headers={"WWW-AUTHENTICATE":"Bearer"}
        )
    return user

async def verify_password(palin_pasword,hashed_password):
    return pwd_context.verify(palin_pasword,hashed_password)

async def authenticate_user(username:str,password:str):
    user = await User.get(username=username)
    if user and await verify_password(password,user.password):
        return user
    return False

async def token_generator(username:str,password:str):
    user = await authenticate_user(username,password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid UserName or Password ",
            headers={"WWW-AUTHENTICATE":"Bearer"}            
        )
    token_data = {
        "id":user.id,
        "username":user.username
    }
    token = jwt.encode(token_data,config_credentiel["SECRET"])
    return token