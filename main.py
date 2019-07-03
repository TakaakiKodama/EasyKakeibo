# -*- coding: utf-8 -*-

from flask import Flask, session, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_bcrypt import Bcrypt
from datetime import datetime
from hashids import Hashids
import random
import os

app = Flask(__name__)
app.secret_key = 'sAec%mSWcFpt-6zwBHMPXZMLnx7t8fNeD4Kn/DZT' #ソルト
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://127.0.0.1:5432/app'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# def app_init():
# 	db.drop_all()
# 	db.create_all()
# 	you=User()
# 	you.email="2@2"
# 	you.password=bcrypt.generate_password_hash("password"+app.secret_key).decode('utf-8')
# 	db.session.add(you)
# 	db.session.commit()

def generate_random_color():
    return '#{:X}{:X}{:X}'.format(*[random.randint(0, 255) for _ in range(3)])

class User(db.Model):
	__tablename__ = "User"
	email = db.Column(db.String(), unique=True, nullable=False, primary_key=True)
	password = db.Column(db.String(200), nullable=False)

class BookMap(db.Model):
	__tablename__ = "BookMap"
	id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
	book_id = db.Column(db.String(), nullable=False)
	book_name = db.Column(db.String(),nullable=False)
	email = db.Column(db.String(), nullable=False)
	permission = db.Column(db.Integer, nullable=False)

class BookRecode(db.Model):
	__tablename__ = "BookRecode"
	registory_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
	book_id = db.Column(db.String(), nullable=False)
	date = db.Column(db.DateTime, nullable=False)
	category_id = db.Column(db.Integer, nullable=False)
	recode_name = db.Column(db.String(), nullable=False)
	price = db.Column(db.Integer, nullable=False)

class CategoryList(db.Model):
	__tablename__ = "CategoryList"
	id = db.Column(db.Integer, nullable=False, primary_key=True)
	book_id = db.Column(db.String(), nullable=False)
	category_name = db.Column(db.String(), nullable=False)

class Permission(db.Model):
	__tablename__ = "Permission"
	id = db.Column(db.Integer, nullable=False, primary_key=True)
	role = db.Column(db.String(),nullable=False)


@app.route('/')
def index():
	name="nanashi"
	if 'username' in session:
		name=str(session['username'])
	return render_template('index.html', title='flask test', name=name)

