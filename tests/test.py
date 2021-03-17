from app import *
from app.models import *
from app import models
from sqlalchemy import and_,or_
from app.service import *
# account=Account()
# account.username='fay'
# account.password='psw'
# account.type=1
# db.session.add(account)
# db.session.commit()
# a=Account.query.filter(and_(Account.username=='fay',Account.password=='psw')).first()
# print(a.username)

# from app import utils
# a=utils.excelToMatrix("1.xlsx")
# print(a[0][1])

# ret=db.session.execute("SELECT s.sex,COUNT(s.sex) FROM student s WHERE grade='{}' GROUP BY s.sex ".format("2018级"))
# l=list(ret)
# print(l)
# ret=Student.query.with_entities(Student.grade).distinct().all()
# print(ret)
# print(ret[1])
# print(ret[1][0])

# print(data)

# page=1
# pn=Student.query.paginate(page,per_page=3)
# print(pn.items)
# for e in pn.items:
#     print(e.name)
# from flask.json import JSONEncoder, jsonify
# app_ctx = app.app_context()
# app_ctx.push()
#
# class Ha():
#     name=1
#     sex=1
#     def serializable(self):
#         return self.name,self.sex
# a=Ha()

# a=db.session.execute("insert into school (name) values('1') ")
# print(a)

#tstudents=TestingStudent.query.filter(TestingStudent.year==2020,TestingStudent.school_id==1).all()
#print(tstudents)
#calculateSchoolScoreNumber(2020)
