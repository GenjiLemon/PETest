#此文件为中间服务类
from io import BytesIO
from urllib.parse import quote

import xlsxwriter
from flask import session, send_file
from sqlalchemy import desc
from werkzeug.security import generate_password_hash,check_password_hash
from app import db,app
from app.models import *
from . import utils
import os

from .utils import gradeToInt


#**************账户begin**************
#登录
#返回账户类型，1学校，2省厅，0错误


def login(username,password):
    # account=Account.query.filter_by(username=username).
    pass
def logout():
    session.pop('user_id')
    if session.get('secret')!=None:
        #判断是院校还是省厅
        session.pop('secret')
    else:
        session.pop('school_id')
#创建学校账户
def createAccount(username,password,schoolid):
    pass

#根据账户名更换密码
def changePassword(user_id,old_password,new_password):
    user=Account.query.get(user_id)
    if user:
        if check_password_hash(user.password,old_password):
            user.password=generate_password_hash(new_password)
            db.session.commit()
            return True
        else: return "旧密码错误!"
    else:
        return "用户未找到！"
#**************账户end**************


#**************省厅begin**************


#通过code或者name找学校
def findSchool(name=None,code=None):
    filter_list = []
    if name and name!='':
        filter_list.append(School.name == name)
    if code and code!='':
        filter_list.append(School.code == code)
    return School.query.filter(*filter_list).all()

#获取审核名单
def getTestingStudent(school_id,year):
    testingStudents=TestingStudent.query.filter(TestingStudent.school_id==school_id,TestingStudent.year==year).all()
    res=[]
    for e in testingStudents:
        student=Student.query.get(e.student_id)
        student.comment=e.comment
        res.append(student)
    return res

#选择项目
#传入id的list
def selectProject(projectids,year):
    old=ProjectSelection.query.filter(ProjectSelection.year==year).all()
    #求出原来的id列表
    oldids=[]
    # 先处理删除的
    for e in old:
        oldids.append(e.project_id)
        if e.project_id not in projectids:
            db.session.delete(e)
    #再处理添加的
    for e in projectids:
        if e not in oldids:
            temp=ProjectSelection()
            temp.year=year
            temp.project_id=e
            db.session.add(temp)
    db.session.commit()

#获取选择的项目
def getSelectProjects(year,sex):
    res = ProjectSelection.query.filter(ProjectSelection.year == year).order_by(ProjectSelection.project_id).all()
    ret=[]
    for e in res:
        project=TestingProject.query.get(e.project_id)
        if project.sex==sex:
            ret.append(project)
    return ret
#删除选择的项目

#检查文件是否符合要求，目前只检查头
#正常返回school id 不对就返回False
def checkScoreExcel(data):
    template=getTemplateData(-1,utils.getNowTestingYear())
    if data[0][:len(template[0])]==template[0]:
        school_name=data[1][1]
        school=School.query.filter(School.name==school_name).first()
        if school:
            return school.id
    return False

#成绩导入
def importScores(excel_data,school_id,year):
    excel_header=excel_data[0]
    #先获取row_data对应的列、projectid
    boyProjects=getSelectProjects(year,1)
    #男生女生 对应的项目id 列序号 用于之后直接导入
    boys=[]
    girlProjects=getSelectProjects(year,0)
    girls=[]
    for i in range(5,len(excel_header)):
        name=utils.getProjectName(excel_header[i])
        for e in boyProjects:
            if name==e.name:
                boys.append({"id":e.id,"index":i})
        for e in girlProjects:
            if name==e.name:
                girls.append({"id":e.id,"index":i})
    data=excel_data[1:]
    columns=['row_data','project_id','tstudent_id','school_id']
    values=[]
    for eachline in data:
        student=Student.query.filter(Student.school_id==school_id,Student.student_number==eachline[4]).first()
        tstudent=TestingStudent.query.filter(TestingStudent.student_id==student.id).first()
        if student.sex==1:
            #处理每个性别，把所有的id rowdata放进去
            for e in boys:
                #这里的e是每个项目，是个dict 拥有id(project_id)和index
                temp=[]
                #依次放入rowdata project_id tstudent_id school_id
                temp.append(eachline[e['index']])
                temp.append(e['id'])
                temp.append(tstudent.id)
                temp.append(school_id)
                values.append(temp)
        elif student.sex==0:
            for e in girls:
                #这里的e是每个项目，是个dict 拥有id(project_id)和index
                temp=[]
                #依次放入rowdata project_id student_id school_id
                temp.append(eachline[e['index']])
                temp.append(e['id'])
                temp.append(tstudent.id)
                temp.append(school_id)
                values.append(temp)
    quickInsert(TestingScore,columns,values)
    return

