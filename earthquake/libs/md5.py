import hashlib


def md5(str):
  md = hashlib.md5()
  md.update(str.encode('utf-8'))
  md5_str = md.hexdigest()
  return md5_str
