#此文件为公共工具类

import numpy as np
import pandas as pd



def excelToMatrix(filePath,header=None):
    if filePath.find('.xlsx') != -1 or filePath.find('.xls') != -1:
        WS = pd.read_excel(filePath, header=header)
        return np.array(WS)
    if filePath.find('.csv') != -1:
        with open(filePath, 'r', errors='ignore') as fileHandle:
            return np.loadtxt(fileHandle,delimiter=",")
    return