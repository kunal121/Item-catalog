from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Food,Base,User

engine=create_engine('postgresql://kunal:kunal121@localhost/food')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

#adding fake food database

food1=Food(name='Pizza Hub',description='hello',image='https://www.coldstonecreamery.com/assets/img/products/shakes/shakes.jpg',categories='Italian',place='Bikaner',price='70')
session.add(food1)
session.commit()

food2=Food(name='just Rolz',description='hello',image='https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcTqotF4BZp17X0_DKcCv3px0IDjHMN1P1hyualIcBJ_7dgEa5TbMA',categories='Drinks',place='Bikaner',price='50')
session.add(food2)
session.commit()

print ("food added successfully!")