def getProjectRank(project_name,year,school_type,sex):
    #数据查出来，插入排名字段，再返回
    #按照成绩排名降序
    #找到参加体测的所有学校
    schoolids=getTestingSchoolids(year,school_type)
    if schoolids==[]:
        return False
    if sex=="all":
        #处理性别全部的情况
        # 先找这个项目是否存在，拿到id
        boy = TestingProject.query.filter(TestingProject.name == project_name, TestingProject.sex == 1).first()
        girl=TestingProject.query.filter(TestingProject.name == project_name, TestingProject.sex == 0).first()
        if boy!=None and girl !=None:
            # 先找到boy，然后每个对应的girl找到，加到girl上，最后再返回
            boyScoreDetails = SchoolScoreDetail.query.filter(SchoolScoreDetail.year == year,
                                                  SchoolScoreDetail.project_id == boy.id,
                                                  SchoolScoreDetail.school_id.in_(schoolids)).all()
            for e in boyScoreDetails:
                school=School.query.get(e.school_id)
                schoolScore=SchoolScore.query.filter(SchoolScore.school_id==e.school_id).first()
                boy_num=schoolScore.boy_number
                girl_num=schoolScore.girl_number
                total_num=boy_num+girl_num
                girlScoreDetail=SchoolScoreDetail.query.filter(SchoolScoreDetail.year == year,
                                                  SchoolScoreDetail.project_id == girl.id,
                                                  SchoolScoreDetail.school_id==e.school_id).first()
                e.score=round((e.score*boy_num+girlScoreDetail.score*girl_num)/total_num,2)
                e.excellent_rate=round((e.excellent_rate*boy_num+girlScoreDetail.excellent_rate*girl_num)/total_num,4)
                e.good_rate=round((e.good_rate*boy_num+girlScoreDetail.good_rate*girl_num)/total_num,4)
                e.pass_rate=round((e.pass_rate*boy_num+girlScoreDetail.pass_rate*girl_num)/total_num,4)
            #都加到boy上，boy就是女生加男生共同的ScoreDetails
            #但是要重新排序一下score
            boyScoreDetails.sort(key=lambda x: x.score, reverse=True)
            ret = __addRankandName(boyScoreDetails)
            return ret
        else:
            return getProjectRank(project_name,year,school_type,1 if boy else 0)
    else:
        #先找这个项目是否存在，拿到id
        project=TestingProject.query.filter(TestingProject.name==project_name,TestingProject.sex==sex).first()
        if project:
            #找到这个项目指定年下的所有学校的成绩，进行排序
            data = SchoolScoreDetail.query.filter(SchoolScoreDetail.year == year,
                                                  SchoolScoreDetail.project_id == project.id,
                                                  SchoolScoreDetail.school_id.in_(schoolids)).order_by(
                desc(SchoolScoreDetail.score)).all()
            ret=__addRankandName(data)
            return ret
    return False

#传入schoolscore或者schoolscoredetail的list
#添加score_rank excellent_rank good_rank pass_rank后返回
def __addRankandName(schoolScoreDetails):
    if not schoolScoreDetails:
        #判断空和None
        return []
    #先把各种list填充
    score_list=[]
    excellent_rate_list=[]
    good_rank_list=[]
    pass_rank_list=[]
    for e in schoolScoreDetails:
        score_list.append(e.score)
        excellent_rate_list.append(e.excellent_rate)
        good_rank_list.append(e.good_rate)
        pass_rank_list.append(e.pass_rate)
    #计算各个list的orderlist
    scoreOrder=utils.getOrderList(score_list)
    excellentOrder=utils.getOrderList(excellent_rate_list)
    goodOrder=utils.getOrderList(good_rank_list)
    passOrder=utils.getOrderList(pass_rank_list)
    #循环 把每个order填进去
    #再把school_name放进去
    for i in range(0,len(schoolScoreDetails)):
        e=schoolScoreDetails[i]
        e.school_name=School.query.get(e.school_id).name
        e.score_rank=scoreOrder[i]
        e.excellent_rank=excellentOrder[i]
        e.good_rank=goodOrder[i]
        e.pass_rank=passOrder[i]
    return schoolScoreDetails

