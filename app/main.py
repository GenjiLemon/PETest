from flask import Blueprint, render_template, redirect, send_from_directory, url_for, session, request, jsonify
from app import app,service,db,models
from werkzeug.security import generate_password_hash,check_password_hash

from .utils import jsonRet

@app.before_request
def debug_login(*args, **kwargs):
    session['school_id'] = 1
    session['user_id'] = 1

@app.route("/")
def index():
    #return redirect('/login')
    return redirect('/school/index')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect("/school/index")
    #省厅方式没写

    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username and password:
            account=models.Account
            user=account.query.filter(account.username==username).first()
            if user and check_password_hash(user.password,password):
                if user.type==1:
                    session['user_id'] = user.id
                    session['school_id'] = user.school_id
                    return jsonRet(data={"url":"/school/index"})
                elif user.type==2:
                    return jsonRet(data={"url":"/province/index"})
        #没有提前返回的都错了
        return jsonRet(code=-1)
