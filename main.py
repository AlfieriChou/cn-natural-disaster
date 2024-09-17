from tropical_cyclone import (
  get_tropical_cyclone_list,
  write_tropical_cyclone_list_to_db,
)
from libs.area import area_dict
from libs.md5 import md5
from libs.mysql import connection

data_list = get_tropical_cyclone_list()
dict_list = []

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
    'series': int(series),
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
write_tropical_cyclone_list_to_db(dict_list, connection)

connection.close()
