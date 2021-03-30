import datetime

from sqlalchemy import func

from app import db
#学校类
from app.utils import objToDict


class School(db.Model):
    __tablename__='school'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False)
    code=db.Column(db.String(10),unique=True)       #学校代码
    type=db.Column(db.String(4))                    #学校类别，“本科”，“高职高专”

    #让jsonify能正常执行，重写default方法，执行对象的serializable
    def serializable(self):
        #除了_开头的都返回回来
        ret = objToDict(self)
        return ret


#学生类
class Student(db.Model):
    __tablename__='student'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False)
    sex=db.Column(db.Integer)
    student_number=db.Column(db.String(20),nullable=False)   #学号
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

    def serializable(self):
        #密码不发回去
        ret = objToDict(self)
        ret['password']="****"
        ret.pop("school_id")
        return ret

#体测项目
class TestingProject(db.Model):
    __tablename__= 'testingproject'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(10),nullable=True)     #项目名称
    sex=db.Column(db.Integer,nullable=True)          #使用性别
    weight=db.Column(db.Float,nullable=True)        #项目权重
    create_time=db.Column(db.DateTime,default = datetime.datetime.now)               #创建时间
    scoreType=db.Column(db.Integer,default=1) #赋分是高优还是低优，1是高优，-1是低优
    comment=db.Column(db.String(50),default="")#备注

    standards=db.relationship('TestingStandard',backref='project')  #该项目下的标准
    def serializable(self):
        #密码不发回去
        ret = objToDict(self)
        return ret

#体测项目的标准
class TestingStandard(db.Model):
    __tablename__='testingstandard'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(10))                   #标准名称（经常为分数）
    score=db.Column(db.Float,nullable=True)         #标准分数
    bottom=db.Column(db.Float,nullable=True)     #量化后的数据的下界
    top=db.Column(db.Float,nullable=True)     #量化后的数据的上界
    level=db.Column(db.Integer,nullable=True)        #学生年级，123456代表大一到大五，及大六以上
    comment=db.Column(db.String(50),default="")#备注

    project_id=db.Column(db.Integer,db.ForeignKey('testingproject.id'),nullable=False)  #项目外键id
    def serializable(self):
        #密码不发回去
        ret = objToDict(self)
        return ret
#体测成绩
class TestingScore(db.Model):
    __tablename__= 'testingscore'
    id = db.Column(db.Integer, primary_key=True)
    score=db.Column(db.Float,nullable=True)         #成绩
    row_data=db.Column(db.String(10))                #原始数据
    create_time=db.Column(db.DateTime,default = datetime.datetime.now)               #添加时间

    project_id=db.Column(db.Integer,db.ForeignKey('testingproject.id'),nullable=False)  #体测项目id
    school_id=db.Column(db.Integer,db.ForeignKey('school.id'))  #为了减少查询，增加一点冗余
    tstudent_id=db.Column(db.Integer,db.ForeignKey('testingstudent.id'),nullable=False)  #体测学生id

#体测学生
class TestingStudent(db.Model):
    __tablename__= 'testingstudent'
    id = db.Column(db.Integer, primary_key=True)
    year=db.Column(db.Integer,nullable=False)       #抽测年份
    score=db.Column(db.Float,default=0)                       #总分成绩
    comment=db.Column(db.String(255),default="")               #备注
    level=db.Column(db.Integer,nullable=True)        #学生年级，123456代表大一到大五，及大六以上

    student_id=db.Column(db.Integer,db.ForeignKey('student.id'),nullable=False) #学生id外键
    school_id=db.Column(db.Integer,db.ForeignKey('school.id'),nullable=False)#为了节省查询，牺牲一点冗余
    student=db.relationship('Student',uselist=False)    #建立学生关系

#学校成绩
class SchoolScore(db.Model):
    __tablename__= 'schoolscore'
    id = db.Column(db.Integer, primary_key=True)
    year=db.Column(db.Integer,nullable=False)       #年份
    testing_number=db.Column(db.Integer)            #测试人数
    boy_number=db.Column(db.Integer)                #男生人数
    girl_number=db.Column(db.Integer)               #女生人数
    score=db.Column(db.Float)                       #抽测学生平均总分成绩
    excellent_rate=db.Column(db.Float)              #优秀率
    excellent_number=db.Column(db.Integer)          #优秀人数
    excellent_boy_number=db.Column(db.Integer)      #优秀男生人数
    excellent_girl_number=db.Column(db.Integer)     #优秀女生人数
    good_rate=db.Column(db.Float)                   #良好率
    good_number=db.Column(db.Integer)               #良好人数
    good_boy_number=db.Column(db.Integer)           #良好男生人数
    good_girl_number=db.Column(db.Integer)          #良好女生人数
    pass_rate=db.Column(db.Float)                   #及格率
    pass_number=db.Column(db.Integer)               #及格人数
    pass_boy_number=db.Column(db.Integer)           #及格男生人数
    pass_girl_number=db.Column(db.Integer)          #及格女生人数
    school_id=db.Column(db.Integer,db.ForeignKey('school.id'),nullable=False)   #学校id外键

    def serializable(self):
        #密码不发回去
        ret = objToDict(self)
        return ret

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

    def serializable(self):
        #密码不发回去
        ret = objToDict(self)
        return ret

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
    submit=db.Column(db.Integer,default=0)          #提交状态，0未提交，1submit，2 isapply reselect
    confirm=db.Column(db.Integer,default=0)         #审核状态,0审核不通过，1审核通过
    #0，0代表审核不通过 1，0代表已提交未审核 1，1代表审核通过 没有记录代表未提交
    submit_comment=db.Column(db.String(255),default="")        #提交备注
    confirm_comment=db.Column(db.String(255),default="")       #审核备注

    school_id=db.Column(db.Integer,db.ForeignKey('school.id'),nullable=False)   #学校id外键
    update_time = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())#修改时间，自动更新字段

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

#系统配置表
class Systemsetting(db.Model):
    __tablename__='systemsetting'
    id=db.Column(db.Integer,primary_key=True,nullable=False)
    name=db.Column(db.String(20))                                                         #配置名
    comment=db.Column(db.String(50),default="")                                           #备注
    value=db.Column(db.String(50))                                                        #配置值
    update_time = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())  # 修改时间，自动更新字段

    def serializable(self):
        ret = objToDict(self)
        return ret