#获取今年参与体测的学校ids，根据上传的名单来判断
#分为本科和高职高专
def getTestingSchoolids(year,school_type:str):
    if school_type not in ['本科','高职高专']:
        #不时这两类直接返回
        return []
    res=StudentSelection.query.filter(StudentSelection.year==year).all()
    ret=[]
    for e in res:
        school=School.query.get(e.school_id)
        if school.type==school_type:
            ret.append(school.id)
    return ret

#获取学校总分的排名，各项率和排名
def getTotalScoreRank(year,school_type):
    # 找到参加体测的所有学校ids
    schoolids = getTestingSchoolids(year, school_type)
    schoolScores=SchoolScore.query.filter(SchoolScore.school_id.in_(schoolids)).order_by(desc(SchoolScore.score)).all()
    if schoolScores:
        ret=__addRankandName(schoolScores)
        return ret
    return False

def getDetailScoreRank(year,school_type,level):
    #先查到所有学校
    schoolids=getTestingSchoolids(year,school_type)
    ret=[]
    projects=getYearAllProject(year)
    #给出projectid和返回的id的对应关系projectsMap 单性别一样，双性别的女生也指向男生这里
    projectsMap={}
    for e in projects:
        projectsMap[e.id]=e.id
        id=getSisterProjectId(e,year)
        #如果发现同名女项目，把id也指过来
        if id:
            projectsMap[id]=e.id
    #学校遍历
    for school_id in schoolids:
        res=getSchoolLevelScore(year,school_id,level,projectsMap)
        if res:
            # 这里需要把dict里的key都换成str
            #school_name扔进去
            res['school_name']=School.query.get(school_id).name
            ret.append(utils.strDictKey(res))
    #排序，加id
    ret.sort(key=lambda x:x['excellent_rate'],reverse=True)
    ret=utils.addIdColumn(ret)
    return ret,projects

def getSisterProjectId(boyProject,year):
    girls = getSelectProjects(year, 0)
    for p in girls:
        if boyProject.name == p.name and boyProject.weight == p.weight and boyProject.scoreType == p.scoreType:
            # 三者都相同认为是同一个项目只有性别不同
            return p.id
    return None

def getSchoolLevelScore(year,school_id,level,projectsMap):
    #返回dict:pass_rate,good..,exc...,score,2,4,5,4...(项目id，默认男）
    #开始时对应的项目id放的是list，后来放平均值
    ret={}
    for i in set(projectsMap.keys()):
        ret[i]=[]
    #根据学校id找出所有今年体测的level的学生tstudents，
    tstudents=TestingStudent.query.filter(TestingStudent.school_id==school_id,TestingStudent.level==level,TestingStudent.year==year).all()
    #遍历tstudents得到score，各种rate
    scorelist=[]
    tstudentsids=[]
    for e in tstudents:
        scorelist.append(e.score)
        tstudentsids.append(e.id)
    #计算各种率
    ret['score'],ret['excellent_rate'],ret['good_rate'],ret['pass_rate']=utils.calculateScorelist(scorelist)
    #根据学校id和tstudentsid找出所有testingsscores
    testScorelist=TestingScore.query.filter(TestingScore.school_id==school_id,TestingScore.tstudent_id.in_(tstudentsids)).all()
    #遍历testingscores 得到projectid和score的对应
    for testingscore in testScorelist:
        # 把每个projectid映射为最终返回的projectid，成绩填数组里，
        ret[projectsMap[testingscore.project_id]].append(testingscore.score)
    #把数组都求平均值
    for i in set(projectsMap.keys()):
        if len(ret[i])==0:
            ret[i]=0
        else:
            ret[i]=utils.calculateScorelist(ret[i],averageOnly=True)
    return ret
