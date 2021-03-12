import functools

from flask import Blueprint, render_template, redirect, send_from_directory, url_for, session, request, jsonify
from app import app,service,db,models
from werkzeug.security import generate_password_hash,check_password_hash

from .utils import jsonRet



def login_required(func):
    @functools.wraps(func)#修饰内层函数，防止当前装饰器去修改被装饰函数__name__的属性
    def inner(*args,**kwargs):
        userid = session.get('user_id')
        print('获取session  userid',userid)
        if not  userid:
            return redirect('/login')
        else:
            return func(*args,**kwargs)
    return inner

@app.route("/")
def index():
    #进来旧先登录
    return redirect('/login')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    #如果登录了，就直接跳转
    if session.get('user_id'):
        userid=session['user_id']
        user=models.Account.query.get(userid)
        if user.type == 1:
            return redirect("/school/index")
        elif user.type == 2:
            return redirect("/province/index")
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
                    if models.School.query.get(user.school_id) == None:
                        return jsonRet(-1,"学校不存在！")
                    session['user_id'] = user.id
                    session['school_id'] = user.school_id
                    return jsonRet(data={"url":"/school/index"})
                elif user.type==2:
                    session['user_id'] = user.id
                    session['secret']='faybaba'
                    return jsonRet(data={"url":"/province/index"})
        #没有提前返回的都错了
        return jsonRet(code=-1,msg="账号或密码错误！")


@app.route('/changePassword')
@login_required
def changePassword():
    return render_template('changePassword.html')

@app.route('/logout')
@login_required
def logout():
    service.logout()
    return redirect('/login')

