import MySQLdb
import datetime
import build_db
import numpy as np

import constants


def create_statistic_table():
    db = MySQLdb.connect(host=constants.HOST, port=constants.PORT, user=constants.USER, password=constants.PWD,
                         db=constants.DB)
    cursor = db.cursor()
    sql = """CREATE TABLE IF NOT EXISTS `statistic` (
	`ID` INT AUTO_INCREMENT,
	`CARS_WE` INT NOT NULL,
	`CARS_NS` INT NOT NULL,
	`LIGHT_NS` INT NOT NULL,
	`LIGHT_WE` INT NOT NULL,
	`UPDATE_TIME` DATETIME NOT NULL,
    PRIMARY KEY ( `ID` ) 
    ) DEFAULT CHARSET=UTF8"""
    cursor.execute(sql)
    db.close()


def add_statistic(cars_we, cars_ns, light_we, light_ns):  # !new
    db = MySQLdb.connect(constants.HOST, constants.USER, constants.PWD, constants.DB)
    cursor = db.cursor()
    sql_select = "select max(`ID`) from `statistic`"
    cursor.execute(sql_select)
    res = cursor.fetchall()
    ID = 0
    if (res[0][0] != None):
        ID = int(res[0][0])
    sql_insert = ""
    coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    sql_insert = f'INSERT INTO `statistic` values({ID + 1},\'{cars_we}\',\'{cars_ns}\',\'{light_we}\',{light_ns},\'{coolection_time}\')'
    print(sql_insert)
    try:
        cursor.execute(sql_insert)
        db.commit()
        print("添加成功!")
    except:
        db.rollback()
        print("添加失败!")
    db.close()


def search_statistic(type, content1, content2):
    if (type not in ['ID', 'UPDATE_TIME', '']):
        print(f'没有 {type} 属性!')
        return
    sql = ""
    sql = f'SELECT * FROM statistic WHERE `{type}` >= \'{content1}\' AND `{type}` <= \'{content2}\''
    db = MySQLdb.connect(host=constants.HOST, port=constants.PORT, user=constants.USER, password=constants.PWD,
                         db=constants.DB)
    cursor = db.cursor()
    if (type == ''):
        try:
            cursor.execute('SELECT * FROM `statistic`')
            res = cursor.fetchall()
            for row in res:
                if (row != None):
                    print(row)
            if (res == ()):
                print("查询结果为空")
            db.close()
            return res
        except:
            print("查询失败!")
            db.close()
    else:
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            for row in res:
                if (row != None):
                    print(row)
            if (res == ()):
                print("查询结果为空")
            db.close()
            return res
        except:
            print("查询失败!")
            db.close()
