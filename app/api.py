import functools
from io import BytesIO
from urllib.parse import quote

import xlsxwriter
from flask import Blueprint, render_template, request, jsonify, session, send_file
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash,check_password_hash
from app import db, models, service, utils
from sqlalchemy import and_,or_
from .utils import *
api = Blueprint('api',__name__)

#检查userid
def login_required(func):
    @functools.wraps(func)#修饰内层函数，防止当前装饰器去修改被装饰函数__name__的属性
    def inner(*args,**kwargs):
        userid = session.get('user_id')
        print('获取session  userid',userid)
        if not  userid:
            #api里返回错误代码而不是跳转
            return jsonRet(-2,"您还未登录,请先登录！")
        else:
            return func(*args,**kwargs)
    return inner

def admin_required(func):
    @functools.wraps(func)#修饰内层函数，防止当前装饰器去修改被装饰函数__name__的属性
    def inner(*args,**kwargs):
        userid = session.get('user_id')
        secret=session.get('secret')
        print('获取session  userid',userid)
        if userid==None or secret==None:
            #api里返回错误代码而不是跳转
            return jsonRet(-2,"您还未登录,请先登录！")
        else:
            return func(*args,**kwargs)
    return inner

@api.route('/student',methods=['GET','POST','PUT','DELETE'])
@login_required
def school_student():
    if request.method=="POST":
        student=models.Student()
        data=request.form.to_dict()
        student.name=data.get('name')
        student.sex = data.get('sex')
        student.student_number=data.get('student_number')
        student.college_name = data.get('college_name')
        student.grade = data.get('grade')
        student.class_name=data.get('class_name')
        student.school_id=session.get('school_id')
        if(service.addStudent(student)):
            return jsonRet()
        else: return jsonRet(-1,"请检查信息后再提交")
    elif request.method=="GET":
        args=request.args.to_dict()
        data=service.findStudents(session.get('school_id'),
                                  name=args.get('name'),number=args.get('student_number'),
                                  college=args.get('college_name'),grade=args.get('grade'),
                                  class_name=args.get('class_name'),sex=args.get('sex'))
        return jsonRet(data=data)
    elif request.method=="DELETE":
        id=request.form.get('id')
        if id:
            student=models.Student.query.get(id)
            db.session.delete(student)
            db.session.commit()
            return jsonRet()
        else: return jsonRet(-1,"id不存在")
    elif request.method=="PUT":
        student = models.Student()
        data = request.form.to_dict()
        student.id = data.get('id')
        student.name = data.get('name')
        student.sex = data.get('sex')
        student.student_number = data.get('student_number')
        student.college_name = data.get('college_name')
        student.grade = data.get('grade')
        student.class_name = data.get('class_name')
        student.school_id = session.get('school_id')
        if service.updateStudent(student):
            return jsonRet()
        else: return jsonRet(-1,"更新失败")
    else: return jsonRet(-1)

@api.route('/testingStudent',methods=["GET","POST"])
@login_required
def school_testingStudent():
    if request.method=="GET":
        data=request.args.to_dict()
        data=service.getMultipleStudentScore(session.get('school_id'),data.get('grade'),data.get('college_name'),data.get('student_number'),data.get('year'),data.get('name'))
        return jsonRet(data=data)
    if request.method=="POST":
        status=service.getSubmitStatus(session.get('school_id'),utils.getNowTestingYear())
        if status==1 or status==2:
            #检查今年名单是否添加
            return jsonRet(-1,"您已提交审核，不能再添加学生。")
        idsstr=request.form.get('student_ids')
        if idsstr:
            ids=idsstr.split(",")
            map(int,ids)
            ret={}
            ret['total_num']=len(ids)
            ret['success_num']=service.selectStudents(ids,getNowTestingYear())
            return jsonRet(data=ret)
        else:return jsonRet(-1,"没有找到id参数")
    else: abort(404)

#获取历史体测成绩抽取情况
@api.route('/getTestingSelectionBefore')
@login_required
def school_getTestingSelectionBefore():
    data=service.getTestingStudentSumBefore(getNowTestingYear(),session['school_id'])
    count=len(data)
    return jsonRet(data=data,count=count)

#获取每个年级的学生名册情况
@api.route('/gradeStudent',methods=["GET"])
@login_required
def school_gradeStudent():
    data=service.getStudentSums(session['school_id'])
    #加个id栏
    data=addIdColumn(data)
    count= len(data)
    return jsonRet(data=data,count=count)

