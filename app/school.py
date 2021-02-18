from flask import Blueprint, render_template, redirect, send_from_directory
from app import app
school = Blueprint('school',__name__)

@school.route('/index')
def index():
    return render_template('school/index.html')
@school.route('/home')
def home():
    return render_template('school/welcome-1.html')
@school.route('/addStudent')
def addStudent():
    return render_template('school/addStudent.html')

@school.route('/schoolScore')
def schoolScore():
    return render_template('school/schoolScore.html')

@school.route('/selectStudent')
def selectStudent():
    return render_template('school/selectStudent.html')

@school.route('/studentScore')
def studentScore():
    return render_template('school/studentScore.html')

@school.route('/uploadStudent')
def uploadStudent():
    return render_template('school/uploadStudent.html')

@school.route('/yearStudent')
def yearStudent():
    return render_template('school/yearStudent.html')