#此文件为公共工具类

import numpy as np
import pandas as pd

from collections import Counter,OrderedDict
from flask import jsonify
import datetime

def objToDict(obj):
    ret={}
    if hasattr(obj,'__dict__'):
        for k,v in obj.__dict__.items():
            if not k.startswith('_'):
                ret[k]=v
    return ret

def jsonRet(code=0,msg="",data=None,count=None):
    print("jsonret 得到的数据为")
    print(data)
    map={
        "code":code,
        "msg":msg,
        "data":data
    }
    if count:
        map['count']=count
    return jsonify(map)
def excelToMatrix(filePath,header=None):
    if filePath.find('.xlsx') != -1 or filePath.find('.xls') != -1:
        WS = pd.read_excel(filePath, header=header)
        return np.array(WS)
    if filePath.find('.csv') != -1:
        with open(filePath, 'r', errors='ignore') as fileHandle:
            return np.loadtxt(fileHandle,delimiter=",")
    return
#obj为True表示是对象，否则是dict
def addIdColumn(data,obj=False):
    th=1
    for e in data:
        if obj:
            e.id=th
        else:
            e['id']=th
        th=th+1
    return data
#用来转化学生类中的str grade
def gradeToInt(s):
    try:
        return int(s)
    except:
        if s[-1]=="级" and len(s)==5:
            return int(s[0:4])
        else:
            raise Exception("grade error")

def getNowTestingYear():
    #获取当前体测年份，目前采取根据时间获取的方法
    today = datetime.date.today()
    year=today.year
    if today.month<9:
        year=year-1
    return year

#传入 name(备注) 返回name
def getProjectName(title):
    end=title.find('(')
    if end==-1:
        return title
    else:
        return title[:end]


#传入scorelist 传回平均值 优秀率 良好率 及格率
def calculateScorelist(scorelist,averageOnly=False):
    #平均值保留两位，其他保留四位
    narray=np.array(scorelist)
    average=round(float(narray.mean()),2)
    if averageOnly:
        return average
    else:
        if len(scorelist)==0:
            return 0,0,0,0
        excellent_rate=round(np.count_nonzero(narray >= 90)/len(scorelist),4)
        good_rate=round(np.count_nonzero(narray >= 80)/len(scorelist),4)
        pass_rate=round(np.count_nonzero(narray >= 60)/len(scorelist),4)
        return average,excellent_rate,good_rate,pass_rate


#获取list的每个元素的排序list
def getOrderList(datalist):
    cplist = datalist[:]
    cplist.sort()
    ret=[]
    for e in datalist:
        ret.append(cplist.index(e) + 1)
    return ret

#把dict中所有key的int转成str类型
def strDictKey(dictdata:dict):
    for k in list(dictdata.keys()):
        if isinstance(k,int):
            dictdata[str(k)]=dictdata.pop(k)
    return dictdata