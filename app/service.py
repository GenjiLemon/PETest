#此文件为中间服务类
from flask import session
from werkzeug.security import generate_password_hash,check_password_hash
from app import db,app
from app.models import *
from . import utils
import os

from .utils import gradeToInt


#**************账户begin**************
#登录
#返回账户类型，1学校，2省厅，0错误


def login(username,password):
    # account=Account.query.filter_by(username=username).
    pass
def logout():
    session.pop('user_id')
    session.pop('school_id')
#创建学校账户
def createAccount(username,password,schoolid):
    pass

#根据账户名更换密码
def changePassword(user_id,old_password,new_password):
    user=Account.query.get(user_id)
    if user:
        if check_password_hash(user.password,old_password):
            user.password=generate_password_hash(new_password)
            db.session.commit()
            return True
        else: return "旧密码错误!"
    else:
        return "用户未找到！"
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
def getStudentSumByGrade(grade,school_id):
    res = db.session.execute(
        "SELECT s.sex,COUNT(s.sex) FROM student s WHERE grade='{}' and school_id={} GROUP BY s.sex ".format(grade,school_id))
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
def getStudentSums(school_id):
    sums=[]
    #先查出所有的grade，再拿grade查出每个年级的情况
    res=Student.query.with_entities(Student.grade).distinct().order_by(Student.grade.desc()).all()
    for e in res:
        sums.append(getStudentSumByGrade(e[0],school_id))
    return sums
#查询学生
def findStudents(schoolid,name=None,number=None,college=None,grade=None,class_name=None,sex=None):
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
    if class_name:
        filter_list.append(Student.class_name==class_name)
    if sex:
        filter_list.append(Student.sex==sex)
    return Student.query.filter(*filter_list).all()
#选择学生
#传入学生id的list
def selectStudents(studentids,year:int):
    success_num=0
    for id in studentids:
        student=Student.query.get(id)
        if student:
            if TestingStudent.query.filter(TestingStudent.student_id==id).first()==None:
                testingStudent=TestingStudent()
                testingStudent.year=year
                # year等于2018 说明2018-2019年的体测，2018级的学生属于大一
                testingStudent.level=year-gradeToInt(student.grade)+1
                testingStudent.student_id=student.id
                testingStudent.school_id=student.school_id
                db.session.add(testingStudent)
                #记录成功添加一个体测学生
                success_num=success_num+1
    db.session.commit()
    return success_num
#查询指定年抽取人数情况
#查询一个年级体测学生情况
def getTestingStudentSumByGrade(grade,year,school_id):
    res = db.session.execute(
        "SELECT s.sex,COUNT(s.sex) FROM testingstudent ts INNER JOIN student s ON ts.student_id=s.id WHERE ts.year={} AND s.grade='{}' AND s.school_id={}  GROUP BY s.sex ".format(year,grade,school_id))
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

#获取历史体测情况
def getTestingStudentSumBefore(nowyear,school_id):
    #先获取所有的年
    res=TestingStudent.query.with_entities(TestingStudent.year).filter(TestingStudent.school_id==school_id,TestingStudent.year<nowyear).distinct().all()
    ret=[]
    if res:
        for e in res:
            #每年的数据根据审核上交的情况来获取
            selection=StudentSelection.query.filter(StudentSelection.year==e[0],StudentSelection.school_id==school_id).first()
            temp={}
            temp['boy_num']=selection.boy
            temp['girl_num']=selection.girl
            temp['year']=e[0]
            ret.append(temp)
        return ret
    return ret


#查询指定年每个年级体测学生的情况
def getTestingStudentSums(year:int,school_id):
    #year为2018代表体测年2018，及2018-2019
    sums=[]
    #先查出所有的grade，再拿grade查出每个年级的情况
    res=TestingStudent.query.join(Student).filter().with_entities(Student.grade).filter(TestingStudent.year==year).distinct().order_by(Student.grade.desc()).all()
    for e in res:
        sums.append(getTestingStudentSumByGrade(e[0],year,school_id))
    return sums

#查询单个学生成绩
def getStudentScore(tstudent_id):
    #注意是从testingstudent里查
    res=db.session.execute(
        "SELECT tp.name ,ts.score FROM  testingscore ts JOIN Testingproject tp ON ts.project_id=tp.id WHERE ts.student_id={}".format(tstudent_id)
    )
    ret={}
    for e in res:
        #0是name，1是score
        ret[e[0]]=e[1]
    return ret

#筛选查询成绩
def getMultipleStudentScore(schoolid,grade=None,college=None,number=None,year=None,name=None):
    filter_list = []
    filter_list.append(TestingStudent.school_id == schoolid)
    if name:
        filter_list.append(Student.name == name)
    if number:
        filter_list.append(Student.student_number == number)
    if college:
        filter_list.append(Student.college_name == college)
    if grade:
        filter_list.append(Student.grade == grade)
    if year:
        filter_list.append(TestingStudent.year == year)
    res=TestingStudent.query.join(Student).filter(*filter_list).all()
    ret=[]
    for e in res:
        studentscore={}
        #拿的因该是testingstudent的id
        studentscore['id']=e.id
        studentscore['college_name']=e.student.college_name
        studentscore['grade']=e.student.grade
        studentscore['class_name']=e.student.class_name
        studentscore['name']=e.student.name
        studentscore['sex']=e.student.sex
        studentscore['student_number']=e.student.student_number
        studentscore['year']=e.year
        studentscore['score']=e.score
        ret.append(studentscore)
    return ret

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