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
# data=service.getStudentSums()
# print(data)
# ret=db.session.execute("SELECT s.sex,COUNT(s.sex) FROM student s WHERE grade='{}' GROUP BY s.sex ".format("2020级"))
# l=list(ret)
# print(l)
page=1
pn=Student.query.paginate(page,per_page=3)
print(pn)