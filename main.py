from fastapi import FastAPI,Depends
from tortoise import models
from tortoise.contrib.fastapi import register_tortoise
from models.models import *

#Authentication
from authentications.authentication import *
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
#Signal 
from tortoise.signals import post_save
from typing import List,Optional,Type
from tortoise import BaseDBAsyncClient

# Upload Images
from fastapi import File,UploadFile
import secrets
from fastapi.staticfiles import StaticFiles
from PIL import Image


app=FastAPI()

oath2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# static file config
app.mount("/static",StaticFiles(directory="static"),name="static")

@app.post('/token')
async def generate_token(request_form: OAuth2PasswordRequestForm=Depends()):
    token = await token_generator(request_form.username,request_form.password)
    return {"access_token":token,"token_type":"bearer"}

async def get_current_user(token: str = Depends(oath2_scheme)):
    print("hafed")
    payload = jwt.decode(token,config_credentiel["SECRET"],algorithms=['HS256'])
    print(payload.get("id"),"med")
    try:
        print(config_credentiel["SECRET"])
        payload = jwt.decode(token,config_credentiel["SECRET"],algorithms=['HS256'])
        print(payload)
        user = await User.get(id=payload.get("id"))
    except:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Invalid userN or password ",
            headers={"WWW-AUTHENTICATE":"Bearer"}
        )
    return await user

@app.post('/user/login')
async def user_login(user:user_pydanticIn = Depends(get_current_user)):
    business = await Business.get(owner = user.id)
    logo = business.logo
    logo_path = "/static/images/profiles"+logo
    return {
        "status":"OK",
        "data":{
            "username":user.username,
            "email":user.email,
            "logo":logo_path,
            "is_verified":user.is_verified,
            "join_date":user.join_date.strftime("%b %d %Y")
        }
    }


@app.get("/")
def index():
    return "Hello Automate"

@app.post("/upload/profile")
async def create_profil_image(file:UploadFile=File(...),user:user_pydantic=Depends(get_current_user)):
    FILEPATH = "./static/images/profiles/"
    filename = file.filename
    extention = filename.split(".")[1]

    if extention not in ["png","jpg"]:
        return { "status":"erro","detail":"File extention not allowed ex: png,jpg"}
    token_name = secrets.token_hex(10)+"."+extention
    generated_filename = FILEPATH +token_name
    file_content= await file.read()
    with open(generated_filename,'wb') as file:
        file.write(file_content)

    #Pillow 
    img = Image.open(generated_filename)
    img = img.resize(size=(200,200))
    img.save(generated_filename)

    file.close

    business = await Business.get(owner = user)
    owner = await business.owner
    if owner == user:
        business.logo = token_name
        await business.save()
    else:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Not Allowed to perform this action",
            headers={"WWW-AUTHENTICATE":"Bearer"}
        )
    return { "status":"OK","detail":"File has been uploaded"}


@app.post("/upload/product/{id}")
async def create_product_image(id:int,file:UploadFile=File(...),user:user_pydantic=Depends(get_current_user)):
    FILEPATH = "./static/images/products/"
    filename = file.filename
    extention = filename.split(".")[1]

    if extention not in ["png","jpg"]:
        return { "status":"erro","detail":"File extention not allowed ex : png,jpg"}
    token_name = secrets.token_hex(10)+"."+extention
    generated_filename = FILEPATH +token_name
    file_content= await file.read()
    with open(generated_filename,'wb') as file:
        file.write(file_content)

    #Pillow 
    img = Image.open(generated_filename)
    img = img.resize(size=(200,200))
    img.save(generated_filename)

    file.close

    product = await Product.get(id = id)
    business = await product.business
    owner = await business.owner
    if owner == user:
        product.product_image = token_name
        await product.save()
    else:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Not Allowed to perform this action",
            headers={"WWW-AUTHENTICATE":"Bearer"}
        )
    return { "status":"OK","detail":"File has been uploaded"}



@post_save(User)
async def create_business(
    sender:"Type[User]",
    instance:User,
    created:bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields:List[str]
) -> None:
    if created:
        business_obj= await Business.create(
            businessname = instance.username,owner= instance   
        )
        await business_pydantic.from_tortoise_orm(business_obj)

@app.post("/users/")
async def create_user(user: user_pydanticIn):
    user_info=user.dict(exclude_unset=True)
    user_info["password"]=get_hashed_passord(user_info["password"])
    user_info["is_verified"]=True
    user_obj= await User.create(**user_info)
    new_user= await user_pydantic.from_tortoise_orm(user_obj)
    return {
        "status" :"OK",
        "data":f"Hello {new_user.username}"

    }
#CRUD Category

@app.post("/upload/category/{id}")
async def create_category_image(id:int,file:UploadFile=File(...),user:user_pydantic=Depends(get_current_user)):
    FILEPATH = "./static/images/categories/"
    filename = file.filename
    extention = filename.split(".")[1]

    if extention not in ["png","jpg"]:
        return { "status":"erro","detail":"File extention not allowed ex : png,jpg"}
    token_name = secrets.token_hex(10)+"."+extention
    generated_filename = FILEPATH +token_name
    file_content= await file.read()
    with open(generated_filename,'wb') as file:
        file.write(file_content)

    #Pillow 
    img = Image.open(generated_filename)
    img = img.resize(size=(200,200))
    img.save(generated_filename)

    file.close

    category = await Category.get(id = id)
    business = await category.business
    owner = await business.owner
    if owner == user:
        category.category_image = token_name
        await category.save()
    else:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Not Allowed to perform this action",
            headers={"WWW-AUTHENTICATE":"Bearer"}
        )
    return { "status":"OK","detail":"File has been uploaded"}

