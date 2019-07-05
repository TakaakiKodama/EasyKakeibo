# -*- coding: utf-8 -*-

from flask import Flask, session, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from flask_bcrypt import Bcrypt
from datetime import datetime
from datetime import timedelta
from hashids import Hashids
import uuid
import random
import os

app = Flask(__name__)
app.secret_key = 'sAec%mSWcFpt-6zwBHMPXZMLnx7t8fNeD4Kn/DZT' #ソルト
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://127.0.0.1:5432/app'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
	__tablename__ = "User"
	email = db.Column(db.String(), unique=True, nullable=False, primary_key=True)
	password = db.Column(db.String(200), nullable=False)

class BookMap(db.Model):
	__tablename__ = "BookMap"
	id = db.Column(db.Integer, primary_key=True)
	book_id = db.Column(db.String(),nullable=False)
	book_name = db.Column(db.String(),nullable=False)
	email = db.Column(db.String(), nullable=False)
	permission = db.Column(db.Integer, nullable=False)

class BookRecode(db.Model):
	__tablename__ = "BookRecode"
	book_id = db.Column(db.String(),nullable=False)
	registory_id = db.Column(db.String(), primary_key=True, nullable=False)
	date = db.Column(db.DateTime, nullable=False)
	category_id = db.Column(db.String(), nullable=False)
	recode_name = db.Column(db.String(), nullable=False)
	price = db.Column(db.Integer, nullable=False)

class CategoryList(db.Model):
	__tablename__ = "CategoryList"
	id = db.Column(db.String(), primary_key=True, nullable=False)
	book_id = db.Column(db.String(), nullable=False)
	category_name = db.Column(db.String(), nullable=False)

class Permission(db.Model):
	__tablename__ = "Permission"
	id = db.Column(db.Integer, nullable=False, primary_key=True)
	role = db.Column(db.String(),nullable=False)

@app.route('/', methods=['GET', 'POST'])
def index():
	name="nanashi"
	if 'username' in session:
		name=str(session['username'])
	elif request.method == 'POST':
		if "registory" in request.form:
			email = request.form['email']
			password = bcrypt.generate_password_hash(request.form['password']+app.secret_key).decode('utf-8')
			session['email'] = email
			you=User()
			you.email=email
			you.password=password
			db.session.add(you)
			db.session.commit()
			return redirect('/mypage')
		elif "login" in request.form:
			you = User.query.filter_by(email=request.form['email']).first()
			email=you.email
			password=you.password
			if bcrypt.check_password_hash(password, request.form['password']+app.secret_key):
				session['email'] = email
				return redirect('/mypage')
			else:
				render_template('index.html' )
	return render_template('index.html', title='EasyKakeibo', page_title="EasyKakeibo" , name=name)


@app.route('/logout')
def logout():
	session.pop('email', None)
	return render_template('logout.html', title='Logout | EasyKakeibo', page_title="Logout")


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
			# hashids = Hashids(salt=makebook.email+makebook.book_name, min_length=20)
			makebook.book_id = str(uuid4())
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
			book_id = makebook.book_id
			return redirect('/book/'+str(book_id))
		booklist=BookMap.query.filter_by(email=email).all()
		return render_template('mypage.html', title='MyPage | EasyKakeibo', page_title="MyPage", email=email, time=time, booklist=booklist)
	else:
		return redirect('/login')

