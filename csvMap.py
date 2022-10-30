from jsonschema import draft201909_format_checker
import pandas

filename20 = './data/china_precipitation_2170stations.csv'
filename26 = './data/20210726.csv'
outputpath = './data/20210720-20210726.csv'
# ---------------------------------------------------------------------------------------------------------------------
# 读取14-20日及20-26日降雨量数据，并进行合并,生成总降雨量表
# ---------------------------------------------------------------------------------------------------------------------
df20 = pandas.read_csv(filename20, encoding='gb2312')
df26 = pandas.read_csv(filename26, encoding='gb2312',
                       header=None, names=['区站号', '降雨量20-26'])
df3 = pandas.merge(df20, df26)
df3['总降雨量'] = df3.iloc[:, 3:5].sum(axis=1)
df3.to_csv(outputpath, sep=',', index=False, header=True, encoding="utf_8_sig")