#获取每个年级的学生体测情况
@api.route('/testingGradeStudent',methods=["GET"])
@login_required
def school_testingGradeStudent():
    year=getNowTestingYear()
    data=service.getTestingStudentSums(year,session['school_id'])
    #加个id栏
    count=len(data)
    return jsonRet(data=data,count=count)
@api.route('/changePassword',methods=['POST'])
@login_required
def changePassword():
    res=service.changePassword(session['user_id'],request.form.get('old_password'),request.form.get('new_password'))
    if res==True:
        service.logout()
        return jsonRet()
    else:
        return jsonRet(msg=res)

@api.route('/downloadScoreTemplate',methods=['GET'])
@login_required
def school_downloadScoreTemplate():
    school_id=session.get('school_id')
    school=models.School.query.get(school_id)
    year=getNowTestingYear()
    #获取excel要导入的所有数据
    data=service.getTemplateData(school_id,year)
    out = BytesIO()
    workbook = xlsxwriter.Workbook(out)
    table = workbook.add_worksheet()
    headstyle = workbook.add_format({
        "bold": 1,  # 字体加粗
        "align": "center",  # 对齐方式
        "valign": "vcenter",  # 字体对齐方式
    })
    datastyle = workbook.add_format({
        "align": "center",  # 对齐方式
        "valign": "vcenter",  # 字体对齐方式
    })
    #先加头部
    table.write_row("A1",data[0],cell_format=headstyle)
    #每行数据添加
    for i in range(1,len(data)):
        line=data[i]
        table.write_row('A'+str(i+1), line,cell_format=datastyle)
    workbook.close()
    #调整偏移到第一个
    out.seek(0)
    #中文正常编码
    filename = quote(school.name+".xlsx")
    rv = send_file(out, as_attachment=True, attachment_filename=filename)
    rv.headers['Content-Disposition'] += "; filename*=utf-8''{}".format(filename)
    return rv
    #参考https://www.cnblogs.com/renguiyouzhi/p/11874479.html

@api.route('/downloadStudentTemplate',methods=['GET'])
@login_required
def school_downloadStudentTemplate():
    out = BytesIO()
    workbook = xlsxwriter.Workbook(out)
    table = workbook.add_worksheet()
    headstyle = workbook.add_format({
        "bold": 1,  # 字体加粗
        "align": "center",  # 对齐方式
        "valign": "vcenter",  # 字体对齐方式
    })
    headers=['学院(系)名称','年级','专业班级','姓名','性别','学号']
    table.write_row("A1",headers,cell_format=headstyle)
    workbook.close()
    #调整偏移到第一个
    out.seek(0)
    #中文正常编码
    filename = quote("学生信息导入模板.xlsx")
    rv = send_file(out, as_attachment=True, attachment_filename=filename)
    rv.headers['Content-Disposition'] += "; filename*=utf-8''{}".format(filename)
    return rv


@api.route("/systemInit",methods=['GET'])
@login_required
def getSystemInit():
    type=request.args.get('type')
    if type=='1':
        homeInfo= {
            "title":"首页",
            "href":"/school/home"
        }
        logoInfo={
            "title":"院校端",
            "image":"/static/layuimini/images/logo.png",
            "href":""
        }
        menuInfo=__getMenuList(type)
        init={
            "homeInfo":homeInfo,
            "logoInfo":logoInfo,
            "menuInfo":menuInfo
        }
        return jsonify(init)
    elif type=='2':
        homeInfo = {
            "title": "首页",
            "href": "/province/home"
        }
        logoInfo = {
            "title": "院校端",
            "image": "/static/layuimini/images/logo.png",
            "href": ""
        }
        menuInfo = __getMenuList(type)
        init = {
            "homeInfo": homeInfo,
            "logoInfo": logoInfo,
            "menuInfo": menuInfo
        }
        return jsonify(init)
    else: return jsonRet('-1',msg="接口有误")


def __getMenuList(type):
    menu=models.Systemmenu
    menulist=menu.query.filter(and_(menu.pid==0,menu.type==type)).order_by(menu.sort).all()
    for m in menulist:
        m.child=__buildChild(m.id,type)
    return menulist

def __buildChild(pid,type):
    menu=models.Systemmenu
    childmenuns=menu.query.filter(and_(menu.pid==pid,menu.type==type)).order_by(menu.sort).all()
    if childmenuns:
        for cm in childmenuns:
            cm.child=__buildChild(cm.id,type)
        return childmenuns
    return
