# initializeDB.py

from datetime import datetime

from main import db
from main import User, BookMap, CategoryList, BookRecode, Permission
from main import bcrypt
from uuid import uuid4
from main import app

import random
init_categoryname=["その他","食費","外食費","日用品","交通費","衣服","交際費","趣味","雑費"]
init_recodes=[]
for i in range(1000):
    recode={}
    recode["cname"]=init_categoryname[random.randint(0, 8)]
    recode['date']="2019-"+str(random.randint(7,8))+"-"+str(random.randint(1, 30))
    recode['name']= "test_"+recode["cname"]
    recode['price']= random.randint(100, 20000)
    init_recodes.append(recode)

db.drop_all()
db.create_all()
users=["test1@test.com","test2@test.com","test3@test.com"]
for n_user in users:
    you=User()
    you.email=n_user
    you.password=bcrypt.generate_password_hash("password"+app.secret_key).decode('utf-8')
    db.session.add(you)
    db.session.commit()

shreid=str(uuid4())
makebook=BookMap()
makebook.book_name = "newbook"
makebook.email = "test1@test.com"
makebook.permission = 1
makebook.book_id = shreid
db.session.add(makebook)
db.session.commit()

makebook=BookMap()
makebook.book_name = "newbook"
makebook.email =  "test2@test.com"
makebook.permission = 2
makebook.book_id = shreid
db.session.add(makebook)
db.session.commit()

makebook=BookMap()
makebook.book_name = "newbook"
makebook.email = "test3@test.com"
makebook.permission = 3
makebook.book_id = shreid
db.session.add(makebook)
db.session.commit()

init_categoryname=["その他","食費","外食費","日用品","交通費","衣服","交際費","趣味","雑費"]
for name in init_categoryname:
	initialize_category=CategoryList()
	initialize_category.book_id=makebook.book_id
	initialize_category.category_name=name
	initialize_category.id=str(uuid4())
	db.session.add(initialize_category)
	db.session.commit()

for recode in init_recodes:
    category=CategoryList.query.filter_by(book_id=makebook.book_id,category_name=recode['cname']).first()
    add_recode=BookRecode()
    add_recode.book_id = makebook.book_id
    add_recode.registory_id = str(uuid4())
    add_recode.date = datetime.strptime(recode['date'], '%Y-%m-%d')
    add_recode.category_id = category.id
    add_recode.recode_name = recode['name']
    add_recode.price = recode['price']
    db.session.add(add_recode)
    db.session.commit()
