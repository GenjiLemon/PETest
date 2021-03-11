import functools

from flask import Blueprint, render_template, redirect, send_from_directory, url_for, session, request
from werkzeug.exceptions import abort

from app import app, service, db, models, utils

school = Blueprint('school',__name__)


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
#********页面访问********
# @school.route('/',methods=['GET'])
# def defaultIndex():
#     return redirect(url_for('/school/index'))

@school.route('/index',methods=['GET'])
@school.route('/',methods=['GET'])
@login_required
def index():
    school=models.School.query.get(session['school_id'])
    return render_template('school/index.html',school=school)

# @school.route('/home',methods=['GET'])
# @login_required
# def home():
#     return render_template('school/welcome-1.html')

@school.route('/addStudent',methods=['GET'])
@login_required
def addStudent():
    return render_template('school/addStudent.html')

@school.route('/editStudent',methods=['GET'])
@login_required
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
@login_required
def schoolScore():
    model={}
    model['year']=utils.getNowTestingYear()
    return render_template('school/schoolScore.html',model=model)

@school.route('/selectStudent',methods=['GET'])
@login_required
def selectStudent():
    return render_template('school/selectStudent.html')

@school.route('/removeTStudent',methods=['GET'])
@login_required
def removeTStudent():
    return render_template('school/removeTStudent.html')

@school.route('/studentScore',methods=['GET'])
@login_required
def studentScore():
    nowyear=utils.getNowTestingYear()
    return render_template('school/studentScore.html',nowyear=nowyear)

@school.route('/uploadStudent',methods=['GET'])
@login_required
def uploadStudent():
    return render_template('school/uploadStudent.html')

@school.route('/gradeStudent',methods=['GET'])
@login_required
def yearStudent():
    return render_template('school/gradeStudent.html')

@school.route('/scoreDetail',methods=['GET'])
@login_required
def scoreDetail():
    id=request.args.get('id')
    if id==None :abort(404)
    scores=service.getStudentScore(id)
    return render_template('school/scoreDetail.html',scores=scores)

@school.route('/submitStatus')
@login_required
def submitStatus():
    year=utils.getNowTestingYear()
    school_id=session.get('school_id')
    status=service.getSubmitStatus(school_id,year)
    status_word="未知"
    if status==-1:
        status_word="未提交"
    elif status==0:
        status_word="审核未通过"
    elif status==1:
        status_word="审核中"
    elif status==2:
        status_word="审核已通过"
    elif status==3:
        status_word="申请重新提交中"
    model={}
    model['status_word']=status_word
    model['status']=status
    StudentSelection=models.StudentSelection
    studentSelection = StudentSelection.query.filter(StudentSelection.year == year,
                                                     StudentSelection.school_id == school_id).first()
    model['submit_comment']=studentSelection.submit_comment
    model['confirm_comment']=studentSelection.confirm_comment
    return render_template('school/submitStatus.html',model=model)