@api.route("/uploadStudent", methods=["POST"])
@login_required
def school_uploadStudent():
    f = request.files.get('file',None)
    if f:
        WS = pd.read_excel(f)
        data=np.array(WS).tolist()
        # 默认会去掉第一行，正好把中文头部去掉
        header=['college_name','grade','class_name','name','sex','student_number','school_id']
        school_id=session['school_id']
        for e in data:
            e.append(school_id)
            if e[4]=='男':
                e[4]=1
            else:
                e[4]=0
        count= len(data)-1
        service.quickInsert(models.Student,header,data)
        return jsonRet(msg="新增了{}个学生".format(count),code=0)
    return jsonRet(-1,msg="没有找到上传文件")


@api.route('/submitStudent',methods=['POST'])
@login_required
def school_submitStudent():
    year=getNowTestingYear()
    schoolid=session['school_id']
    comment=request.form.get('comment')
    if comment == None:
        comment = ""
    #先查看是否有之前的提交记录
    StudentSelection=models.StudentSelection
    studentSelection=StudentSelection.query.filter(StudentSelection.year==year,StudentSelection.school_id==schoolid).first()
    if studentSelection:
        studentSelection.submit_comment=comment
        studentSelection.submit=1
        studentSelection.confirm = 0
        db.session.commit()
        return jsonRet()
    else:
        #否则新建一个提交
        service.createSubmitStudent(schoolid,year,comment)
        return jsonRet()

@api.route('/schoolTotalScore',methods=['GET'])
def school_schoolTotalScore():
    year=request.args.get('year')
    school_id=session['school_id']
    if year:
        type=models.School.query.get(school_id).type
        alldata=service.getTotalScoreRank(year,type)
        for e in alldata:
            if e.school_id==school_id:
                return jsonRet(data=[e])
        return jsonRet(-1,"未找到该校数据")
    else:
        return jsonRet(-1,"参数不全")

@api.route('/schoolDetailScore',methods=['GET'])
def school_schoolDetailScore():
    year=request.args.get('year')
    school_id=session['school_id']
    if year:
        type = models.School.query.get(school_id).type
        ret=[]
        #男生项目女生项目分开处理
        boy_projects=service.getSelectProjects(year,1)
        for e in boy_projects:
            #拿到基于schoolscoredetail的obj
            alldata=service.getProjectRank(e.name,year,type,1)
            for each in alldata:
                if each.school_id==school_id:
                    each.project_name=e.name+"(男)"
                    ret.append(each)
                    break

        girl_projects=service.getSelectProjects(year,0)
        for e in girl_projects:
            #拿到基于schoolscoredetail的obj
            alldata=service.getProjectRank(e.name,year,type,0)
            if alldata:
                for each in alldata:
                    if each.school_id==school_id:
                        each.project_name=e.name+ "(女)"
                        ret.append(each)
                        break
        ret=utils.addIdColumn(ret,obj=True)
        return jsonRet(data=ret)
    else:
        return jsonRet(-1,"参数不全")
#************************分割线************************

@api.route('/downloadSchoolTemplate',methods=['GET'])
@admin_required
def school_downloadSchoolTemplate():
    out = BytesIO()
    workbook = xlsxwriter.Workbook(out)
    table = workbook.add_worksheet()
    headstyle = workbook.add_format({
        "bold": 1,  # 字体加粗
        "align": "center",  # 对齐方式
        "valign": "vcenter",  # 字体对齐方式
    })
    headers=['学校姓名','学校代码','学校类比']
    table.write_row("A1",headers,cell_format=headstyle)
    workbook.close()
    #调整偏移到第一个
    out.seek(0)
    #中文正常编码
    filename = quote("学校信息导入模板.xlsx")
    rv = send_file(out, as_attachment=True, attachment_filename=filename)
    rv.headers['Content-Disposition'] += "; filename*=utf-8''{}".format(filename)
    return rv

@api.route("/uploadSchool", methods=["POST"])
@admin_required
def province_uploadSchool():
    f = request.files.get('file',None)
    if f:
        WS = pd.read_excel(f)
        #默认会去掉第一行，正好把中文头部去掉
        data=np.array(WS).tolist()
        header=['name','code','type']
        count= len(data)-1
        service.quickInsert(models.School,header,data)
        return jsonRet(msg="新增了{}个学校".format(count))
    return jsonRet(-1,msg="没有找到上传文件")