#极少情况
#根据项目名，获取这个学校今年的这个项目平均分
def getSchoolProjectScoreByName(school_id,project_name,year):
    #先查一下这个projectname有几个project
    projects=TestingProject.query.filter(TestingProject.name==project_name).all()
    if not projects:
        return False
    if len(projects)==1:
        res=SchoolScoreDetail.query.filter(SchoolScoreDetail.year==year,SchoolScoreDetail.project_id==projects[0].id,SchoolScoreDetail.school_id==school_id).first().score
        return res if res else False
    elif len(projects)==2:
        scoreScore = SchoolScore.query.filter(SchoolScore.school_id == school_id, SchoolScore.year == year).first()
        boy_num = scoreScore.boy_number
        girl_num = scoreScore.girl_number
        total_number=boy_num+girl_num
        if projects[0].sex==1:
            boy = SchoolScoreDetail.query.filter(SchoolScoreDetail.year == year,
                                                 SchoolScoreDetail.project_id == projects[0].id,
                                                 SchoolScoreDetail.school_id == school_id).first()
            girl = SchoolScoreDetail.query.filter(SchoolScoreDetail.year == year,
                                                  SchoolScoreDetail.project_id == projects[1].id,
                                                  SchoolScoreDetail.school_id == school_id).first()
        else:
            boy = SchoolScoreDetail.query.filter(SchoolScoreDetail.year == year,
                                                 SchoolScoreDetail.project_id == projects[1].id,
                                                 SchoolScoreDetail.school_id == school_id).first()
            girl = SchoolScoreDetail.query.filter(SchoolScoreDetail.year == year,
                                                  SchoolScoreDetail.project_id == projects[0].id,
                                                  SchoolScoreDetail.school_id == school_id).first()
        return round((boy_num*boy.score+girl_num*girl.score)/total_number,2)
    else:return False

def getYearRateRanked(year,type,school_type):
    # type=1 for passrate type=2 for goodrate
    schoolids=getTestingSchoolids(year,school_type)
    scores=SchoolScore.query.filter(SchoolScore.school_id.in_(schoolids)).all()
    if type==1:
        return sorted(scores,key=lambda x :(x.pass_rate,x.good_rate,x.excellent_rate),reverse=True)
    elif type==2:
        return sorted(scores, key=lambda x: (x.good_rate, x.pass_rate, x.excellent_rate), reverse=True)

def updateAllSettings(settingsform):
    #先获取所有的设置
    allsettings=Systemsetting.query.all()
    #遍历所有的设置项，如果名字相同（能找到）就更新，否则不更新
    for e in allsettings:
        newvalue=settingsform.get(e.name)
        if newvalue:
            e.value=newvalue
    #提交所有更新
    db.session.commit()
#**************省厅end**************

#**************学校端begin**************
#导入学生信息

def importStudent(filename,school_id):
    file_root_path=r"F:/zanproject/高校体测数据处理系统/code/tests/"
    filepath=os.path.join(file_root_path,filename)
    data=utils.excelToMatrix(filepath,header=0)
    columns=['school_id','college_name','grade','class_name','name','sex','student_number']
    for e in data:
        e[0]=1
        e[5]=1 if e[5]=="男" else 0
    quickInsert(Student,columns,data)

def addStudent(student:Student):
   try:
       db.session.add(student)
       db.session.commit()
   except Exception as e:
       print(e)
       return False
   return True

def updateStudent(student):
    mstudent=Student.query.get(student.id)
    if mstudent:
        mstudent.name = student.name
        mstudent.sex = student.sex
        mstudent.student_number = student.student_number
        mstudent.college_name = student.college_name
        mstudent.grade = student.grade
        mstudent.class_name = student.class_name
        db.session.commit()
        return True
    return False

#查询一个年级学生情况
def getStudentSumByGrade(grade,school_id):
    res = db.session.execute(
        "SELECT s.sex,COUNT(s.sex) FROM student s WHERE grade='{}' and school_id={} GROUP BY s.sex ".format(grade,school_id))
    ret={}
    #按照返回的情况是sex先0后1
    ret['girl_num']=0
    ret['boy_num'] = 0
    for e in list(res):
        if e[0]==0:
            ret['girl_num']=e[1]
        else:
            ret['boy_num']=e[1]
    ret['total_num']=ret['girl_num']+ret['boy_num']
    ret['grade']=grade
    return ret
#查询每个年级学生的情况
def getStudentSums(school_id):
    sums=[]
    #先查出所有的grade，再拿grade查出每个年级的情况
    res=Student.query.with_entities(Student.grade).distinct().filter(Student.school_id==school_id).order_by(Student.grade.desc()).all()
    for e in res:
        sums.append(getStudentSumByGrade(e[0],school_id))
    return sums
