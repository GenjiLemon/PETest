#province.py
import functools

from flask import Blueprint, render_template, request, session, jsonify
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from app import models,utils,service

province = Blueprint('province',__name__)

def admin_required(func):
    @functools.wraps(func)#修饰内层函数，防止当前装饰器去修改被装饰函数__name__的属性
    def inner(*args,**kwargs):
        userid = session.get('user_id')
        #需要同时认证userid和secret
        secret=session.get('secret')
        if userid==None or secret==None:
            return redirect('/login')
        else:
            return func(*args,**kwargs)
    return inner

@province.route('/')
@province.route('/index')
@admin_required
def index():
    return render_template('province/index.html')

@province.route('/addAccount')
@admin_required
def addAccount():
    return render_template('province/addAccount.html')

@province.route('/addProject')
@admin_required
def addProject():
    return render_template('province/addProject.html')

@province.route('/addSchool')
@admin_required
def addSchool():
    return render_template('province/addSchool.html')

@province.route('/editSchool')
@admin_required
def editSchool():
    id=request.args.get('id')
    if id:
        school=models.School.query.get(id)
        return render_template('province/editSchool.html',school=school)
    else: abort(404)
@province.route('/check')
@admin_required
def check():
    id=request.args.get('id')
    if id:
        model={}
        studentSelection=models.StudentSelection.query.get(id)
        model['comment']=studentSelection.submit_comment
        model['school_name']=models.School.query.get(studentSelection.school_id).name
        model['id']=id
        if studentSelection.submit==2:
            #resubmit mode
            model['type']="申请重新选择体测人"
        return render_template('province/check.html',model=model)
    else: abort(404)

@province.route('/checkList')
@admin_required
def checkList():

    return render_template('province/checkList.html')

@province.route('/historyProject')
@admin_required
def historyProject():
    year=request.args.get('year')
    if year:
        projects = []
        boy=service.getSelectProjects(year,1)
        girl=service.getSelectProjects(year,0)
        #两个相加，得出总的列表
        boy.extend(girl)
        #现在的boy是男生女生之和
        for e in boy:
            temp={}
            temp['sex']="男" if e.sex==1 else "女"
            temp['name']=e.name
            projects.append(temp)
        return render_template('province/historyProject.html',projects=projects)
    else:abort(404)

@province.route('/home')
@admin_required
def home():
    return render_template('province/home.html')

@province.route('/projectRank')
@admin_required
def projectRank():
    model = {}
    model['year'] = utils.getNowTestingYear()
    model['project_names']=service.getProjectNames(model['year'])
    return render_template('province/projectRank.html',model=model)

@province.route('/school')
@admin_required
def school():
    return render_template('province/school.html')

@province.route('/schoolAccount')
@admin_required
def schoolAccount():
    return render_template('province/schoolAccount.html')

@province.route('/schoolRank')
@admin_required
def schoolRank():
    model={}
    model['year']=utils.getNowTestingYear()
    return render_template('province/schoolRank.html',model=model)

@province.route('/selectProject')
@admin_required
def selectProject():
    return render_template('province/selectProject.html')

@province.route('/testingProject')
@admin_required
def testingProject():
    return render_template('province/testingProject.html')

@province.route('/testingStandard')
@admin_required
def testingStandard():
    id=request.args.get('id')
    if id:
        return render_template('province/testingStandard.html',id=id)
    else: abort(404)

@province.route('/uploadSchool')
@admin_required
def uploadSchool():
    return render_template('province/uploadSchool.html')

@province.route('/uploadScore')
@admin_required
def uploadScore():
    year=utils.getNowTestingYear()
    res = models.StudentSelection.query.filter(models.StudentSelection.year == year).all()
    schools = []
    for e in res:
        school = models.School.query.get(e.school_id)
        if school:
            schools.append({"id":school.id,"name":school.name})
    return render_template('province/uploadScore.html',schools=schools)

