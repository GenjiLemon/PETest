import functools

from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.exceptions import abort

from app import db,models,service
from sqlalchemy import and_,or_
from .utils import *
api = Blueprint('api',__name__)

def login_required(func):
    @functools.wraps(func)#修饰内层函数，防止当前装饰器去修改被装饰函数__name__的属性
    def inner(*args,**kwargs):
        userid = session.get('user_id')
        print('获取session  userid',userid)
        if not  userid:
            #api里返回错误代码而不是跳转
            return jsonRet(-2,"您还未登录,请先登录！")
        else:
            return func(*args,**kwargs)
    return inner

@api.route('/student',methods=['GET','POST','PUT','DELETE'])
@login_required
def school_student():
    if request.method=="POST":
        student=models.Student()
        data=request.form.to_dict()
        student.name=data.get('name')
        student.sex = data.get('sex')
        student.student_number=data.get('student_number')
        student.college_name = data.get('college_name')
        student.grade = data.get('grade')
        student.class_name=data.get('class_name')
        student.school_id=session.get('school_id')
        if(service.addStudent(student)):
            return jsonRet()
        else: return jsonRet(-1,"请检查信息后再提交")
    elif request.method=="GET":
        args=request.args.to_dict()
        data=service.findStudents(session.get('school_id'),
                                  name=args.get('name'),number=args.get('student_number'),
                                  college=args.get('college_name'),grade=args.get('grade'),
                                  class_name=args.get('class_name'),sex=args.get('sex'))
        return jsonRet(data=data)
    elif request.method=="DELETE":
        id=request.form.get('id')
        if id:
            student=models.Student.query.get(id)
            db.session.delete(student)
            db.session.commit()
            return jsonRet()
        else: return jsonRet(-1,"id不存在")
    elif request.method=="PUT":
        student = models.Student()
        data = request.form.to_dict()
        student.id = data.get('id')
        student.name = data.get('name')
        student.sex = data.get('sex')
        student.student_number = data.get('student_number')
        student.college_name = data.get('college_name')
        student.grade = data.get('grade')
        student.class_name = data.get('class_name')
        student.school_id = session.get('school_id')
        if service.updateStudent(student):
            return jsonRet()
        else: return jsonRet(-1,"更新失败")
    else: return jsonRet(-1)

@api.route('/testingStudent',methods=["GET","POST"])
@login_required
def school_testingStudent():
    if request.method=="GET":
        data=request.args.to_dict()
        data=service.getMultipleStudentScore(session.get('school_id'),data.get('grade'),data.get('college_name'),data.get('student_number'),data.get('year'),data.get('name'))
        return jsonRet(data=data)
    if request.method=="POST":
        idsstr=request.form.get('student_ids')
        if idsstr:
            ids=idsstr.split(",")
            map(int,ids)
            ret={}
            ret['total_num']=len(ids)
            ret['success_num']=service.selectStudents(ids,getNowTestingYear())
            return jsonRet(data=ret)
        else:return jsonRet(-1,"没有找到id参数")
    else: abort(404)

#获取历史体测成绩抽取情况
@api.route('/getTestingSelectionBefore')
@login_required
def school_getTestingSelectionBefore():
    data=service.getTestingStudentSumBefore(getNowTestingYear(),session['school_id'])
    count=len(data)
    return jsonRet(data=data,count=count)

#获取每个年级的学生名册情况
@api.route('/gradeStudent',methods=["GET"])
@login_required
def school_gradeStudent():
    data=service.getStudentSums(session['school_id'])
    #加个id栏
    data=addIdColumn(data)
    count= len(data)
    return jsonRet(data=data,count=count)

#获取每个年级的学生体测情况
@api.route('/testingGradeStudent',methods=["GET"])
@login_required
def school_testingGradeStudent():
    year=getNowTestingYear()
    data=service.getTestingStudentSums(year,session['school_id'])
    #加个id栏
    count=len(data)
    return jsonRet(data=data,count=count)
@api.route('/changePassword',methods=['POST'])
@login_required
def changePassword():
    res=service.changePassword(session['user_id'],request.form.get('old_password'),request.form.get('new_password'))
    if res==True:
        service.logout()
        return jsonRet()
    else:
        return jsonRet(msg=res)

@api.route("/systemInit",methods=['GET'])
@login_required
def getSystemInit(type=1):
    if type==1:
        homeInfo= {
            "title":"首页",
            "href":"/school/home"
        }
        logoInfo={
            "title":"院校端",
            "image":"/static/layuimini/images/logo.png",
            "href":""
        }
        menuInfo=__getMenuList(type)
        init={
            "homeInfo":homeInfo,
            "logoInfo":logoInfo,
            "menuInfo":menuInfo
        }
        return jsonify(init)

def __getMenuList(type):
    menu=models.Systemmenu
    menulist=menu.query.filter(and_(menu.pid==0,menu.type==type)).order_by(menu.sort).all()
    for m in menulist:
        m.child=__buildChild(m.id,type)
    return menulist

def __buildChild(pid,type):
    menu=models.Systemmenu
    childmenuns=menu.query.filter(and_(menu.pid==pid,menu.type==type)).order_by(menu.sort).all()
    if childmenuns:
        for cm in childmenuns:
            cm.child=__buildChild(cm.id,type)
        return childmenuns
    return

@api.route("/uploadStudent", methods=["POST"])
@login_required
def uploadStudent():
    f = request.files.get('file',None)
    if f:
        WS = pd.read_excel(f)
        data=np.array(WS).tolist()
        header=['college_name','grade','class_name','name','sex','student_number','school_id']
        school_id=session['school_id']
        for e in data:
            e.append(school_id)
            if e[4]=='男':
                e[4]=1
            else:
                e[4]=0
        count= len(data)-1
        service.quickInsert(models.Student,header,data)
        return jsonRet(msg="新增了{}个学生".format(count))
    return jsonRet(-1,msg="没有找到上传文件")

@api.route('/student-list')
def studentlist():
    return {
  "code": 0,
  "msg": "",
  "count": 1000,
  "data": [
    {
      "id": 1,
      "college_name":"物理学院",
	  "grade":2020,
	  "class_name":"物理学",
	  "name":"小明",
	  "sex":"男",
	  "student_number":"20202020202020",
	  "comment":"备注"
    },
    {"id": 2,
      "college_name":"数学学院",
      "grade":2020,
      "class_name":"数学应用数学",
      "name":"小红",
      "sex":"女",
      "student_number":"20202020202021",
      "comment":"备注"
    }
  ]
}