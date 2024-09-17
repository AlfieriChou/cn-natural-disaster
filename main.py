from tropical_cyclone import (
  get_tropical_cyclone_list,
  write_tropical_cyclone_list_to_db,
)
from libs.area import area_dict
from libs.md5 import md5
from libs.mysql import connection

data_list = get_tropical_cyclone_list()
dict_list = []

# 手动补充24年数据
data_list += [
  ['2024', '3', '', '', '格美', '1', '1', '台湾', ''],
  ['2024', '4', '', '', '派比安', '1', '1', '海南', ''],
  ['2024', '11', '', '', '摩羯', '1', '1', '海南', ''],
  ['2024', '13', '', '', '贝碧嘉', '1', '1', '上海', ''],
]

for data in data_list:
  (
    series,
    code,
    china_code,
    english_name,
    chinese_name,
    land_count,
    land_index,
    land_area,
    land_level,
  ) = data
  if '－' in land_area:
    land_area = land_area.split('－')[0]  # 先默认保留第一个，后续再进行拆分
  if '-' in land_area:
    land_area = land_area.split('-')[0]  # 先默认保留第一个，后续再进行拆分
  dict = {
    'id': md5(series + code + land_index + land_area),
    'series': series,
    'code': code,
    'china_code': china_code,
    'english_name': english_name,
    'chinese_name': chinese_name,
    'land_count': int(land_count),
    'land_index': int(land_index),
    'land_area': land_area,
    'land_area_code': area_dict[land_area],
    'land_level': land_level,
  }
  dict_list.append(
    [
      dict['id'],
      dict['series'],
      dict['code'],
      dict['china_code'],
      dict['english_name'],
      dict['chinese_name'],
      dict['land_count'],
      dict['land_index'],
      dict['land_area'],
      dict['land_area_code'],
      dict['land_level'],
    ]
  )
write_tropical_cyclone_list_to_db(dict_list, connection)

connection.close()
