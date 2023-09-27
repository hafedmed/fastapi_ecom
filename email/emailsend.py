from typing import List

from fastapi import BackgroundTasks, UploadFile,File,Form,Depends,HTTPException,status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from dotenv import dotenv_values
from models.models import User
import jwt
config_credentiel = dotenv_values(".env")


class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME =config_credentiel["EMAIL"],
    MAIL_PASSWORD = config_credentiel["PASS"],
    MAIL_FROM = config_credentiel["EMAIL"],
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL = False,
    USE_CREDENTIALS = True
)

async def send_mail(email: EmailSchema,instance:User):
    token_data = { 
        "id":instance.id,
        "username":instance.username
    }
    token = jwt.encode(token_data,config_credentiel["SECRET"],algorithm='HS256')