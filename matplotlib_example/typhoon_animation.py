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
      'select series, land_area_code, land_area, count(1) as count from tropical_cyclone group by series, land_area_code, land_area order by series asc',
    )
    data_list = cursor.fetchall()
    dict_list = []
    for row in data_list:
      if row['series'] not in dates:
        dates.append(row['series'])
      dict_list.append(
        {
          'name': row['land_area'],
          'group': row['land_area'],
          'date': row['series'],
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
nine_dash_line = china[china.name == '十段线']

df = pd.DataFrame(
  {
    'date': df0['date'].tolist(),
    'province': df0['name'].tolist(),
    'value': df0['value'].tolist(),
  }
)

fig, ax = plt.subplots(figsize=(16, 9))
ax_rank = fig.add_axes([0.02, 0.05, 0.18, 0.35])
fontsize = 8

ims = []
t = []
dates = df['date'].unique()
vmin, vmax = df['value'].min(), df['value'].max()


def update_fig(i):
  if len(ims) > 0:
    del ims[0]
  ax_rank.clear()
  geos = china_w_needed_provinces['geometry']
  value = df[df['date'] == dates[i]]['value'].tolist()
  print(geos, value)
  artist = gpd.plotting._plot_polygon_collection(ax, geos, value, cmap='Reds')
  ims.append(artist)
  nine_dash_line.plot(ax=ax, color='black', linestyle='--', linewidth=1.2)
  # ax.text(20, 45, 'Date:\n{}'.format(dates[i]), fontsize=fontsize, horizontalalignment='center')
  for lon, lat, province in zip(
    china_w_needed_provinces.lon,
    china_w_needed_provinces.lat,
    china_w_needed_provinces.name,
  ):
    ax.text(lon, lat, province, fontsize=fontsize)
  ax.set_title(
    '{}年至{}年各省台风记录 单位：（次） {}年'.format(
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
  # 左下角省份排名表格（只显示次数大于0的）
  current_df = df[df['date'] == dates[i]]
  sorted_df = current_df[current_df['value'] > 0].sort_values(by='value', ascending=False)
  ax_rank.clear()
  ax_rank.set_axis_off()
  
  if len(sorted_df) > 0:
    # 绘制表格
    table_data = [[row['province'], str(row['value'])] for _, row in sorted_df.iterrows()]
    col_labels = ['省市', '次数']
    
    table = ax_rank.table(
      cellText=table_data,
      colLabels=col_labels,
      loc='upper center',
      cellLoc='center',
      colWidths=[0.5, 0.3]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize + 4)
    table.scale(1, 1.5)
  return ims


anim = FuncAnimation(
  fig,
  update_fig,
  interval=1000,
  repeat_delay=300,
  frames=len(df['date'].unique()),
)

# plt.show()
anim.save(filename='video/typhoon_animation.mp4', writer='ffmpeg')
