import pymysql

mysql_config = {
  'host': '127.0.0.1',
  'user': 'root',
  'password': 'alfieri',
  'database': 'test',
}

# 定义MySQL数据库连接
connection = pymysql.connect(
  host=mysql_config['host'],
  user=mysql_config['user'],
  password=mysql_config['password'],
  database=mysql_config['database'],
  charset='utf8mb4',
  cursorclass=pymysql.cursors.DictCursor,
)
