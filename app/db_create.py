from app import db
db.create_all()

addMune=False
if addMune:
    from app.models import Systemmenu
    menu={
      "title": "体测管理",
      "icon": "fa fa-address-book",
      "href": "",
      "target": "_self",
      "child": [
        {
          "title": "主页",
          "href": "page_raw/welcome-1.html",
          "icon": "fa fa-home",
          "target": "_self"
        },
        {
          "title": "学生名册导入",
          "href": "page/uploadStudent.html",
          "icon": "fa fa-window-maximize",
          "target": "_self"
        },
        {
          "title": "体测学生抽取",
          "href": "page/selectStudent.html",
          "icon": "fa fa-gears",
          "target": "_self"
        },
        {
          "title": "学生成绩查询",
          "href": "page/studentScore.html",
          "icon": "fa fa-file-text",
          "target": "_self"
        },
        {
          "title": "学生成绩排名",
          "href": "page/schoolScore.html",
          "icon": "fa fa-calendar",
          "target": "_self"
        },
        {
          "title": "测试页面",
          "href": "/school/index",
          "icon": "fa fa-calendar",
          "target": "_self"
        }
      ]
    }
    m1=Systemmenu()
    m1.id=1
    m1.title=menu['title']
    m1.type=1
    m1.icon=menu['icon']
    m1.href=menu['href']
    db.session.add(m1)
    th=1
    for child in menu['child']:
        mn=Systemmenu()
        mn.pid=1
        mn.title = child['title']
        mn.type = 1
        mn.icon = child['icon']
        mn.href = child['href']
        mn.sort=th
        th=th+1
        db.session.add(mn)
    db.session.commit()