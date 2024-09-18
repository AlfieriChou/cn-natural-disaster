from bs4 import BeautifulSoup

from libs.html import get_html

base_url = 'https://tcdata.typhoon.org.cn/dlrdqx.html'


def get_tropical_cyclone_list():
  html = get_html(base_url)
  soup = BeautifulSoup(html, 'html.parser')
  table = soup.find(
    'table', class_='el-table el-table--border land-falling-table'
  )
  tbody = table.find('tbody')
  if tbody is None:
    return []

  # 初始化表格
  rows = []
  rowspan_map = {}

  # 遍历表格的行
  for row_idx, row in enumerate(tbody.find_all('tr')):
    cells = []
    col_idx = 0
    for cell in row.find_all(['td', 'th']):
      # 跳过由于rowspan占据的单元格
      while (row_idx, col_idx) in rowspan_map:
        cells.append(rowspan_map.pop((row_idx, col_idx)))
        col_idx += 1

      # 处理rowspan
      rowspan = int(cell.get('rowspan', 1))
      colspan = int(cell.get('colspan', 1))

      # 如果有rowspan，记录需要合并的行
      if rowspan > 1:
        for i in range(1, rowspan):
          rowspan_map[(row_idx + i, col_idx)] = cell.text.encode(
            'iso-8859-1'
          ).decode('UTF-8')

      # 处理colspan
      for i in range(colspan):
        cells.append(cell.text.encode('iso-8859-1').decode('UTF-8'))
        col_idx += 1

    rows.append(cells)

  return rows


def write_tropical_cyclone_list_to_db(list, connection):
  try:
    with connection.cursor() as cursor:
      # 创建表（如果尚未存在）
      cursor.execute("""
      CREATE TABLE IF NOT EXISTS tropical_cyclone (
        id VARCHAR(64) PRIMARY KEY,
        series VARCHAR(64) NOT NULL,
        code VARCHAR(32) NOT NULL,
        china_code VARCHAR(32) NOT NULL,
        english_name VARCHAR(32) NOT NULL,
        chinese_name VARCHAR(32) NOT NULL,
        land_count INT NOT NULL,
        land_index INT NOT NULL,
        land_area VARCHAR(32) NOT NULL,
        land_area_code VARCHAR(32) NOT NULL,
        land_level VARCHAR(32) NOT NULL,
        INDEX idx_id (id),
        INDEX idx_series (series),
        INDEX idx_code (code),
        INDEX idx_china_code (china_code),
        INDEX idx_english_name (english_name),
        INDEX idx_chinese_name (chinese_name),
        INDEX idx_land_count (land_count),
        INDEX idx_land_index (land_index),
        INDEX idx_land_area (land_area),
        INDEX idx_land_area_code (land_area_code),
        INDEX idx_land_level (land_level)
      )
      """)

      # 插入数据
      # 构建INSERT语句
      insert_query = """
        INSERT IGNORE INTO tropical_cyclone (
          id,
          series,
          code,
          china_code,
          english_name,
          chinese_name,
          land_count,
          land_index,
          land_area,
          land_area_code,
          land_level
        ) VALUES (
          %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
      """

      # 构建并执行多个插入语句
      for row in list:
        # 执行INSERT语句
        cursor.execute(insert_query, row)

      connection.commit()

  finally:
    print('write tropical cyclone list done')
