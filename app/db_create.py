from app import db


addMune=True
if addMune:
    db.create_all()
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
    menu2=[
    {
      "title": "学校管理",
      "icon": "fa fa-address-book",
      "href": "",
      "target": "_self",
      "child": [
        {
          "title": "主页模板",
          "href": "row_page/welcome-1.html",
          "icon": "fa fa-home",
          "target": "_self"
        },
        {
          "title": "批量导入",
          "href": "page/uploadSchool.html",
          "icon": "fa fa-window-maximize",
          "target": "_self"
        },
        {
          "title": "所有院校",
          "href": "page/school.html",
          "icon": "fa fa-gears",
          "target": "_self"
        },
        {
          "title": "院校管理员",
          "href": "page/schoolAccount.html",
          "icon": "fa fa-file-text",
          "target": "_self"
        }
      ]
    },
    {
      "title": "体测管理",
      "icon": "fa fa-lemon-o",
      "href": "",
      "target": "_self",
      "child": [
        {
          "title": "确认名单",
          "href": "page/checkList.html",
          "icon": "fa fa-dot-circle-o",
          "target": "_self"
        },
        {
          "title": "体测项目管理",
          "href": "page/testingProject.html",
          "icon": "fa fa-adn",
          "target": "_self"
        },
        {
          "title": "体测项目选择",
          "href": "page/selectProject.html",
          "icon": "fa fa-angle-double-down",
          "target": "_self"
        }
      ]
    },
    {
      "title": "成绩统计",
      "icon": "fa fa-slideshare",
      "href": "",
      "target": "_self",
      "child": [
        {
          "title": "原始数据导入",
          "href": "page/uploadScore.html",
          "icon": "fa fa-meetup",
          "target": ""
        },
        {
          "title": "学校单项排名情况",
          "href": "page/projectRank.html",
          "icon": "fa fa-superpowers",
          "target": "_self"
        },
		{
		  "title": "学校总体排名情况",
		  "href": "page/schoolRank.html",
		  "icon": "fa fa-superpowers",
		  "target": "_self"
		}
      ]
    }
]
    # m1=Systemmenu()
    # m1.id=1
    # m1.title=menu['title']
    # m1.type=1
    # m1.icon=menu['icon']
    # m1.href=menu['href']
    # db.session.add(m1)
    # th=1
    # for child in menu['child']:
    #     mn=Systemmenu()
    #     mn.pid=1
    #     mn.title = child['title']
    #     mn.type = 1
    #     mn.icon = child['icon']
    #     mn.href = child['href']
    #     mn.sort=th
    #     th=th+1
    #     db.session.add(mn)
    # db.session.commit()
    td=7
    for e in menu2:
        m2=Systemmenu()
        m2.title=e['title']
        m2.type=2
        m2.pid=0
        m2.icon=e['icon']
        m2.href=e['href']
        m2.sort=0
        db.session.add(m2)
        ti=1
        for child in e['child']:
            mn=Systemmenu()
            mn.pid=td
            mn.title = child['title']
            mn.type = 2
            mn.icon = child['icon']
            mn.href = child['href']
            mn.sort=ti
            ti=ti+1
            db.session.add(mn)
            td=td+1
        td=td+1
    db.session.commit()