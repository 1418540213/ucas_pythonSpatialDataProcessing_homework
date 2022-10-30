import matplotlib.pyplot as plt
import numpy as np
import pandas
import geopandas
import rasterio
import rioxarray
import xarray
import math

from scipy import interpolate
from shapely.geometry import Polygon
from rasterio.transform import Affine
from rasterio import features
from mpl_toolkits.basemap import Basemap, cm

# 读取矢量地图
filename = './data/CHN_adm1.shp'
china = geopandas.read_file(filename)

# 地图范围
minx = china.bounds['minx'].min()
miny = china.bounds['miny'].min()
maxx = china.bounds['maxx'].max()
maxy = china.bounds['maxy'].max()

# 分辨率为0.5的仿射投影变换
delta = 0.5
row = math.ceil((maxy - miny) / delta)
col = math.ceil((maxx - minx) / delta)
transform = Affine.from_gdal(minx, delta, 0, miny, 0, delta)

china['region'] = 1
polys = ((geom, value) for geom, value in zip(china.geometry, china['region']))
mask = features.rasterize(shapes=polys, out_shape=(
    row, col), fill=0, transform=transform)

# 读取了站点坐标并进行了插值，prec为降雨量矩阵
filename = './data/20210720-20210726.csv'
df = pandas.read_csv(filename, encoding="utf_8_sig")
gdf = geopandas.GeoDataFrame(
    df, geometry=geopandas.points_from_xy(df["X"], df["Y"]))
# filtering-noise
gdf = gdf.query('70<X<135 and 15<Y<55 and 0<总降雨量<1000')
# rbf
x_ = np.arange(minx + delta / 2, minx + col * delta, delta)
y_ = np.arange(miny + delta / 2, miny + row * delta, delta)
X, Y = np.meshgrid(x_, y_)
#
# 'multiquadric': sqrt((r/self.epsilon)**2 + 1)
# 'inverse': 1.0/sqrt((r/self.epsilon)**2 + 1)
# 'gaussian': exp(-(r/self.epsilon)**2)
# 'linear': r
# 'cubic': r**3
# 'quintic': r**5
# 'thin_plate': r**2 * log(r)
rbf = interpolate.Rbf(gdf['X'], gdf['Y'], gdf['总降雨量'],
                      function="thin_plate")  # 样条函数插值
Z = rbf(X, Y)

# 按矢量地图范围掩膜
prec = Z * 1.0
prec[np.where(mask == 0)] = np.nan
prec[np.where(prec <= 0)] = np.nan


# 基于basemap绘图
ax = plt.gca()

# 投影、经纬网
m = Basemap(llcrnrlat=miny, urcrnrlat=maxy, llcrnrlon=minx, urcrnrlon=maxx,
            ellps='WGS84', epsg=4326, resolution='l', ax=ax)
m.drawmeridians(np.arange(80, 135, 10), labels=[
                0, 0, 0, 1], fontsize=10, linewidth=2)
m.drawparallels(np.arange(20, 60, 10), labels=[1, 0, 0, 0], fontsize=10)

# 等值线、图例
clevs = [v for v in range(0, 50, 1)] + \
    [v for v in range(50, 800, 50)] + [800, 5000]
cs = m.contourf(X, Y, prec, clevs, cmap=cm.s3pcpn)
cbar = m.colorbar(cs, location='right', pad="3%")
cbar.set_label('mm')

# 边界、城市名
china.plot(ax=ax, linewidth=1, facecolor="none")
# for x, y, label in zip(china.geometry.centroid.x, china.geometry.centroid.y, china['NAME_1']):
#     ax.annotate(label[:5], xy=(x, y), xytext=(-3, 3),
#                 textcoords="offset points", color='black')
#     #print(x, y, label)

# 标题
plt.title('Mailand Precipitation (2021.7.14-2021.7.26)')
plt.show()
