from app import db
import datetime
#学校类
from app.utils import objToDict


class School(db.Model):
    __tablename__='school'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False)
    code=db.Column(db.String(10),unique=True)       #学校代码
    type=db.Column(db.String(2))                    #学校类别，“本科”，“专科”

    students=db.relationship('Student',backref='school')    #学生一对多

#学生类
class Student(db.Model):
    __tablename__='student'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False)
    sex=db.Column(db.Integer)
    student_number=db.Column(db.String(20),nullable=False,unique=True)   #学号
    college_name=db.Column(db.String(30))                    #学院名称
    grade=db.Column(db.String(5))                           #年级
    class_name=db.Column(db.String(20))                      #班级名称

    school_id=db.Column(db.Integer,db.ForeignKey('school.id'),nullable=False)   #学校id外键

    def serializable(self):
        ret=objToDict(self)
        ret.pop('school_id')
        return ret


#账户类
class Account(db.Model):
    __tablename__='account'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),nullable=True,unique=True) #用户名
    password=db.Column(db.String(255),nullable=True)             #密码
    type=db.Column(db.Integer,nullable=True)                    #账户类型，1校级账户，2省厅账户

    school_id=db.Column(db.Integer,db.ForeignKey('school.id'))  #学校id外键

#体测项目
class TestingProject(db.Model):
    __tablename__= 'testingproject'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(10),nullable=True)     #项目名称
    sex=db.Column(db.Integer,nullable=True)          #使用性别
    weight=db.Column(db.Float,nullable=True)        #项目权重
    create_time=db.Column(db.DateTime,default = datetime.datetime)               #创建时间

    standards=db.relationship('TestingStandard',backref='project')  #该项目下的标准

#体测项目的标准
class TestingStandard(db.Model):
    __tablename__='testingstandard'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(10))                   #标准名称（经常为分数）
    score=db.Column(db.Float,nullable=True)         #标准分数
    lower_data=db.Column(db.Float,nullable=True)     #量化后的数据的下界
    grade=db.Column(db.Integer,nullable=True)        #学生年级，123456代表大一到大五，及大六以上

    project_id=db.Column(db.Integer,db.ForeignKey('testingproject.id'),nullable=False)  #项目外键id

#体测成绩
class TestingScore(db.Model):
    __tablename__= 'testingscore'
    id = db.Column(db.Integer, primary_key=True)
    score=db.Column(db.Float,nullable=True)         #成绩
    row_data=db.Column(db.String(10))                #原始数据
    create_time=db.Column(db.DateTime,default = datetime.datetime)               #添加时间

    project_id=db.Column(db.Integer,db.ForeignKey('testingproject.id'),nullable=False)  #体测项目id
    student_id=db.Column(db.Integer,db.ForeignKey('testingstudent.id'),nullable=False)  #体测学生id

#体测学生
class TestingStudent(db.Model):
    __tablename__= 'testingstudent'
    id = db.Column(db.Integer, primary_key=True)
    year=db.Column(db.Integer,nullable=False)       #抽测年份
    score=db.Column(db.Float)                       #总分成绩
    comment=db.Column(db.String(255))               #备注
    grade=db.Column(db.Integer,nullable=True)        #学生年级，123456代表大一到大五，及大六以上

    student_id=db.Column(db.Integer,db.ForeignKey('student.id'),nullable=False) #学生id外键
    student=db.relationship('Student',uselist=False)    #建立学生关系

#学校成绩
class SchoolScore(db.Model):
    __tablename__= 'schoolscore'
    id = db.Column(db.Integer, primary_key=True)
    year=db.Column(db.Integer,nullable=False)       #年份
    testing_number=db.Column(db.Integer)            #测试人数
    score=db.Column(db.Float)                       #抽测学生平均总分成绩
    excellent_rate=db.Column(db.Float)              #优秀率
    good_rate=db.Column(db.Float)                   #良好率
    pass_rate=db.Column(db.Float)                   #通过率

    school_id=db.Column(db.Integer,db.ForeignKey('school.id'),nullable=False)   #学校id外键
    
#学校详细成绩
class SchoolScoreDetail(db.Model):
    __tablename__= 'schoolscoredetail'
    id = db.Column(db.Integer, primary_key=True)
    year=db.Column(db.Integer,nullable=False)       #年份
    score=db.Column(db.Float)                       #抽测学生平均成绩
    excellent_rate=db.Column(db.Float)              #优秀率
    good_rate=db.Column(db.Float)                   #良好率
    pass_rate=db.Column(db.Float)                   #通过率

    school_id=db.Column(db.Integer,db.ForeignKey('school.id'),nullable=False)   #学校id外键
    project_id = db.Column(db.Integer, db.ForeignKey('testingproject.id'), nullable=False)  # 体测项目id

#每年选体测项目
class ProjectSelection(db.Model):
    __tablename__='projectselection'
    id=db.Column(db.Integer,primary_key=True)
    year=db.Column(db.Integer,nullable=False)       #年份

    project_id=db.Column(db.Integer,db.ForeignKey('testingproject.id'),nullable=False)  #项目id

#抽取学生审核
class StudentSelection(db.Model):
    __tablename__='studentselection'
    id=db.Column(db.Integer,primary_key=True)
    year=db.Column(db.Integer,nullable=False)       #年份
    boy=db.Column(db.Integer,default=0)             #男生人数
    girl=db.Column(db.Integer,default=0)            #女生人数
    submit=db.Column(db.Integer,default=0)          #提交状态，0未提交，1已提交
    confirm=db.Column(db.Integer,default=0)         #审核状态,0审核不通过，1审核通过
    submit_comment=db.Column(db.String(255))        #提交备注
    confirm_comment=db.Column(db.String(255))       #审核备注

    school_id=db.Column(db.Integer,db.ForeignKey('school.id'),nullable=False)   #学校id外键

#菜单表
class Systemmenu(db.Model):
    __tablename__='systemmenu'
    id=db.Column(db.Integer,primary_key=True,nullable=False)
    pid=db.Column(db.Integer,default=0,nullable=False)
    title=db.Column(db.String(100),default="")
    icon=db.Column(db.String(100),default="")
    href=db.Column(db.String(100),default="")
    target=db.Column(db.String(20),default="_self")
    sort=db.Column(db.Integer,default=0)
    type=db.Column(db.Integer)#1院校端，2省厅端
    child=[]

    def serializable(self):
        rt={
            'title':self.title,
            'icon':self.icon,
            'href':self.href,
            'target':self.target,
            'child':[]
        }
        if self.child:
             rt['child']=[c.serializable() for c in self.child if self.child]
        return rt