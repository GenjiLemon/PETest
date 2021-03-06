#此文件为公共工具类

import numpy as np
import pandas as pd
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
def addIdColumn(data):
    th=1
    for e in data:
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