@app.get("/categories")
async def get_all_categories():
    response = await category_pydantic.from_queryset(Category.all())
    #response = await Product.all()
    return {"status":"ok","data":response}

@app.get("/categories/{id}")
async def get_category(id:int):
    category = await Category.get(id=id)
    business = await category.business
    owner = await business.owner
    response = await category_pydantic.from_queryset_single(Category.get(id=id))
    return {
        "status":"ok",
        "data":{
            "category_details":response,
            "business_detail":{
                "name":business.businessname,
                "city":business.city,
                "region":business.region,
                "logo":business.logo,
                "owner_id":owner.id,
                "email":owner.email,
                "join_date":owner.join_date.strftime("%b %d %Y")
            }
        }
    }

@app.post("/categories/")
async def create_new_category(category:category_pydanticIn,user:user_pydantic=Depends(get_current_user)):
    category=category.dict(exclude_unset=True)
    business_ob = await Business.get(owner = user)
    owner = await business_ob.owner
    business_ob = await Business.get(owner = user)

    if user == owner:
        category_obj = await Category.create(**category,business=business_ob)
        category_obj = await category_pydantic.from_tortoise_orm(category_obj)
    else:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Not Allowed to perform this action",
            headers={"WWW-AUTHENTICATE":"Bearer"}
        )
    return { "status":"OK","detail":"Category created{ category_obj }"}
@app.delete("/categories/{id}")
async def delete_product(id:int,user:user_pydantic=Depends(get_current_user)):
    category = await Category.get(id=id)
    business = await category.business
    owner = await business.owner
    if user == owner:
        await category.delete() 
    else:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Not Allowed to perform this action",
            headers={"WWW-AUTHENTICATE":"Bearer"}
        )
    return { "status":"OK","detail":"Category and Products related has been Deleted "}   
#CRUD Product 
@app.get("/products")
async def get_all_product():
    response = await product_pydantic.from_queryset(Product.all())
    #response = await Product.all()
    return {"status":"ok","data":response}

@app.get("/products/{id}")
async def get_product(id:int):
    product = await Product.get(id=id)
    business = await product.business
    category = await product.category
    owner = await business.owner
    response = await product_pydantic.from_queryset_single(Product.get(id=id))
    return {
        "status":"ok",
        "data":{
            "product_details":response,
            "category":category.name,
            "business_detail":{
                "name":business.businessname,
                "city":business.city,
                "region":business.region,
                "logo":business.logo,
                "owner_id":owner.id,
                "email":owner.email,
                "join_date":owner.join_date.strftime("%b %d %Y")
            }
            }
    }

@app.delete("/products/{id}")
async def delete_product(id:int,user:user_pydantic=Depends(get_current_user)):
    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner
    if user == owner:
        await product.delete() 
    else:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Not Allowed to perform this action",
            headers={"WWW-AUTHENTICATE":"Bearer"}
        )
    return { "status":"OK","detail":"Product Deleted "}



@app.post("/products/")
async def create_new_product(product:product_pydanticIn,category:int,user:user_pydantic=Depends(get_current_user)):
    product=product.dict(exclude_unset=True)
    category_obj = await Category.get(id=category)
    #print(category_obj.name)
    # Avoid DIV 0   
    if product["original_price"] > 0:
        product["percentage_discount"]=(( product["original_price"] -  product["new_price"])/product["original_price"]) * 100
        business_ob = await Business.get(owner = user)
        product_obj = await Product.create(**product,business=business_ob,category=category_obj)
        product_obj = await product_pydantic.from_tortoise_orm(product_obj)
        return {"status" :"OK","data":product_obj}
    else:
        return {"status" :"Error"}

@app.put("/products/{id}")
async def update_product(id:int,update_info:product_pydanticIn,user:user_pydantic=Depends(get_current_user)):
    product = await  Product.get(id=id)
    business = await product.business
    category = await product.category
    owner = await business.owner
    update_info = update_info.dict(exclude_unset=True)
    # Avoid DIV 0   
    if user == owner and update_info["original_price"] != 0:
        await product.update_from_dict(update_info)
        await product.save()
        response = await product_pydantic.from_tortoise_orm(product)
        return { "status":"Ok","data":"Product has been updated"}
    else:
        return {"status" :"Error"}
# CRUD Business
@app.get("/business")
async def get_all_business():
    response = await business_pydantic.from_queryset(Business.all())
    #response = await Product.all()
    return {"status":"ok","data":response}
@app.get("/business/{id}")
async def get_business(id:int):
    business = await Business.get(id=id)
    owner = await business.owner
    response = await business_pydantic.from_queryset_single(Business.get(id=id))
    return {
        "status":"ok",
        "data":{
                "name":business.businessname,
                "city":business.city,
                "region":business.region,
                "logo":business.logo,
                "owner_id":owner.id,
                "email":owner.email,
                "join_date":owner.join_date.strftime("%b %d %Y")
            }
    }

@app.put("/business/{id}")
async def update_business(id:int,update_info:business_pydanticIn,user:user_pydantic=Depends(get_current_user)):
    business = await Business.get(id=id)
    owner = await business.owner
    update_info = update_info.dict()
    # Avoid DIV 0   
    if user == owner:
        await business.update_from_dict(update_info)
        await business.save()
        response = await business_pydanticIn.from_tortoise_orm(business)
        return { "status":"Ok","data":"Business has been updated"}
    else:
        return {"status" :"Error"}
register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={'models': ['models.models']} ,
    generate_schemas=True,
    add_exception_handlers=True
)