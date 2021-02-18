#province.py
from flask import Blueprint,render_template, request

province = Blueprint('province',__name__)

@province.route('/index')
def index():
    return render_template('province/index.html')

@province.route('/add')
def add():
    return 'province_add'

@province.route('/show')
def show():
    return 'province_show'