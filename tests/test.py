from app import *
from app.models import *
from app import models
from sqlalchemy import and_,or_
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

service.importStudent('student.xlsx',1)