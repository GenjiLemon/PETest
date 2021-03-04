from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager,Shell
from flask import Flask, url_for, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from app import app,db
from app.models import *
##数据迁移关键代码
manage = Manager(app)
# 第一个参数是Flask的实例，第二个参数是Sqlalchemy数据库实例
migrate = Migrate(app, db)
# manager是Flask-Script的实例，这条语句在flask-Script中添加一个db命令
manage.add_command('db', MigrateCommand)
##调用迁移的入口方法cd .

if __name__ == '__main__':
    manage.run()
#第一次迁移需要先建立
#python migrate.py db init
#python migrate.py db migrate -m "create table"
#python migrate.py db upgrade

#后来只需要这两句
#python migrate.py db migrate -m "迁移备注信息"
#python migrate.py db upgrade

#url  https://blog.csdn.net/weixin_43790276/article/details/103554632