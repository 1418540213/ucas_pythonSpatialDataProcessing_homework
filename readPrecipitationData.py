import io
import re
import os
import glob
from smtplib import OLDSTYLE_AUTH
import pandas
from zipfile import *
import numpy as np

basedir = r'./data/'
filename = '20210726.zip'
outputpath = './data/20210726.csv'

# ---------------------------------------------------------------------------------------------------------------------
# 读取日气象数据，并转为数组形式
# ---------------------------------------------------------------------------------------------------------------------


def unzip(filename):
    data = []
    zipped = ZipFile(filename)
    for obj in zipped.filelist:
        if obj.is_dir():
            continue
        if re.match('^S[0-9]{21,21}\.((ZIP)|(zip))$', os.path.split(obj.filename)[-1]):
            mem = io.BytesIO()
            mem.write(zipped.open(obj.filename).read())
            mem.seek(0)
            zipped_ = ZipFile(mem)
            for txt in zipped_.filelist:
                if txt.is_dir():
                    continue
                if re.match('^S[0-9]{21,21}\.((TXT)|(txt))$', txt.filename):
                    buff = zipped_.open(txt.filename).read()
                    data.append([filename, obj.filename, txt.filename,
                                buff.decode('utf8').split('\n')])
    return data
# ---------------------------------------------------------------------------------------------------------------------
# 根据区号对降雨量进行分组求和，并存储为csv格式
# ---------------------------------------------------------------------------------------------------------------------


def to_csv(outputpath, data):
    for x in range(31):
        buff = data[x][-1]
        fdlist = buff[0].split(' ')
        # print(fdlist)
        arry = np.array([[float(v) for v in b.strip().split(' ')]
                        for b in buff[1:] if len(b.strip()) > 0])
        # print(arry)
        series = [[fdlist[i], arry[:, i]] for i in range(len(fdlist))]
        # print(series)
        df = pandas.DataFrame(dict(series))
        g = df.groupby(["Station_Id_C"])
        out = g[["PRE_1h"]].aggregate(np.sum)
        out.to_csv(outputpath, sep=',', index=True, header=False, mode="a")
        # df1是你想要输出的的DataFrame
        # index是否要索引，header是否要列名，True就是需要


# ---------------------------------------------------------------------------------------------------------------------
# 调用函数
# ---------------------------------------------------------------------------------------------------------------------
filepath = os.path.join(basedir, filename)
data = unzip(filepath)
to_csv(outputpath, data)