#查询学生
def findStudents(schoolid,name=None,number=None,college=None,grade=None,class_name=None,sex=None):
    filter_list=[]
    filter_list.append(Student.school_id==schoolid)
    if name and name!='':
        filter_list.append(Student.name==name)
    if number and number!='':
        filter_list.append(Student.student_number==number)
    if college and college!='':
        filter_list.append(Student.college_name==college)
    if grade and grade!='':
        filter_list.append(Student.grade==grade)
    if class_name and class_name!='':
        filter_list.append(Student.class_name==class_name)
    if sex and sex!='':
        filter_list.append(Student.sex==sex)
    return Student.query.filter(*filter_list).all()
#选择学生
#传入学生id的list
def selectStudents(studentids,year:int):
    success_num=0
    for id in studentids:
        student=Student.query.get(id)
        if student:
            if TestingStudent.query.filter(TestingStudent.student_id==id).first()==None:
                testingStudent=TestingStudent()
                testingStudent.year=year
                # year等于2018 说明2018-2019年的体测，2018级的学生属于大一
                #level整体计算更新，直接根据systemsettings里的level_benke level_zhuanke来取
                school=School.query.get(student.school_id)
                #给个虚假的初始值
                if school.type=="本科":
                    testingStudent.level=int(getSystemSetting("level_benke"))
                elif school.type=="高职高专":
                    testingStudent.level=int(getSystemSetting("level_zhuanke"))
                #如果大于4，按照4来算
                testingStudent.student_id=student.id
                testingStudent.school_id=student.school_id
                db.session.add(testingStudent)
                #记录成功添加一个体测学生
                success_num=success_num+1
    db.session.commit()
    return success_num

#创建审核
def createSubmitStudent(school_id,year,comment):
    ret=getTestingStudentNum(school_id,year)
    boy=ret['boy']
    girl=ret['girl']
    studentSelection=StudentSelection()
    studentSelection.year=year
    studentSelection.boy=boy
    studentSelection.girl=girl
    studentSelection.submit=1
    studentSelection.confirm=0
    studentSelection.submit_comment=comment
    studentSelection.school_id=school_id
    db.session.add(studentSelection)
    db.session.commit()
    return


#获取一个学校指定年的抽测男生女生数量
def getTestingStudentNum(school_id,year):
    res=getTestingStudentSums(year,school_id)
    ret={}
    ret['boy']=0
    ret['girl']=0
    for e in res:
        ret['boy']=ret['boy']+e['boy_num']
        ret['girl']=ret['girl']+e['girl_num']
    return ret
#查询指定年抽取人数情况
#查询一个年级体测学生情况
def getTestingStudentSumByGrade(grade,year,school_id):
    res = db.session.execute(
        "SELECT s.sex,COUNT(s.sex) FROM testingstudent ts INNER JOIN student s ON ts.student_id=s.id WHERE ts.year={} AND s.grade='{}' AND s.school_id={}  GROUP BY s.sex ".format(year,grade,school_id))
    ret={}
    #按照返回的情况是sex先0后1
    ret['girl_num']=0
    ret['boy_num'] = 0
    for e in list(res):
        if e[0]==0:
            ret['girl_num']=e[1]
        else:
            ret['boy_num']=e[1]
    ret['total_num']=ret['girl_num']+ret['boy_num']
    ret['grade']=grade
    return ret

#获取历史体测情况
def getTestingStudentSumBefore(nowyear,school_id):
    #先获取所有的年
    res=TestingStudent.query.with_entities(TestingStudent.year).filter(TestingStudent.school_id==school_id,TestingStudent.year<nowyear).distinct().all()
    ret=[]
    if res:
        for e in res:
            #每年的数据根据审核上交的情况来获取
            selection=StudentSelection.query.filter(StudentSelection.year==e[0],StudentSelection.school_id==school_id).first()
            temp={}
            temp['boy_num']=selection.boy
            temp['girl_num']=selection.girl
            temp['year']=e[0]
            ret.append(temp)
        return ret
    return ret


