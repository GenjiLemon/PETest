from flask import Blueprint,render_template, request,jsonify
from app import db,models
from sqlalchemy import and_,or_
api = Blueprint('api',__name__)

@api.route("/systemInit",methods=['GET'])
def getSystemInit(type=1):
    if type==1:
        homeInfo= {
            "title":"首页",
            "href":"/school/home"
        }
        logoInfo={
            "title":"院校端",
            "icon":"/static/school/images/logo.png"
        }
        menuInfo=__getMenuList(type)
        init={
            "homeInfo":homeInfo,
            "logoInfo":logoInfo,
            "menuInfo":[topMenu.serialize() for topMenu in menuInfo]
        }
        return init
        #return jsonify(init)

def __getMenuList(type):
    menu=models.Systemmenu
    menulist=menu.query.filter(and_(menu.pid==0,menu.type==type)).order_by(menu.sort).all()
    for m in menulist:
        m.child=__buildChild(m.id,type)
    return menulist

def __buildChild(pid,type):
    menu=models.Systemmenu
    print(pid)
    childmenuns=menu.query.filter(and_(menu.pid==pid,menu.type==type)).order_by(menu.sort).all()
    if childmenuns:
        for cm in childmenuns:
            cm.child=__buildChild(cm.id,type)
        return childmenuns
    return

@api.route('/grade-student')
def gradelist():
    return {
        "code": 0,
        "msg": "",
        "count": 1000,
        "data": [
            {
                "id": 1,
                "year": 2020,
                "total_num": 100,
                "boy_num": 30,
                "girl_num": 70
            },
            {
                "id": 2,
                "year": 2019,
                "total_num": 200,
                "boy_num": 130,
                "girl_num": 70
            }
        ]
    }

@api.route('/student-list')
def studentlist():
    return {
  "code": 0,
  "msg": "",
  "count": 1000,
  "data": [
    {
      "id": 1,
      "college_name":"物理学院",
	  "grade":2020,
	  "class_name":"物理学",
	  "name":"小明",
	  "sex":"男",
	  "student_number":"20202020202020",
	  "comment":"备注"
    },
    {"id": 2,
      "college_name":"数学学院",
      "grade":2020,
      "class_name":"数学应用数学",
      "name":"小红",
      "sex":"女",
      "student_number":"20202020202021",
      "comment":"备注"
    }
  ]
}