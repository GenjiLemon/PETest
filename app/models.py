from app import db

# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True)
#     email = db.Column(db.String(320), unique=True)
#     password = db.Column(db.String(32), nullable=False)
#
#     def __repr__(self):
#         return '<User %r>' % self.username
#
#
# class Admin(db.Model):
#     __tablename__ = 'admins'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True)
#     email = db.Column(db.String(320), unique=True)
#     password = db.Column(db.String(32), nullable=False)
#
#     def __repr__(self):
#         return '<User %r>' % self.username

class School(db.Model):
    __tablename__='school'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False)
    code=db.Column(db.String(10),unique=True)       #学校代码
    type=db.Column(db.String(2))                    #学校类别，“本科”，“专科”
    students=db.Relationship('Student','school')    #学生一对多

class Student(db.Model):
    __tablename__='student'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False)
    sex=db.Column(db.Integer)
    studentnumber=db.Column(db.String(20),nullable=False)   #学号
    collegename=db.Column(db.String(30))                    #学院名称
    grade=db.Column(db.String(5))                           #年级
    classname=db.Column(db.String(20))                      #班级名称

    school_id=db.Column(db.Integer,db.ForeignKey('school.id'),nullable=False)   #学校id外键

class User(db.Model):
    __tablename__:'user'
    id=db.Column(db.Integer,primary_key=True)

class TestingProject(db.Model):
    __tablename__: 'testingproject'
    id = db.Column(db.Integer, primary_key=True)

class TestingStandard(db.Model):
    __tablename__: 'testingstandard'
    id = db.Column(db.Integer, primary_key=True)

class TestingScore(db.Model):
    __tablename__: 'testingscore'
    id = db.Column(db.Integer, primary_key=True)

class TestingStudent(db.Model):
    __tablename__: 'testingstudent'
    id = db.Column(db.Integer, primary_key=True)

class SchoolScore(db.Model):
    __tablename__: 'schoolscore'
    id = db.Column(db.Integer, primary_key=True)