#查询指定年每个年级体测学生的情况
def getTestingStudentSums(year:int,school_id):
    #year为2018代表体测年2018，及2018-2019
    sums=[]
    #先查出所有的grade，再拿grade查出每个年级的情况
    res=TestingStudent.query.join(Student).filter(TestingStudent.school_id==school_id).with_entities(Student.grade).filter(TestingStudent.year==year).distinct().order_by(Student.grade.desc()).all()
    for e in res:
        sums.append(getTestingStudentSumByGrade(e[0],year,school_id))
    return sums

#查询单个学生成绩
#返回dict,name:score
def getStudentScore(tstudent_id):
    #注意是从testingstudent里查
    res=db.session.execute(
        "SELECT tp.name ,ts.score FROM  testingscore ts JOIN testingproject tp ON ts.project_id=tp.id WHERE ts.tstudent_id={}".format(tstudent_id)
    )
    ret={}
    for e in res:
        #0是name，1是score
        ret[e[0]]=e[1]
    return ret

#筛选查询成绩
#返回一个dict数组，里面是所有信息以及score,id是tstudentid
def getMultipleStudentScore(schoolid,grade=None,college=None,number=None,year=None,name=None,class_name=None):
    filter_list = []
    filter_list.append(TestingStudent.school_id == schoolid)
    if name and name!='':
        filter_list.append(Student.name == name)
    if number and number!='':
        filter_list.append(Student.student_number == number)
    if college and college!='':
        filter_list.append(Student.college_name == college)
    if grade and grade!='':
        filter_list.append(Student.grade == grade)
    if year and year!='':
        filter_list.append(TestingStudent.year == year)
    if class_name:
        filter_list.append(Student.class_name == class_name)
    res=TestingStudent.query.join(Student).filter(*filter_list).all()
    ret=[]
    for e in res:
        studentscore={}
        #拿的因该是testingstudent的id
        studentscore['id']=e.id
        studentscore['college_name']=e.student.college_name
        studentscore['grade']=e.student.grade
        studentscore['class_name']=e.student.class_name
        studentscore['name']=e.student.name
        studentscore['sex']=e.student.sex
        studentscore['student_number']=e.student.student_number
        studentscore['year']=e.year
        studentscore['score']=e.score
        ret.append(studentscore)
    return ret



#获取学校成绩模板的数据，二维数组的形式，传给api直接生成数据
#传schoolid为-1 说明只要头
def getTemplateData(schoolid,year):
    ret=[]
    #行首
    headers=['序号','学校名称','姓名','性别','学号']
    #筛下除了性别其他都一样的项目字段
    projects=getYearAllProject(year)
    for p in projects:
        name=p.name
        if p.comment:
            name+="("+p.comment+")"
        headers.append(name)
    ret.append(headers)
    if schoolid==-1:
        #只要头
        return ret
    school_name = School.query.get(schoolid).name
    #定义序号
    th=1
    #查到学生并把基本信息填进去
    for e in getTestingStudent(schoolid,year):
        temp=[]
        temp+=[th,school_name,e.name]
        temp.append("男" if e.sex==1 else "女")
        temp.append(e.student_number)
        ret.append(temp)
        th+=1
    return ret
#**************学校段end**************

#**************系统级begin**************
def getProjectWeight(year):
    #计算男生和女生的项目的真实权值，返回[{id:weight}]
    boys=getSelectProjects(year,1)
    boyweights={}
    sum=0
    for e in boys:
        #先计算权重和
        sum+=e.weight
    for e in boys:
        #权重矫正后放入
        boyweights[e.id]=e.weight/sum
    girls=getSelectProjects(year,0)
    gilrweights = {}
    sum = 0
    for e in girls:
        sum += e.weight
    for e in girls:
        gilrweights[e.id] = e.weight / sum
    #男女一起
    boyweights.update(gilrweights)
    return boyweights

def calculateStudentScore(year):
    #先计算出各个项目对应的真实权值
    weights=getProjectWeight(year)
    #先处理原始成绩
    try:
        tstudents=TestingStudent.query.filter(TestingStudent.year==year).all()
        for t in tstudents:
            #找到所有成绩
            scores=TestingScore.query.filter(TestingScore.tstudent_id==t.id).all()
            totalScore=0
            for s in scores:
                #每个成绩进行原始成绩转化为得分
                if s.score==None:
                    #score 没有默认值0，所以NOne是没计算过
                    s.score=__getScore(s.row_data,s.project_id)
                    #即使更新过了，这边也要拿到成绩，用于放到tstudent里
                totalScore+=s.score*weights[s.project_id]
            #保留两位小数存进去
            t.score=round(totalScore,2)
        db.session.commit()
    except Exception as e:
        #先回退再报错
        db.session.rollback()
        raise e

