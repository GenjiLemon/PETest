from app import db,models
User=models.User
# u=User()
# u.username="fay"
# u.email="fay@fay.com"
# u.password="fay"
u=User(password="1",username="1")
print(u)
db.session.add(u)
db.session.commit()
