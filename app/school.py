from flask import Blueprint, render_template, redirect, send_from_directory, url_for,session
from app import app,service
school = Blueprint('school',__name__)



#********页面访问********
@school.route('/',methods=['GET'])
def defaultIndex():
    return redirect(url_for('/school/index'))

@school.route('/index',methods=['GET'])
def index():
    return render_template('school/index.html')

@school.route('/home',methods=['GET'])
def home():
    return render_template('school/welcome-1.html')

@school.route('/addStudent',methods=['GET'])
def addStudent():
    return render_template('school/addStudent.html')


@school.route('/schoolScore',methods=['GET'])
def schoolScore():
    return render_template('school/schoolScore.html')

@school.route('/selectStudent',methods=['GET'])
def selectStudent():
    return render_template('school/selectStudent.html')

@school.route('/studentScore',methods=['GET'])
def studentScore():
    return render_template('school/studentScore.html')

@school.route('/uploadStudent',methods=['GET'])
def uploadStudent():
    return render_template('school/uploadStudent.html')

@school.route('/yearStudent',methods=['GET'])
def yearStudent():
    return render_template('school/gradeStudent.html')