#给原始成绩和项目查找实际成绩，如果找不到返回0
def __getScore(row_data,project_id):
    #rowdata是字符串
    row_data=float(row_data)
    project = TestingProject.query.get(project_id)
    if project.scoreType==1:
        #高优计算是 =< <
        for standard in project.standards:
            if row_data>=standard.bottom and row_data<standard.top:
                return standard.score
    elif project.scoreType==-1:
        #低优计算是 < <=
        for standard in project.standards:
            if row_data>standard.bottom and row_data<=standard.top:
                return standard.score
    #找不到返回0
    return 0

def calculateSchoolScore(year):
    #先找出所有的学校
    #testingstudent表里计算总分平均值  优秀率等 天道schoolscore
    school_ids=TestingStudent.query.with_entities(TestingStudent.school_id).distinct().all()
    #这里查出来要转化一下
    try:
        for school_id in school_ids:
            school_id=school_id[0]
            tstudents=TestingStudent.query.filter(TestingStudent.year==year,TestingStudent.school_id==school_id).all()
            scorelist=[]
            for t in tstudents:
                scorelist.append(t.score)
            average,excellent_rate,good_rate,pass_rate=utils.calculateScorelist(scorelist)
            #如果之前有，说明这次只是更新就好了
            schoolScore=SchoolScore.query.filter(SchoolScore.year==year,SchoolScore.school_id==school_id).first()
            if schoolScore==None:
                schoolScore=SchoolScore()
            schoolScore.year=year
            schoolScore.testing_number=len(scorelist)
            schoolScore.school_id=school_id
            schoolScore.score=average
            schoolScore.excellent_rate=excellent_rate
            schoolScore.good_rate=good_rate
            schoolScore.pass_rate=pass_rate
            if schoolScore.id==None:
                #处理新增
                db.session.add(schoolScore)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    #填充学校成绩其他字段 （人数、优秀、及格人数等）
    calculateSchoolScoreNumber(year)
    #score表里计算学校-项目的平均值 优秀率等 填到schoolscoredetail
    boy=getSelectProjects(year,1)
    girl=getSelectProjects(year,0)
    try:
        for school_id in school_ids:
            school_id = school_id[0]
            for project in boy+girl:
                scores=TestingScore.query.filter(TestingScore.school_id==school_id,TestingScore.project_id==project.id).all()
                scorelist = []
                for score in scores:
                    scorelist.append(score.score)
                average, excellent_rate, good_rate, pass_rate = utils.calculateScorelist(scorelist)
                #如果之前有数据只需要更新
                schoolScoreDetail = SchoolScoreDetail.query.filter(SchoolScoreDetail.year == year,
                                                                   SchoolScoreDetail.school_id == school_id,
                                                                   SchoolScoreDetail.project_id == project.id).first()
                if schoolScoreDetail==None:
                    schoolScoreDetail=SchoolScoreDetail()
                schoolScoreDetail.project_id=project.id
                schoolScoreDetail.school_id=school_id
                schoolScoreDetail.year=year
                schoolScoreDetail.score=average
                schoolScoreDetail.excellent_rate=excellent_rate
                schoolScoreDetail.good_rate=good_rate
                schoolScoreDetail.pass_rate=pass_rate
                if schoolScoreDetail.id==None:
                    #如果id不在说明事新增模式
                    db.session.add(schoolScoreDetail)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def calculateSchoolScoreNumber(year):
    res=SchoolScore.query.filter(SchoolScore.year==year).all()
    try:
        for schoolScore in res:
            tstudents = TestingStudent.query.filter(TestingStudent.year == year,
                                                    TestingStudent.school_id == schoolScore.school_id).all()
            manyNumbers=__getScoreLeverNumber(tstudents)
            schoolScore.testing_number=manyNumbers[0]
            schoolScore.boy_number=manyNumbers[1]
            schoolScore.girl_number=manyNumbers[2]
            schoolScore.excellent_number=manyNumbers[3]
            schoolScore.excellent_boy_number=manyNumbers[4]
            schoolScore.excellent_girl_number=manyNumbers[5]
            schoolScore.good_number=manyNumbers[6]
            schoolScore.good_boy_number=manyNumbers[7]
            schoolScore.good_girl_number=manyNumbers[8]
            schoolScore.pass_number=manyNumbers[9]
            schoolScore.pass_boy_number=manyNumbers[10]
            schoolScore.pass_girl_number=manyNumbers[11]
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
def __getScoreLeverNumber(tstudents):
    number=len(tstudents)
    boy_number=0
    excellent_number=0
    excellent_boy_number=0
    good_number=0
    good_boy_number=0
    pass_number=0
    pass_boy_number=0
    #开始循环
    for e in tstudents:
        sex=e.student.sex
        if sex==1:
            boy_number+=1
        if e.score>=90:
            excellent_number+=1
            if sex==1:
                excellent_boy_number+=1
        if e.score>=80:
            good_number+=1
            if sex==1:
                good_boy_number+=1
        if e.score>=60:
            pass_number+=1
            if sex==1:
                pass_boy_number+=1
    #结束循环
    #处理女生
    girl_number=number-boy_number
    excellent_girl_number = excellent_number-excellent_boy_number
    good_girl_number = good_number-good_boy_number
    pass_girl_number = pass_number-pass_boy_number
    return number, boy_number, girl_number, excellent_number, excellent_boy_number, excellent_girl_number, \
           good_number, good_boy_number, good_girl_number, pass_number, pass_boy_number, pass_girl_number

