import os
import sys
from sqlalchemy import Column,ForeignKey,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base= declarative_base()
class Food(Base):
    __tablename__='food'
    id=Column(Integer,primary_key=True)
    name=Column(String(20),nullable=False)
    description=Column(String(300),nullable=False)
    image=Column(String(250),nullable=False)
    categories=Column(String(20),nullable=False)
    place=Column(String(20))
    price=Column(Integer)
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.image,
            'categories': self.categories
        }

class User(Base):
    __tablename__='User'
    id=Column(Integer,primary_key=True)
    name=Column(String(20),nullable=False)
    email=Column(String(20),nullable=False)
    picture=Column(String(200))
    user_id=Column(Integer,ForeignKey(Food.id))
    user=relationship(Food)


engine= create_engine('postgresql://kunal:kunal121@localhost/food')
Base.metadata.create_all(engine)