@app.route('/login', methods=['GET', 'POST'])
def login():
	is_login=False
	if 'email' in session: #ログインしてるかどうか
		is_login=True
		email=str(session['email'])
		return redirect('mypage')
	if request.method == 'POST':
		you = User.query.filter_by(email=request.form['email']).first()
		email=you.email
		password=you.password
		if bcrypt.check_password_hash(password, request.form['password']+app.secret_key):
			session['email'] = email
			return redirect('/mypage')
		else:
			render_template('login.html')
	return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('email', None)
	return render_template('logout.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
	email=""
	password=""
	if request.method == 'POST':
		email = request.form['email']
		password = bcrypt.generate_password_hash(request.form['password']+app.secret_key).decode('utf-8')
		session['email'] = email
		you=User()
		you.email=email
		you.password=password
		db.session.add(you)
		db.session.commit()

	return render_template('registration.html', email=email, password=password)

@app.route('/mypage', methods=['GET', 'POST'])
def mypage():
	is_login=False
	if 'email' in session:
		is_login=True
		edited=""
		time=int(datetime.now().strftime('%s'))
		email=str(session['email'])
		if request.method == 'POST' and request.form['bookname']!="":
			makebook=BookMap()
			makebook.book_name = request.form['bookname']
			makebook.email =  session['email']
			makebook.permission = 1
			hashids = Hashids(salt=makebook.email+makebook.book_name, min_length=20)
			makebook.book_id = hashids.encode(int(datetime.now().strftime('%s')))
			db.session.add(makebook)
			db.session.commit()
			init_categoryname=["その他","食費","外食費","日用品","交通費","衣服","交際費","趣味","雑費"]
			for name in init_categoryname:
				initialize_category=CategoryList()
				initialize_category.book_id=makebook.book_id
				initialize_category.category_name=name
				db.session.add(initialize_category)
				db.session.commit()
			book_id = makebook.book_id
			return redirect('/book/'+book_id)
		booklist=BookMap.query.filter_by(email=email).all()
		return render_template('mypage.html', email=email, time=time, booklist=booklist)
	else:
		return redirect('/login')

@app.route('/book/<book_id>', methods=['GET', 'POST'])
def editBook(book_id):
	is_login=False
	if 'email' in session:
		is_login=True
		email=str(session['email'])
		permission=BookMap.query.filter_by(book_id=book_id, email=email).first().permission
		bydate=[]
		forchart=[]
		res={}
		colors=[]
		chart_type=""
		span=""
		if permission == 1 :
			if request.method == 'POST':
				try: #add_recode
					request.form['add']
					category=CategoryList.query.filter_by(book_id=book_id,category_name=request.form['category']).first()
					if category == None:
						category=CategoryList()
						category.book_id = book_id
						category.category_name = request.form['category']
						db.session.add(category)
						db.session.commit()
						category=CategoryList.query.filter_by(book_id=book_id,category_name=request.form['category']).first()
					recode=BookRecode()
					recode.book_id = request.form['book_id']
					recode.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
					recode.category_id = category.id
					recode.recode_name = request.form['recode_name']
					recode.price = request.form['price']
					db.session.add(recode)
					db.session.commit()
				except:
					pass
				try: #change_recode
					request.form['change']
					category=CategoryList.query.filter_by(book_id=book_id,category_name=request.form['category']).first()
					if category == None:
						category=CategoryList()
						category.book_id = book_id
						category.category_name = request.form['category']
						db.session.add(category)
						db.session.commit()
						category=CategoryList.query.filter_by(book_id=book_id,category_name=request.form['category']).first()
					change=BookRecode.query.get(request.form['registory_id'])
					change.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
					change.category_id = category.id
					change.recode_name = request.form['recode_name']
					change.price = request.form['price']
					# db.session.add(change)
					db.session.commit()
				except:
					pass
				try: #delete_recode
					request.form['delete']
					action='delete'
					delete=BookRecode.query.get(request.form['registory_id'])
					db.session.delete(delete)
					db.session.commit()
				except:
					pass
				try: #get_recode_by_date_foredit
					request.form['get_recode_by_date_foredit']
					bydate=BookRecode.query.filter(BookRecode.date==datetime.strptime(request.form['date'], '%Y-%m-%d')).all()
				except:
					pass
				try:
					request.form['get_recode_by_date_fordaily']
					chart_type="pie"
					forchart=BookRecode.query.filter(BookRecode.date==datetime.strptime(request.form['date'], '%Y-%m-%d')).all()
					res={}
					for data in forchart:
						c_name=CategoryList.query.filter_by(book_id=book_id,id=data.category_id).first().category_name
						if c_name in res:
							res[c_name]=res[c_name]+data.price
						else:
							res[c_name]=data.price
					colors=[]
					for i in range(len(res)):
						colors.append(generate_random_color())
					span=datetime.strptime(request.form['date'], '%Y-%m-%d').strftime('%Y/%m/%d')+"の支出"
				except:
					pass
				try:
					request.form['get_recode_by_date_forspan']
					chart_type="pie"
					forchart=BookRecode.query.filter(and_(BookRecode.date>=datetime.strptime(request.form['datefrom'], '%Y-%m-%d'), BookRecode.date<=datetime.strptime(request.form['dateto'], '%Y-%m-%d'))).all()
					for data in forchart:
						c_name=CategoryList.query.filter_by(book_id=book_id,id=data.category_id).first().category_name
						if c_name in res:
							res[c_name]=res[c_name]+data.price
						else:
							res[c_name]=data.price
					colors=[]
					for i in range(len(res)):
						colors.append(generate_random_color())
					span=datetime.strptime(request.form['datefrom'], '%Y-%m-%d').strftime('%Y/%m/%d')+"〜"+datetime.strptime(request.form['dateto'], '%Y-%m-%d').strftime('%Y/%m/%d')+"の支出"
				except:
					pass
				try: #change_category
					request.form['change_category']
					change_c=CategoryList.query.filter_by(book_id=book_id, id=request.form['category_id']).first()
					change_c.category_name=request.form['category_name']
					db.session.commit()
				except:
					pass
				try: #delete_category
					request.form['delete_category']
					delete_c=CategoryList.query.filter_by(book_id=book_id, id=request.form['category_id']).first()
					delete_id=delete_c.id
					db.session.delete(delete_c)

					other=CategoryList.query.filter_by(book_id=book_id, category_name="その他").first().id
					for recode in BookRecode.query.filter_by(category_id=delete_id).all():
						recode.category_id=other
					db.session.commit()
				except:
					pass
				try: #delete_thisbook
					request.form['delete_thisbook']
					delete=BookRecode.query.filter_by(book_id=book_id).all()
					for i in delete:
						db.session.delete(i)
					delete=BookMap.query.filter_by(book_id=book_id).all()
					for i in delete:
						db.session.delete(i)
					db.session.commit()
					return redirect('/mypage')
				except:
					pass
				try: #add_permission
					request.form['add_permission']
					add_permission=BookMap()
					add_permission.book_id = book_id
					add_permission.book_name = BookMap.query.filter_by(book_id=book_id).first().book_name
					add_permission.email = request.form['add_person']
					add_permission.permission = request.form['permission_level']
					db.session.add(add_permission)
					db.session.commit()
				except:
					pass
				try: #change_permission
					request.form['change_permission']
					change_permission=BookMap.query.filter_by(book_id=book_id,email=request.form['change_person']).first()
					change_permission.permission = request.form['permission_level']
					# db.session.add(add_permission)
					db.session.commit()
				except:
					pass

			history=BookRecode.query.filter_by(book_id=book_id).all()
			permited_users=[person.email for person in BookMap.query.filter_by(book_id=book_id).all()]
			categories=CategoryList.query.filter_by(book_id=book_id).all()
			for i in range(len(history)):
				history[i].date=history[i].date.strftime('%Y-%m-%d')
				history[i].category_name=CategoryList.query.filter_by(book_id=book_id, id=history[i].category_id).first().category_name
			return render_template('book.html', email=email, book_id=book_id, history=history, permited_users=permited_users, categories=categories, bydate=bydate,forchart=forchart, res=res,colors=colors,span=span,chart_type=chart_type)
		return redirect('/mypage')
	else:
		return redirect('/login')
if __name__ == "__main__":
	app.run(debug=True)