#**************系统级end****************

#**************公共方法**************
#传入类，列名和数据，快速插入到数据库
def quickInsert(model,columns,data):
    db.session.execute(
        model.__table__.insert(),
        [dict(zip(columns,d)) for d in data]
    )
    db.session.commit()

##按照confirm和submit的和来算 0，0代表未提交或者审核不通过 1，0代表已提交未审核 1，1代表审核通过  没有记录代表未提交 2,1代表提交申请重选
## 所以 返回0 1 2 -1 3    5种状况
def getSubmitStatus(school_id,year):
    studentSelection=StudentSelection.query.filter(StudentSelection.year==year,StudentSelection.school_id==school_id).first()
    if studentSelection:
        return studentSelection.submit+studentSelection.confirm
    else:return -1

#get all project names (distinct)
def getProjectNames(year):
    projects=getYearAllProject(year)
    ret=[]
    for e in projects:
        ret.append(e.name)
    return ret

def getYearAllProject(year):
    boy=getSelectProjects(year,1)
    girl=getSelectProjects(year,0)
    for e in boy:
        for p in girl[:]:
            if e.name==p.name and e.weight==p.weight and e.scoreType==p.scoreType:
                #三者都相同认为是同一个项目只有性别不同
                girl.remove(p)
    #筛选后合并
    projects=boy+girl
    return projects

def downloadScoreTemplate(school_id):
    school = School.query.get(school_id)
    year = utils.getNowTestingYear()
    # 获取excel要导入的所有数据
    data = getTemplateData(school_id, year)
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
    # 先加头部
    table.write_row("A1", data[0], cell_format=headstyle)
    # 每行数据添加
    for i in range(1, len(data)):
        line = data[i]
        table.write_row('A' + str(i + 1), line, cell_format=datastyle)
    workbook.close()
    # 调整偏移到第一个
    out.seek(0)
    # 中文正常编码
    filename = quote(school.name + "成绩模板.xlsx")
    rv = send_file(out, as_attachment=True, attachment_filename=filename)
    rv.headers['Content-Disposition'] += "; filename*=utf-8''{}".format(filename)
    return rv

#获取系统配置数据
def getSystemSetting(name):
    res=Systemsetting.query.filter(Systemsetting.name == name).first()
    if res:
        return res.value
    else: return None
def updateSystemSetting(name,value,comment=None):
    #转化为str类型
    value=str(value)
    res=Systemsetting.query.filter(Systemsetting.name == name).first()
    #如果在就更新
    if res:
        if comment:
            res.comment=comment
        res.value=value
    else:
        #否则为添加模式
        newsetting=Systemsetting()
        newsetting.name=name
        newsetting.value=value
        if comment:
            newsetting.comment=comment
        db.session.add(newsetting)
    #提交更新
    db.session.commit()