@app.route('/book/<book_id>', methods=['GET', 'POST'])
def editBook(book_id):
	is_login=False
	if 'email' in session:
		is_login=True
		email=str(session['email'])
		thisbook=BookMap.query.filter_by(book_id=book_id, email=email).first()
		permission=thisbook.permission
		bookname=thisbook.book_name
		bydate=[]
		forchart=[]
		res={}
		colors=[]
		chart_type=""
		span=""
		sumup=""
		if permission == None:
			return redirect('/mypage')
		elif request.method == 'POST':
			if permission <= 3 : #閲覧のみ

				if 'get_recode_by_date_fordaily' in request.form:
					chart_type, forchart, res, sumup, span=get_recode_by_date_fordaily(request,book_id,res,colors)
				elif 'get_recode_by_date_forspan' in request.form:
					chart_type, forchart, res, sumup, span=get_recode_by_date_forspan(request,book_id,res,colors)
			if permission <= 2 : #閲覧、追加変更
				if 'add' in request.form:
					add_recode(request,book_id)
				elif 'change' in request.form:
					change_recode(request,book_id)
				elif 'delete' in request.form:
					delete_recode(request)
				elif 'get_recode_by_date_foredit' in request.form:
					bydate=get_recode_by_date_foredit(request)
				elif 'change_category' in request.form:
					change_category(request,book_id)
				elif 'delete_category' in request.form:
					delete_category(request,book_id)
			if permission == 1 : #閲覧、追加変更、権限の追加変更、家計簿の削除
				if 'delete_thisbook' in request.form:
					delete_thisbook(request,book_id)
					return redirect('/mypage')
				elif 'change_bookname' in request.form:
					change_bookname(request,book_id)
				elif 'add_permission' in request.form:
					add_permission(request,book_id)
				elif 'change_permission' in request.form:
					change_permission(request,book_id)
		history=BookRecode.query.filter_by(book_id=book_id).order_by(BookRecode.price.desc()).all()
		permited_users=[person.email for person in BookMap.query.filter_by(book_id=book_id).all()]
		categories=CategoryList.query.filter_by(book_id=book_id).all()
		for i in range(len(history)):
			history[i].date=history[i].date.strftime('%Y-%m-%d')
			history[i].category_name=CategoryList.query.filter_by(book_id=book_id, id=history[i].category_id).first().category_name
		return render_template('book.html',
            title=bookname+' | EasyKakeibo',
            page_title=bookname,
			email=email,
			permission=permission,
			book_id=book_id,
			history=history,
			permited_users=permited_users,
			categories=categories,
			bydate=bydate,
			forchart=forchart,
			res=res,
			colors=colors,
			span=span,
			chart_type=chart_type,
			sumup=sumup)

	else:
		return redirect('/login')

def add_recode(request,book_id):
	# request.form['add']
	category=CategoryList.query.filter_by(book_id=book_id,category_name=request.form['category']).first()
	if category == None:
		category=CategoryList()
		category.book_id = book_id
		category.category_name = request.form['category']
		db.session.add(category)
		db.session.commit()
		category=CategoryList.query.filter_by(book_id=book_id,category_name=request.form['category']).first()
	recode=BookRecode()
	recode.registory_id = str(uuid4())
	recode.book_id = request.form['book_id']
	recode.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
	recode.category_id = category.id
	recode.recode_name = request.form['recode_name']
	recode.price = request.form['price']
	db.session.add(recode)
	db.session.commit()

def change_recode(request,book_id):
	# request.form['change']
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
	db.session.commit()

def delete_recode(request):
	delete=BookRecode.query.get(request.form['registory_id'])
	db.session.delete(delete)
	db.session.commit()

def get_recode_by_date_foredit(request):
	bydate=BookRecode.query.filter(BookRecode.date==datetime.strptime(request.form['date'], '%Y-%m-%d')).order_by(BookRecode.date,BookRecode.category_id,BookRecode.price).all()
	return bydate

def get_recode_by_date_fordaily(request,book_id,res,colors):
	chart_type="pie"
	forchart=BookRecode.query.filter(BookRecode.date==datetime.strptime(request.form['date'], '%Y-%m-%d')).order_by(BookRecode.date,BookRecode.category_id,BookRecode.price).all()
	for data in forchart:
		c_name=CategoryList.query.filter_by(book_id=book_id,id=data.category_id).first().category_name
		if c_name in res:
			res[c_name]=res[c_name]+data.price
		else:
			res[c_name]=data.price
	for i in range(len(res)):
		colors.append(generate_random_color())
	sumup=sum(res.values())
	span=datetime.strptime(request.form['date'], '%Y-%m-%d').strftime('%Y/%m/%d')+"の支出"
	return chart_type, forchart, res, sumup, span

