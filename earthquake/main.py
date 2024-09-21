# https://data.earthquake.cn/datashare/report.shtml?PAGEID=earthquake_subao

import pandas as pd
import pyexcel as p
import datetime

from libs.area import area_dict, area_list
from libs.md5 import md5
from libs.mysql import connection


def get_date_str_zero_timestamp(date_str):
  date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
  midnight = date.replace(hour=0, minute=0, second=0, microsecond=0)
  midnight_ts = midnight.timestamp()
  return int(midnight_ts)


def get_date_str_timestamp(date_str):
  date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
  timestamp = date.timestamp()
  return int(timestamp)


def read_earthquake_xlsx(xlsx_path):
  data_list = []
  # 暂不支持解析xls文件
  if xlsx_path.endswith('.xls') is True:
    p.save_book_as(file_name=xlsx_path, dest_file_name=xlsx_path + 'x')
  dfs = pd.read_excel(xlsx_path, sheet_name=None)
  for sheet_name, value in dfs.items():
    if '速报目录' in sheet_name:
      for index, row in value.iterrows():
        if index == 0:
          continue
        earthquake_list = row.to_list()
        date_str = earthquake_list[1]
        longitude = float(earthquake_list[2])
        latitude = float(earthquake_list[3])
        area_detail = earthquake_list[6]
        area = area_detail[0:2]
        if area not in area_list:
          continue
        area_code = area_dict[area[0:2]]
        date = get_date_str_zero_timestamp(str(date_str))
        date_timestamp = get_date_str_timestamp(str(date_str))
        id = md5(str(date_str) + str(longitude) + str(latitude))
        dict = {
          'id': id,
          'date_str': str(date_str),
          'date': date,
          'date_timestamp': date_timestamp,
          'area_code': area_code,
          'area': area,
          'series': str(earthquake_list[0]),
          'longitude': longitude,
          'latitude': latitude,
          'depth': int(earthquake_list[4]),
          'level': float(earthquake_list[5]),
          'area_detail': area_detail,
          'event_type': earthquake_list[7],
        }
        data_list.append(
          [
            dict['id'],
            dict['date_str'],
            dict['date'],
            dict['date_timestamp'],
            dict['area_code'],
            dict['area'],
            dict['area_detail'],
            dict['series'],
            dict['longitude'],
            dict['latitude'],
            dict['depth'],
            dict['level'],
            dict['event_type'],
          ]
        )

  return data_list


def write_earthquake_list_to_db(data_list, connection):
  try:
    with connection.cursor() as cursor:
      # 创建表（如果尚未存在）
      cursor.execute("""
      CREATE TABLE IF NOT EXISTS earthquake (
        id VARCHAR(64) PRIMARY KEY,
        date_str VARCHAR(64) NOT NULL,
        date INT NOT NULL,
        date_timestamp INT NOT NULL,
        area_code VARCHAR(32) NOT NULL,
        area VARCHAR(32) NOT NULL,
        area_detail VARCHAR(255) NOT NULL,
        series VARCHAR(64) NOT NULL,
        longitude FLOAT NOT NULL,
        latitude FLOAT NOT NULL,
        depth INT NOT NULL,
        level FLOAT NOT NULL,
        event_type VARCHAR(32) NOT NULL,
        INDEX idx_id (id),
        INDEX idx_date (date),
        INDEX idx_date_timestamp (date_timestamp),
        INDEX idx_area_code (area_code),
        INDEX idx_series (series),
        INDEX idx_longitude (longitude),
        INDEX idx_latitude (latitude),
        INDEX idx_depth (depth),
        INDEX idx_level (level),
        INDEX idx_area (area),
        INDEX idx_event_type (event_type)
      )
      """)

      # 插入数据
      # 构建INSERT语句
      insert_query = """
        INSERT IGNORE INTO earthquake (
          id,
          date_str,
          date,
          date_timestamp,
          area_code,
          area,
          area_detail,
          series,
          longitude,
          latitude,
          depth,
          level,
          event_type
        ) VALUES (
          %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
      """

      # 构建并执行多个插入语句
      for row in data_list:
        print(row)
        # 执行INSERT语句
        cursor.execute(insert_query, row)

      connection.commit()

  finally:
    print('write earthquake list done')


data = read_earthquake_xlsx('earthquake/earthquake.xls')
write_earthquake_list_to_db(data, connection)

connection.close()