@api.route('/school',methods=['GET','POST','PUT','DELETE'])
@admin_required
def province_shcool():
    #查询单个
    if request.method=='GET':
        id=request.args.get('id')
        if id:
            school=models.School.query.get(id)
            return jsonRet(data=school)
        else:return jsonRet(code=-1,msg="没有id值")
    #添加一个
    elif request.method=='POST':
        name=request.form.get('name')
        code=request.form.get('code')
        type=request.form.get('type')
        school=models.School()
        if name and code and type:
            school.name=name
            school.code=code
            school.type=type
            db.session.add(school)
            db.session.commit()
            return jsonRet()
        else: return jsonRet(-1,"参数不全")
    #更新一个
    elif request.method=='PUT':
        #认为所有的都会发上来
        name = request.form.get('name')
        code = request.form.get('code')
        type = request.form.get('type')
        id = request.form.get('id')
        if id and name and code and type:
            school = models.School.query.get(id)
            school.name = name
            school.code = code
            school.type = type
            db.session.commit()
            return jsonRet()
        else:
            return jsonRet(-1, "参数不全")
    #删除一个
    elif request.method=='DELETE':
        id=request.args.get('id')
        if id:
            school=models.School.query.get(id)
            db.session.delete(school)
            db.session.commit()
            return jsonRet()
        else: return jsonRet(-1,"id值未得到")

@api.route('/schoolList')
@admin_required
def province_schoolList():
    name=request.args.get('name')
    code=request.args.get('code')
    res=service.findSchool(name,code)
    return jsonRet(data=res)

@api.route('/account',methods=['GET','POST','DELETE','PUT'])
@admin_required
def province_account():
    if request.method=='GET':
        # 获取账号列表
        school_name=request.args.get('name')
        if school_name:
            school=models.School.query.filter(models.School.name==school_name).first()
            if school:
                accounts=models.Account.query.filter(models.Account.school_id==school.id,models.Account.type==1).all()
                for e in accounts:
                    #school_name也要拼上去
                    e.name = school_name
                return jsonRet(data=accounts)
            else: return jsonRet(-1,"学校未找到")
        else:
            #不传学校就返回所有账户
            accounts = models.Account.query.filter(models.Account.type==1).all()
            for e in accounts:
                school=models.School.query.get(e.school_id)
                e.name=school.name
            return jsonRet(data=accounts)
    elif request.method=='POST':
        school_name=request.form.get('school_name')
        username=request.form.get('username')
        password=request.form.get('password')
        if school_name and username and password:
            school=models.School.query.filter(models.School.name==school_name).first()
            if school:
                account=models.Account()
                account.school_id=school.id
                account.username=username
                #密码hash处理
                account.password=generate_password_hash(password)
                #类型为学校账户
                account.type=1
                db.session.add(account)
                db.session.commit()
                return jsonRet()
            else:
                return jsonRet(-1, "学校未找到")
        else:return jsonRet(-1,"参数缺失")
    elif request.method=='PUT':
        id=request.form.get('id')
        password=request.form.get('password')
        if id and password:
            account=models.Account.query.get(id)
            account.password=generate_password_hash(password)
            db.session.commit()
            return jsonRet()
        else:return jsonRet(-1,"参数不全")
    elif request.method=='DELETE':
        id=request.args.get('id')
        if id:
            account=models.Account.query.get(id)
            db.session.delete(account)
            db.session.commit()
            return jsonRet()
        else:return jsonRet(-1,"id参数未找到")

@api.route('/getCheckList',methods=['GET'])
@admin_required
def province_getCheckList():
    year = utils.getNowTestingYear()
    res = models.StudentSelection.query.filter(models.StudentSelection.year == year,
                                               models.StudentSelection.submit == 1,
                                               models.StudentSelection.confirm != 1).all()
    data = []
    for e in res:
        temp = {}
        temp['id'] = e.id
        temp['total_num'] = e.boy + e.girl
        temp['update_time'] = e.update_time.strftime('%Y-%m-%d %H:%M:%S')
        school = models.School.query.get(e.school_id)
        temp['name'] = school.name
        data.append(temp)
    return jsonRet(data=data)

