from flask import Flask, session, redirect, url_for, request, render_template

app = Flask(__name__)
app.secret_key = 'sAec%mSWcFpt-6zwBHMPXZMLnx7t8fNeD4Kn/DZT'

@app.route('/')
def index():
	name="nanashi"
	if 'username' in session:
		name=str(session['username'])
	return render_template('index.html', title='flask test', name=name)

@app.route('/login', methods=['GET', 'POST'])
def login():
	name=""
	is_login=False
	if 'email' in session:
		name=str(session['email'])
		is_login=True
	if request.method == 'POST':
		session['email'] = request.form['email']
		return redirect(url_for('index'))
	return render_template('login.html', name=name, is_login=is_login)

@app.route('/logout')
def logout():
	session.pop('username', None)
	return render_template('logout.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
	email=""
	password=""
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		session['email'] = email

	return render_template('registration.html', email=email, password=password)


if __name__ == "__main__":
	app.run(debug=True)
