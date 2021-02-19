from flask import Flask, url_for, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config.from_object('config')
app.secret_key="I9XZH67Pb%0I"
db = SQLAlchemy(app)
#顺序生成视图、模型、创建数据库等
from app import views,models
debug=True
#debug=True
if not debug:
    from app import db_create

from app import service