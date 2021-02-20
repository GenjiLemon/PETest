#此文件为中间服务类
from app import db,app
from app.models import *
from . import utils
import os

#**************账户begin**************
#登录
#返回账户类型，1学校，2省厅，0错误
def login(username,password):
    # account=Account.query.filter_by(username=username).
    pass

#创建学校账户
def createAccount(username,password,schoolid):
    pass

#根据账户名更换密码
def changePassword(username,password):
    pass
#**************账户end**************


#**************省厅begin**************
def addSchool(name,type,code=None):
    pass

#批量添加
#传入school的list
def addAllSchool(schoollist):
    pass

#通过code或者name找学校
def findSchool(code=None,name=None):
    pass

#通过id删除学校
def delSchool(id):
    pass

#修改学校
def editSchool(id,name=None,code=None,type=None):
    pass

#审核学校学生名单
def confirmStudent(id):
    pass

#体测项目增加
def addProject(name,sex,weight):
    pass

#体测项目修改
def editProject(id,name=None,sex=None ,weight=None):
    pass

#删除体测项目
def delProject(id):
    pass

#项目标准增加
def addStandard(projectid,name,score,lowerdata,grade):
    pass

#项目标准修改
def editStandard(id,name=None,score=None,lowerdata=None,grade=None):
    pass

#项目标准删除
def delStandard(id):
    pass

#选择项目
#传入id的list
def selectProject(projectids,sex):
    pass

#删除选择的项目
def delSelectProject(projectid,sex):
    pass

#成绩导入
def importScore():
    pass

#**************省厅end**************


#**************各种数据导出**************
#**************各种数据导出**************



#**************学校端begin**************
#导入学生信息
def importStudent(filename,school_id):
    file_root_path=r"F:/zanproject/高校体测数据处理系统/code/tests/"
    filepath=os.path.join(file_root_path,filename)
    data=utils.excelToMatrix(filepath,header=0)
    columns=['school_id','college_name','grade','class_name','name','sex','student_number']
    for e in data:
        e[0]=1
        e[5]=1 if e[5]=="男" else 0
    quickInsert(Student,columns,data)

def addStudent(student:Student):
   try:
       db.session.add(student)
       db.session.commit()
   except Exception as e:
       print(e)
       return False
   return True
def updateStudent(student):
    mstudent=Student.query.get(student.id)
    if mstudent:
        mstudent.name = student.name
        mstudent.sex = student.sex
        mstudent.student_number = student.student_number
        mstudent.college_name = student.college_name
        mstudent.grade = student.grade
        mstudent.class_name = student.class_name
        db.session.commit()
        return True
    return False
#查询一个年级学生情况
def getStudentSumByGrade(grade):
    res = db.session.execute(
        "SELECT s.sex,COUNT(s.sex) FROM student s WHERE grade='{}' GROUP BY s.sex ".format(grade))
    ret={}
    #按照返回的情况是sex先0后1
    ret['girl_num']=0
    ret['boy_num'] = 0
    for e in list(res):
        if e[0]==0:
            ret['girl_num']=e[1]
        else:
            ret['boy_num']=e[1]
    ret['total_num']=ret['girl_num']+ret['boy_num']
    ret['grade']=grade
    return ret
#查询每个年级学生的情况
def getStudentSums():
    sums=[]
    #先查出所有的grade，再拿grade查出每个年级的情况
    res=Student.query.with_entities(Student.grade).distinct().order_by(Student.grade.desc()).all()
    for e in res:
        sums.append(getStudentSumByGrade(e[0]))
    return sums
#查询学生
def findStudents(schoolid,name=None,number=None,college=None,grade=None):
    filter_list=[]
    filter_list.append(Student.school_id==schoolid)
    if name:
        filter_list.append(Student.name==name)
    if number:
        filter_list.append(Student.student_number==number)
    if college:
        filter_list.append(Student.college_name==college)
    if grade:
        filter_list.append(Student.grade==grade)
    return Student.query.filter(*filter_list).all()
#选择学生
#传入学生id的list
def selectStudent(schoolid,studentids):
    pass

#查询单个学生成绩
def getStudentScore(schoolid,number=None,name=None):
    pass

#筛选查询成绩
#年级，1，2，3，4大一大二大三大四
def getMultipleStudentScore(schoolid,grade=None,college=None,classname=None):
    pass

#获取学校人数、分数排名等
def getSchoolScore(schoolid,year):
    pass

#**************学校段end**************

#**************公共方法**************
#传入类，列名和数据，快速插入到数据库
def quickInsert(model,columns,data):
    db.session.execute(
        model.__table__.insert(),
        [dict(zip(columns,d)) for d in data]
    )
    db.session.commit()