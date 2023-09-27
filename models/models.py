from tortoise import Model,fields
from pydantic import BaseModel
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    id = fields.IntField(pk=True,index=True)
    username= fields.CharField(max_length=30,null=False,unique=True)
    email = fields.CharField(max_length=200,null=False,unique=True)
    password=fields.CharField(max_length=100,null=False)
    is_verified = fields.BooleanField(default=False)
    join_date= fields.DatetimeField(default=datetime.utcnow)

class Business(Model):
    id = fields.IntField(pk=True,index=True)
    businessname= fields.CharField(max_length=30,null=False,unique=True)
    city = fields.CharField(max_length=50,null=False,default="Unknown")
    region = fields.CharField(max_length=50,null=False,default="Unknown")
    logo= fields.CharField(max_length=200,null=False,default="default.jpg")
    owner = fields.ForeignKeyField("models.User",related_name="business")

class Category(Model):
    id = fields.IntField(pk=True,index=True)
    name= fields.CharField(max_length=30,null=False,unique=True)
    business = fields.ForeignKeyField("models.Business",related_name="categories")
    category_image=fields.CharField(max_length=200,null=False,default="categoryDefault.jpg")


class Product(Model):
    id = fields.IntField(pk=True,index=True)
    name= fields.CharField(max_length=30,null=False,unique=True)
    desc= fields.CharField(max_length=200)
    category= fields.ForeignKeyField("models.Category",related_name="products")
    original_price=fields.DecimalField(max_digits=12,decimal_places=2)
    new_price=fields.DecimalField(max_digits=12,decimal_places=2)
    percentage_discount=fields.IntField()
    product_image=fields.CharField(max_length=200,null=False,default="productDefault.jpg")
    business = fields.ForeignKeyField("models.Business",related_name="products")



user_pydantic = pydantic_model_creator(User,name="User",exclude=("is_verified", ))
user_pydanticIn = pydantic_model_creator(User,name="UserIn",exclude_readonly=True,exclude=("is_verified","join_date" ))
user_pydanticOut = pydantic_model_creator(User,name="UserOut",exclude=("is_verified", ))

business_pydantic = pydantic_model_creator(Business,name="Business")
business_pydanticIn = pydantic_model_creator(Business,name="BusinessIn",exclude_readonly=True)

product_pydantic = pydantic_model_creator(Product,name="Product")
product_pydanticIn = pydantic_model_creator(Product,name="ProductIn",exclude=("percentage_discount","id" ))

category_pydantic = pydantic_model_creator(Category,name="Category")
category_pydanticIn = pydantic_model_creator(Category,name="CategoryIn",exclude_readonly=True)