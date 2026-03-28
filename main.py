from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, AfterValidator, Field, EmailStr, ConfigDict
from typing import Annotated 
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session


#Database definition and Parent class declaration
database_url = "sqlite:////home/nissi/Desktop/Python_Project/user.db"
engine = create_engine(database_url, echo=True)
Base = declarative_base()


##ORM Models
class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)    
    age = Column(Integer)
    

Base.metadata.create_all(engine)

def create_user(name:str, email:str, age:int):
    with Session(engine) as session:
        user = UserORM(name=name, email=email, age=age)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_user_by_name(name:str):
    with Session(engine) as session:
        user = session.query(UserORM).filter(UserORM.name == name).first()
        if user is not None:
            return user
        else:
            raise HTTPException(status_code=404, detail="User not Found")

def get_users(min_age:int, offset:int, limit:int=None):
    with Session(engine) as session:
        query = session.query(UserORM)
        if min_age is not None:
            query = query.filter(UserORM.age >= min_age)
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        users = query.all()
        return users
        

def update_user(name:str, email:str =None, age:int=None):
    with Session(engine) as session:
        user = session.query(UserORM).filter(UserORM.name == name).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not Found")

        if email is not None:
            user.email = email
        if age is not None:
            user.age = age

        session.add(user)
        session.commit()
        session.refresh(user)
        return {
            "message": f"{user.name} updated successfully"
        }

def delete_user(name:str):
    with Session(engine) as session:
        user = session.query(UserORM).filter(UserORM.name == name).first()
        if user is not None:
            session.delete(user)
            session.commit()
            return {
                "message": f"{name} deleted from database"
            }
        else:
            raise HTTPException(status_code=404, detail="User not Found")



#FASTAPI

app = FastAPI()
class User(BaseModel): 
    name: str 
    email: EmailStr
    age: int = Field(default=20, ge=0, le=150) 
    
class UserOut(BaseModel): 
    name: str
    age: int 
    email: EmailStr

    class UserOut(BaseModel):
        model_config = ConfigDict(from_attributes=True)

    
@app.get("/") 
def home(): 
    return {"message": "Welcome to My First Back-end"} 
    
@app.get("/health") 
def health(): 
    return { "status" : "ok", "message" : "The service is running" } 
    
@app.get("/greet/{name}") 
def greet(name: str): 
    return {"message": f"Hello {name}, Welcome to the api"} 
    
@app.post("/user", response_model=UserOut, status_code = status.HTTP_201_CREATED) 
def api_create_user(user: User): 
    name = user.name
    email = user.email
    age = user.age
    return create_user(user.name, user.email, user.age)

@app.get("/users", response_model=list[UserOut]) 
def api_all_users(min_age:int=None, offset:int=None, limit:int=None): 
    return get_users(min_age, offset,limit )

@app.get('/user/{name}', response_model=UserOut)
def api_get_user_by_name(name:str):
    return get_user_by_name(name)

@app.put('/update/{name}')
def api_update(name:str, email:EmailStr= None, age:int= None):
    return update_user(name=name, email=email, age=age)


@app.delete('/delete/{name}')
def api_delete(name:str):
    return delete_user(name)