@api.route('/getTestingStudent',methods=['GET'])
@admin_required
def province_getTestingStudent():
    id=request.args.get('id')
    if id:
        studentSelection=models.StudentSelection.query.get(id)
        year=studentSelection.year
        school_id=studentSelection.school_id
        res=service.getTestingStudent(school_id,year)
        return jsonRet(data=res)
    else:return jsonRet(-1,"id未找到")

@api.route('/checkTestingStudent',methods=['POST'])
@admin_required
def province_checkTestingStudent():
    id=request.form.get('id')
    status=request.form.get('status')
    if id and status!=None:
        status=int(status)
        studentSelection=models.StudentSelection.query.get(id)
        if status==0:
            studentSelection.submit=0
            studentSelection.confirm=0
            db.session.commit()
        else:
            studentSelection.submit = 1
            studentSelection.confirm = 1
            db.session.commit()
        return jsonRet()
    else:return jsonRet(-1,"参数不全")

@api.route('/project',methods=['GET','POST'])
@admin_required
def province_project():
    if request.method=="GET":
        data=models.TestingProject.query.all()
        return jsonRet(data=data)
    elif request.method=="POST":
        form=request.form.to_dict()
        project=models.TestingProject()
        project.name=form.get('name')
        project.sex=int(form.get('sex'))
        project.weight=float(form.get('weight'))
        project.scoreType=int(form.get('scoreType'))
        if form.get('comment'):
            project.comment=form.get('comment')
        db.session.add(project)
        db.session.commit()
        return jsonRet()

@api.route('/standard',methods=['GET','POST','PUT','DELETE'])
@admin_required
def province_standard():
    if request.method=="GET":
        id = request.args.get('id')
        level = request.args.get('level')
        if id != None and level != None:
            standards=models.TestingProject.query.get(id).standards
            level=int(level)
            ret=[]
            for e in standards:
                if e.level==level:
                    ret.append(e)
            return jsonRet(data=ret)
        else: return jsonRet(-1,"参数确实")
    elif request.method=='PUT':
        data=request.form.to_dict()
        id=data.get('id')
        if id:
            standard=models.TestingStandard.query.get(id)
            standard.name=data.get('name')
            standard.score=data.get('score')
            standard.comment=data.get('comment',"")
            standard.bottom=data.get('bottom')
            standard.top=data.get('top')
            db.session.commit()
            return jsonRet()
        else:return jsonRet(-1,"id缺失")
    elif request.method=='POST':
        data = request.form.to_dict()
        standard = models.TestingStandard()
        standard.name = data.get('name')
        standard.score = data.get('score')
        standard.comment = data.get('comment', "")
        standard.bottom = data.get('bottom')
        standard.top = data.get('top')
        standard.level=data.get('level')
        standard.project_id=data.get('project_id')
        db.session.add(standard)
        db.session.commit()
        return jsonRet()

    elif request.method=='DELETE':
        id=request.args.get('id')
        if id:
            standard=models.TestingStandard.query.get(id)
            db.session.delete(standard)
            db.session.commit()
            return jsonRet()
        else:return jsonRet(-1,"id缺失")
    else: return jsonRet(-1)

@api.route('projectselection',methods=['GET','PUT'])
@admin_required
def province_projectselection():
    if request.method=='GET':
        year=utils.getNowTestingYear()
        sex=request.args.get('sex')
        if sex:
            sex=int(sex)
            selected=service.getSelectProjects(year, sex)
            all=models.TestingProject.query.filter(models.TestingProject.sex==sex).all()
            #转换格式
            ret={}
            #data列表是左边，value是右边
            ret['data']=[]
            ret['value']=[]
            for e in all:
                temp = {}
                temp['value'] = e.id
                temp['title'] = e.name
                ret['data'].append(temp)
                for i in selected:
                    if e.id==i.id:
                        #说明这个选了
                        ret['value'].append(e.id)
                        break
            return jsonRet(data=ret)
        else:
            return jsonRet(-1, "sex参数缺失")

@api.route('/historyProjectList',methods=['GET'])
@admin_required
def province_historyProject():
    #先查出来都有哪些年
    res=models.ProjectSelection.query.with_entities(models.ProjectSelection.year).distinct().order_by(models.ProjectSelection.year.desc()).all()
    ret=[]
    for e in res:
        year=e[0]
        temp={}
        temp['boy']=len(service.getSelectProjects(year, 1))
        temp['girl']=len(service.getSelectProjects(year, 0))
        temp['year']=year
        ret.append(temp)
    #每列加个id
    ret=utils.addIdColumn(ret)
    return jsonRet(data=ret)

