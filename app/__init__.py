from flask import Flask, url_for, request, redirect, render_template, session
from flask.json import JSONEncoder
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config.from_object('config')
app.secret_key="I9XZH67Pb%0I"
db = SQLAlchemy(app)
#顺序生成视图、模型、创建数据库等
from app import views,models
app.debug = True


#debug=True
if not app.debug:
    from app import db_create

from app import service
#重写default支持自定义类
class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj,"serializable"):
            return obj.serializable()
        return super(MyJSONEncoder, self).default(obj)
app.json_encoder = MyJSONEncoder