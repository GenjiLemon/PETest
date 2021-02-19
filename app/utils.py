#此文件为公共工具类

import numpy as np
import pandas as pd
from flask import jsonify


def jsonRet(code=0,msg="",data=None,count=None):
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