#传入ids，逗号间隔的数组，男生女生加起来的今年的项目列表
@api.route('/selectProject',methods=['POST'])
@admin_required
def province_selectProject():
    idsstr=request.form.get('ids')
    #避免""的直接过不去
    if idsstr!=None:
        if idsstr=="":
            ids=[]
        else:
            ids = idsstr.split(",")
            map(int, ids)
        service.selectProject(ids,getNowTestingYear())
        return jsonRet()
    else:return jsonRet(-1,'参数不存在')

@api.route('/uploadScore',methods=['POST'])
@admin_required
def province_uploadScore():
    f = request.files.get('file', None)
    if f:
        #None表示没有列头，第一行就是数据，所以不会跳过第一行
        WS = pd.read_excel(f,header=None)
        data = np.array(WS).tolist()
        count=len(data)-1
        # 保留第一行，为了匹配到项目
        school_id = service.checkScoreExcel(data)
        if school_id==False:
            return jsonRet(-1,"成绩模板数据有误")
        year=getNowTestingYear()
        service.importScores(data,school_id,year)
        return jsonRet(msg="新增了{}个成绩".format(count), code=0)
    return jsonRet(-1, msg="没有找到上传文件")

@api.route('/calculateSchool',methods=['POST'])
@admin_required
def province_calculateSchool():
    year=getNowTestingYear()
    try:
        service.calculateSchoolScore(year)
        return jsonRet()
    except:
        return jsonRet(-1,"系统错误")


@api.route('/calculateStudent',methods=['POST'])
@admin_required
def province_calculateStudent():
    year = getNowTestingYear()
    try:
        service.calculateStudentScore(year)
        return jsonRet()
    except:
        return jsonRet(-1, "系统错误")

@api.route('/calculateAll',methods=['POST'])
@admin_required
def province_calculateAll():
    year = getNowTestingYear()
    try:
        service.calculateStudentScore(year)
        service.calculateSchoolScore(year)
        return jsonRet()
    except:
        return jsonRet(-1, "系统错误")


@api.route('/projectRank',methods=['GET'])
def province_projectRank():
    data=request.args.to_dict()
    year=data.get('year')
    school_type=data.get('school_type')
    project=data.get('project')
    sex=data.get('sex')
    if year and school_type and project and sex:
        #默认按照分数排名
        #如果sex为all说明为全都要
        res=service.getProjectRank(project,year,school_type,sex)
        if res==False:
            return jsonRet(-1,"参数有误")
        else:
            #把id修正一遍
            res=utils.addIdColumn(res,obj=True)
            return jsonRet(data=res)
    else:
        return jsonRet(-1,"参数缺失")

@api.route('/schoolRank',methods=['GET'])
def province_schoolRank():
    data=request.args.to_dict()
    year=data.get('year')
    school_type=data.get('school_type')
    type=data.get('type')
    if year and school_type and type:
        if type == "score":
            title=[
                {"field": 'excellent_rate', "title": '优秀率', "sort": "true"},
                {"field": 'excellent_rank', "title": '优秀率排名'},
				{"field": 'good_rate', "title": '优良率', "sort": "true"},
				{"field": 'good_rank', "title": '优良率排名'},
				{"field": 'pass_rate', "title": '及格率', "sort": "true"},
				{"field": 'pass_rank', "title": '及格率排名'},
                ]
            res=service.getTotalScoreRank(year,school_type)
            if res==False:
                #说明没找到
                return jsonRet(-1,"参数有误")
            res=utils.addIdColumn(res,obj=True)
            return jsonRet(data={"title":title,"data":res})
        else:
            #剩下情况为查看大type的各项指标
            level=int(type)
            title = [
                {"field": 'pass_rate', "title": '及格率', "sort": "true"},
                {"field": 'good_rate', "title": '优良率', "sort": "true"},
                {"field": 'excellent_rate', "title": '优秀率', "sort": "true"},
            ]
            data,projects=service.getDetailScoreRank(year,school_type,level)
            if data:
                #此时已经加过id和排序了
                for e in projects:
                    title.append({"field":e.id,"title":e.name, "sort": "true"})
                return jsonRet(data={"data":data,"title":title})
            else:return jsonRet(-1,"参数有误")
    else:
        return jsonRet(-1,"参数缺失")