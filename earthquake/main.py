import pandas as pd
import pyexcel as p
import datetime

from libs.area import area_dict, area_list


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
        area = earthquake_list[6][0:2]
        if area not in area_list:
          continue
        area_code = area_dict[area]
        date = get_date_str_zero_timestamp(str(date_str))
        date_timestamp = get_date_str_timestamp(str(date_str))
        earthquake_list.insert(0, area_code)
        earthquake_list.insert(0, date)
        earthquake_list.insert(0, date_timestamp)
        print(earthquake_list)
        list.append(earthquake_list)

  return data_list


data = read_earthquake_xlsx('earthquake/earthquake.xls')
print(data)
