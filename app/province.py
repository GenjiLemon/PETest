#province.py
import functools

from flask import Blueprint, render_template, request, session
from werkzeug.utils import redirect

province = Blueprint('province',__name__)

def login_required(func):
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
@login_required
def index():
    return render_template('province/index.html')

@province.route('/addAccount')
@login_required
def addAccount():
    return render_template('province/addAccount.html')

@province.route('/addProject')
@login_required
def addProject():
    return render_template('province/addProject.html')

@province.route('/addSchool')
@login_required
def addSchool():
    return render_template('province/addSchool.html')

@province.route('/check')
@login_required
def check():
    return render_template('province/check.html')

@province.route('/checkList')
@login_required
def checkList():
    return render_template('province/checkList.html')

@province.route('/historyProject')
@login_required
def historyProject():
    return render_template('province/historyProject.html')

@province.route('/home')
@login_required
def home():
    return render_template('province/home.html')

@province.route('/projectRank')
@login_required
def projectRank():
    return render_template('province/projectRank.html')

@province.route('/school')
@login_required
def school():
    return render_template('province/school.html')

@province.route('/schoolAccount')
@login_required
def schoolAccount():
    return render_template('province/schoolAccount.html')

@province.route('/schoolRank')
@login_required
def schoolRank():
    return render_template('province/schoolRank.html')

@province.route('/selectProject')
@login_required
def selectProject():
    return render_template('province/selectProject.html')

@province.route('/testingProject')
@login_required
def testingProject():
    return render_template('province/testingProject.html')

@province.route('/testingStandard')
@login_required
def testingStandard():
    return render_template('province/testingStandard.html')

@province.route('/uploadSchool')
@login_required
def uploadSchool():
    return render_template('province/uploadSchool.html')

@province.route('/uploadScore')
@login_required
def uploadScore():
    return render_template('province/uploadScore.html')

