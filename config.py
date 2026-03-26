import pymysql
cursorclass=pymysql.cursors.DictCursor
DB_CONFIG={"host": "localhost", 
           "user": "root", 
           "password": "", 
           "database": "recommendation_system",
           "cursorclass":cursorclass}

