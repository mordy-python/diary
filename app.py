from datetime import datetime
from flaskwebgui import FlaskUI
from tkinter import Tk

import bcrypt
from bson.objectid import ObjectId
from flask import Flask, flash, redirect, render_template, request, session, url_for
from pymongo import MongoClient

width = Tk().winfo_screenwidth() - 100
height = Tk().winfo_screenheight() - 100

app = Flask(__name__)
app.config['SECRET_KEY'] = b'=b\xe9`\xb8>\x06\x01\x86a\xae\xc3]4\xcd\xa4\x175=\xa6\x8d\xf9\xdc\x0e'
ui = FlaskUI(app, width=width, height=height)

client = MongoClient("mongodb+srv://mordy:<password>@clustermug.phvvx.mongodb.net/chroniclers?retryWrites=true&w=majority")

db = client.chroniclers
users = db.users 
entries = db.entries

@app.route('/')
def index():
    if 'username' in session:
        user = users.find_one({'username':session['username']})
        UID = user['_id']
        user_entries = entries.find({'author':ObjectId(UID)}).sort('date', -1)
        return render_template('index.html', logged_in_as=session['username'], Myentries=user_entries)
    else:
        return redirect(url_for('login'))
@app.route('/save-entry', methods=['POST'])
def saveEntry():
    title = request.form.get('title')
    content = request.form.get('content')
    user = users.find_one({'username':session['username']})
    UID = user['_id']
    entry = {
        'author':UID,
        'title':title,
        'content':content,
        'date':datetime.utcnow(),   
    }
    entries.insert_one(entry)
    return redirect(url_for('index'))
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        uname = request.form.get('uname').lower()
        existing_user = users.find_one({'username':uname})
        if existing_user is None: # user doesnt exist
            pwd1 = request.form.get('psw')
            pwd2 = request.form.get('psw2')
            if pwd1 != pwd2:
                flash('Passwords do not match')
                return redirect(url_for('signup'))
            else: #passwords do match
                hashedpw = bcrypt.hashpw(pwd1.encode('utf-8'), bcrypt.gensalt())
                users.insert_one({
                    'username':uname,
                    'password':hashedpw
                })
                session['username'] = uname 
                return redirect(url_for('index'))
        else:
            flash('That username is taken')
            return redirect(url_for('signup'))
    else:
        return render_template('signup.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('uname').lower()
        password = request.form.get('psw')
        # check if user exists
        user = users.find_one({'username':uname})
        if user: # Now that we know that this user exists, we can hash their pwd and log them in
            if bcrypt.hashpw(password.encode('utf-8'), user['password']) == user['password']:
                # if the password they entered after hashing was the same as the password stored in the db after hashing theyre good to go and we log them in
                session['username'] = user['username']
                return redirect(url_for('index'))
            else: # If the login is wrong
                flash('Invalid Login')
                return redirect(url_for('index'))
        else: # If the username doesn't exist
            flash('Invalid Login')
            return redirect(url_for('index'))
    else:
        return render_template('login.html')
    

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    # app.run(debug=True)
    ui.run()
