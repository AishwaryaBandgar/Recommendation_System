import pymysql
from config import DB_CONFIG

def get_connection():
    db = pymysql.connect(**DB_CONFIG)
    return db
