import functools

from flask import Blueprint, render_template, redirect, send_from_directory, url_for, session, request
from werkzeug.exceptions import abort

from app import app, service, db, models, utils

school = Blueprint('school',__name__)


def admin_required(func):
    @functools.wraps(func)#修饰内层函数，防止当前装饰器去修改被装饰函数__name__的属性
    def inner(*args,**kwargs):
        userid = session.get('user_id')
        print('获取session  userid',userid)
        if not  userid:
            return redirect('/login')
        else:
            return func(*args,**kwargs)
    return inner
#********页面访问********
# @school.route('/',methods=['GET'])
# def defaultIndex():
#     return redirect(url_for('/school/index'))

@school.route('/index',methods=['GET'])
@school.route('/',methods=['GET'])
@admin_required
def index():
    school=models.School.query.get(session['school_id'])
    return render_template('school/index.html',school=school)

@school.route('/home',methods=['GET'])
@admin_required
def home():
    return render_template('school/welcome-1.html')

@school.route('/addStudent',methods=['GET'])
@admin_required
def addStudent():
    return render_template('school/addStudent.html')

@school.route('/editStudent',methods=['GET'])
@admin_required
def editStudent():
    id=request.args.get('id')
    if id==None:
        abort(404)
    else:
        student=models.Student.query.get(id)
        if student:
            return render_template('school/editStudent.html',student=student)
        else:abort(404)


@school.route('/schoolScore',methods=['GET'])
@admin_required
def schoolScore():
    return render_template('school/schoolScore.html')

@school.route('/selectStudent',methods=['GET'])
@admin_required
def selectStudent():
    return render_template('school/selectStudent.html')

@school.route('/studentScore',methods=['GET'])
@admin_required
def studentScore():
    nowyear=utils.getNowTestingYear()
    return render_template('school/studentScore.html',nowyear=nowyear)

@school.route('/uploadStudent',methods=['GET'])
@admin_required
def uploadStudent():
    return render_template('school/uploadStudent.html')

@school.route('/gradeStudent',methods=['GET'])
@admin_required
def yearStudent():
    return render_template('school/gradeStudent.html')

@school.route('/scoreDetail',methods=['GET'])
@admin_required
def scoreDetail():
    id=request.args.get('id')
    if id==None :abort(404)
    scores=service.getStudentScore(id)
    return render_template('school/scoreDetail.html',scores=scores)
