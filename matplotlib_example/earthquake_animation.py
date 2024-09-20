import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib
from matplotlib import font_manager

from mysql import connection

font_manager.fontManager.addfont('font/SimHei.ttf')
matplotlib.rc('font', family='SimHei')
china = gpd.read_file('geo/china_v1.json')
area_list = [
  '北京',
  '天津',
  '河北',
  '山西',
  '内蒙古',
  '辽宁',
  '吉林',
  '黑龙江',
  '上海',
  '江苏',
  '浙江',
  '安徽',
  '福建',
  '江西',
  '山东',
  '河南',
  '湖北',
  '湖南',
  '广东',
  '广西',
  '海南',
  '重庆',
  '四川',
  '贵州',
  '云南',
  '西藏',
  '陕西',
  '甘肃',
  '青海',
  '宁夏',
  '新疆',
  '台湾',
  '香港',
  '澳门',
]
provinces = area_list
dates = []


def get_area_data_list():
  with connection.cursor() as cursor:
    # 查询并打印结果以验证数据插入成功
    cursor.execute(
      '''
      select 
        month_date_str, 
        area, 
        count(1) as count 
      from 
        (
          select 
            FROM_UNIXTIME(date, '%Y-%m') as month_date_str, 
            area 
          from 
            `earthquake`
        ) as temp 
      group by 
        month_date_str, 
        area 
      order by 
        month_date_str
      ''',
    )
    data_list = cursor.fetchall()
    dict_list = []
    for row in data_list:
      if row['month_date_str'] not in dates:
        dates.append(row['month_date_str'])
      dict_list.append(
        {
          'name': row['area'],
          'group': row['area'],
          'date': row['month_date_str'],
          'value': row['count'],
        }
      )

    return dict_list


base_list = get_area_data_list()

dict_list = []


def search(name, date, dict_list):
  return [
    element
    for element in dict_list
    if element['name'] == name and element['date'] == date
  ]


for date in dates:
  for area in area_list:
    t = search(area, date, base_list)
    if len(t) == 0:
      dict_list.append(
        {
          'name': area,
          'group': area,
          'date': date,
          'value': 0,
        }
      )
    else:
      dict_list.append(t[0])
print(dates, area_list)
df0 = pd.DataFrame.from_dict(dict_list)
connection.close()

china_w_needed_provinces = china[china.name.isin(provinces)]

df = pd.DataFrame(
  {
    'date': df0['date'].tolist(),
    'province': df0['name'].tolist(),
    'value': df0['value'].tolist(),
  }
)

fig, ax = plt.subplots(figsize=(16, 9))
fontsize = 8

ims = []
t = []
dates = df['date'].unique()
vmin, vmax = df['value'].min(), df['value'].max()


def update_fig(i):
  if len(ims) > 0:
    del ims[0]
  geos = china_w_needed_provinces['geometry']
  value = df[df['date'] == dates[i]]['value'].tolist()
  artist = gpd.plotting._plot_polygon_collection(ax, geos, value, cmap='Reds')
  ims.append(artist)
  # ax.text(20, 45, 'Date:\n{}'.format(dates[i]), fontsize=fontsize, horizontalalignment='center')
  for lon, lat, province in zip(
    china_w_needed_provinces.lon,
    china_w_needed_provinces.lat,
    china_w_needed_provinces.name,
  ):
    ax.text(lon, lat, province, fontsize=fontsize)
  ax.set_title(
    '{}年至{}年各省地震记录 单位：（次） {}年'.format(
      dates[0], dates[-1], dates[i]
    )
  )
  ax.set_axis_off()
  fig = ax.get_figure()
  cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
  sm = plt.cm.ScalarMappable(
    cmap='Reds', norm=plt.Normalize(vmin=vmin, vmax=vmax)
  )
  # fake up the array of the scalar mappable. Urgh...
  sm._A = []
  fig.colorbar(sm, cax=cax)
  return ims


anim = FuncAnimation(
  fig,
  update_fig,
  interval=1000,
  repeat_delay=500,
  frames=len(df['date'].unique()),
)

# plt.show()
anim.save(filename='video/earthquake_animation.mp4', writer='ffmpeg')