def get_recode_by_date_forspan(request,book_id,res,colors):
	datefrom=datetime.strptime(request.form['datefrom'], '%Y-%m-%d')
	dateto=datetime.strptime(request.form['dateto'], '%Y-%m-%d')
	selected_category=request.form['selected_category']
	if selected_category == "all":
		chart_type="pie"
		forchart=BookRecode.query.filter(and_(BookRecode.date>=datefrom,BookRecode.date<=dateto)).order_by(BookRecode.date,BookRecode.category_id,BookRecode.price).all()
		for data in forchart:
			c_name=CategoryList.query.filter_by(book_id=book_id,id=data.category_id).first().category_name
			if c_name in res:
				res[c_name]=res[c_name]+data.price
			else:
				res[c_name]=data.price
		for i in range(len(res)):
			colors.append(generate_random_color())
		sumup=sum(res.values())
		span=datetime.strptime(request.form['datefrom'], '%Y-%m-%d').strftime('%Y/%m/%d')+"〜"+datetime.strptime(request.form['dateto'], '%Y-%m-%d').strftime('%Y/%m/%d')+"の支出"
	else:
		chart_type = "bar"
		selected_category_id=CategoryList.query.filter_by(book_id=book_id,category_name=request.form['selected_category']).first().id
		forchart=BookRecode.query.filter(and_(BookRecode.date>=datefrom,BookRecode.date<=dateto,BookRecode.category_id==selected_category_id)).order_by(BookRecode.date,BookRecode.category_id,BookRecode.price).all()
		for data in forchart:
			datelabel=data.date.strftime('%Y-%m-%d')
			if datelabel in res:
				res[datelabel]=res[datelabel]+data.price
			else:
				res[datelabel]=data.price
			timerange=[]
			for n in range((dateto-datefrom).days):
				timerange.append((datefrom + timedelta(n)).strftime('%Y-%m-%d'))
			for datelabel in timerange:
				if datelabel not in res:
					res[datelabel]=0
		colors=generate_random_color()
		sumup=sum(res.values())
		c_name=CategoryList.query.filter_by(book_id=book_id,id=data.category_id).first().category_name
		span=datetime.strptime(request.form['datefrom'], '%Y-%m-%d').strftime('%Y/%m/%d')+"〜"+datetime.strptime(request.form['dateto'], '%Y-%m-%d').strftime('%Y/%m/%d')+c_name+"の支出"
	return chart_type, forchart, res, sumup, span

def change_category(request,book_id):
	change_c=CategoryList.query.filter_by(book_id=book_id, id=request.form['category_id']).first()
	change_c.category_name=request.form['category_name']
	db.session.commit()

def delete_category(request,book_id):
	delete_c=CategoryList.query.filter_by(book_id=book_id, id=request.form['category_id']).first()
	delete_id=delete_c.id
	db.session.delete(delete_c)

	other=CategoryList.query.filter_by(book_id=book_id, category_name="その他").first().id
	for recode in BookRecode.query.filter_by(category_id=delete_id).all():
		recode.category_id=other
	db.session.commit()

def delete_thisbook(request,book_id):
	delete=BookRecode.query.filter_by(book_id=book_id).all()
	for i in delete:
		db.session.delete(i)
	delete=BookMap.query.filter_by(book_id=book_id).all()
	for i in delete:
		db.session.delete(i)
	db.session.commit()

def change_bookname(request,book_id):
	change_bookname=BookMap.query.filter_by(book_id=book_id).all()
	for recode in change_bookname:
		recode.book_name = request.form['bookname']
		db.session.commit()

def add_permission(request,book_id):
	add_permission=BookMap()
	add_permission.book_id = book_id
	add_permission.book_name = BookMap.query.filter_by(book_id=book_id).first().book_name
	add_permission.email = request.form['add_person']
	add_permission.permission = request.form['permission_level']
	db.session.add(add_permission)
	db.session.commit()

def change_permission(request,book_id):
	change_permission=BookMap.query.filter_by(book_id=book_id,email=request.form['change_person']).first()
	if int(request.form['permission_level']) <= 3:
		change_permission.permission = request.form['permission_level']
	if int(request.form['permission_level']) == 4:
		db.session.delete(change_permission)
	db.session.commit()

def generate_random_color():
    return '#{:X}{:X}{:X}'.format(*[random.randint(0, 255) for _ in range(3)])

if __name__ == "__main__":
	app.run(debug=False)
