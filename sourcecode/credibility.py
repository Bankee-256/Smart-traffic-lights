import MySQLdb
import datetime
import build_db
import numpy as np

import constants


def create_truth_table():
    db = MySQLdb.connect(host=constants.HOST, port=3306, user=constants.USER, password=constants.PWD, db=constants.DB)
    cursor = db.cursor()
    sql = """CREATE TABLE IF NOT EXISTS `truth` (
	`ID` INT AUTO_INCREMENT,
	`ATTRIBUTE` VARCHAR(256) NOT NULL,
	`RELIABILITY` DOUBLE NOT NULL,
	`UPDATE_TIME` DATETIME NOT NULL,
	`UPDATE_PERSON` VARCHAR(32),
    PRIMARY KEY ( `ID` ) 
    ) DEFAULT CHARSET=UTF8"""
    cursor.execute(sql)
    db.close()


def add_truth(attr, rel, person=""):  # !new
    db = MySQLdb.connect(constants.HOST, constants.USER, constants.PWD, constants.DB)
    cursor = db.cursor()
    sql_select = "select max(`ID`) from `truth`"
    cursor.execute(sql_select)
    res = cursor.fetchall()
    ID = 0
    if (res[0][0] != None):
        ID = int(res[0][0])
    sql_insert = ""
    coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    if person == "":
        sql_insert = f'INSERT INTO `truth` values({ID + 1},\'{attr}\',{rel},\'{coolection_time}\',NULL)'
    else:
        sql_insert = f'INSERT INTO `truth` values({ID + 1},\'{attr}\',{rel},\'{coolection_time}\',\'{person}\')'
    print(sql_insert)
    try:
        cursor.execute(sql_insert)
        db.commit()
        print("事实添加成功!")
    except:
        db.rollback()
        print("事实添加失败!")
    db.close()


def del_truth(type, content):  # type表示ID，属性
    sql = ""
    if type in ['ID', 'ATTRIBUTE']:
        sql = f'DELETE FROM `truth` WHERE `{type}` = {content}'
    else:
        print("删除所使用的条件出错!")
        return
    db = MySQLdb.connect(host=constants.HOST, port=3306, user=constants.USER, password=constants.PWD, db=constants.DB)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
        print(f'成功删除 {type} 为 {content} 的事实!')
    except:
        db.rollback()
        print("删除失败!")
    db.close()


def update_truth(type1, content, type2, new_content):
    if (type1 not in ['ID', 'ATTRIBUTE', 'UPDATE_PERSON', 'UPDATE_TIME']):
        print("定位条件出错!")
        return
    if (type2 not in ['ATTRIBUTE', 'RELIABILITY', 'UPDATE_PERSON', 'ID', 'UPDATE_TIME']):
        print(f'事实没有 {type2} 属性!')
        return
    if (type2 == 'ID'):
        print(f'{type2}无法修改!')
        return
    if (type2 == 'UPDATE_TIME'):
        print("UPDATE_TIME自动修改!")
        return
    db = MySQLdb.connect(host=constants.HOST, port=3306, user=constants.USER, password=constants.PWD, db=constants.DB)
    cursor = db.cursor()
    sql = ""
    coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    if (type2 in ['ATTRIBUTE', 'UPDATE_PERSON'] and type1 in ['ATTRIBUTE', 'UPDATE_PERSON', 'UPDATE_TIME']):
        sql = f'UPDATE `truth` SET `{type2}` = \'{new_content}\',`UPDATE_TIME` = \'{coolection_time}\' WHERE `{type1}` = \'{content}\''
    elif (type2 == 'RELIABILITY' and type1 in ['ATTRIBUTE', 'UPDATE_PERSON', 'UPDATE_TIME']):
        sql = f'UPDATE `truth` SET `{type2}` = {new_content},`UPDATE_TIME` = \'{coolection_time}\' WHERE `{type1}` = \'{content}\''
    elif (type2 in ['ATTRIBUTE', 'UPDATE_PERSON'] and type1 == 'ID'):
        sql = f'UPDATE `truth` SET `{type2}` = \'{new_content}\',`UPDATE_TIME` = \'{coolection_time}\' WHERE `{type1}` = {content}'
    elif (type2 == 'RELIABILITY' and type1 == 'ID'):
        sql = f'UPDATE `truth` SET `{type2}` = {new_content},`UPDATE_TIME` = \'{coolection_time}\' WHERE `{type1}` = {content}'
    try:
        cursor.execute(sql)
        db.commit()
        print("修改成功!")
    except:
        db.rollback()
        print("修改失败!")
    db.close()


def search_truth(type, content):
    if (type not in ['ID', 'ATTRIBUTE', 'RELIABILITY', 'UPDATE_PERSON', 'UPDATE_TIME', '']):
        print(f'事实没有 {type} 属性!')
        return
    sql = ""
    if (type in ['ATTRIBUTE', 'RELIABILITY', 'UPDATE_PERSON', 'UPDATE_TIME']):
        sql = f'SELECT * FROM truth WHERE `{type}` = \'{content}\''
    else:
        sql = f'SELECT * FROM truth WHERE `{type}` = {content}'
    db = MySQLdb.connect(host=constants.HOST, port=3306, user=constants.USER, password=constants.PWD, db=constants.DB)
    cursor = db.cursor()
    if (type == '' and content == ''):
        try:
            cursor.execute('SELECT * FROM `truth`')
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


def rel_infer(car_num):
    if car_num >= 0 and car_num <= 5:
        res1 = search_truth("ATTRIBUTE", "0 to 5 cars passed in 15 seconds")
        if res1 == ():
            return '0 to 5 cars passed in 15 seconds'
        res2 = build_db.search_credibility_knowledge("CONDITION", "0 to 5 cars passed in 15 seconds")
        if res2 == ():
            return 'no knowledge'
        rel = float(res1[0][-3])
        lamb = float(res2[0][-3])
        CF_E = float(res2[0][-4])
        if CF_E > lamb:
            CF_H = CF_E * rel
            if search_truth("ATTRIBUTE", "Green light on for 8 second") == 0:
                add_truth("Green light on for 8 second", CF_H, "Jz")
            else:
                update_truth("ATTRIBUTE", "Green light on for 8 second", "RELIABILITY", CF_H)
            return 8
        return 'fail'
    elif car_num > 5 and car_num <= 10:
        res1 = search_truth("ATTRIBUTE", "5 to 10 cars passed in 15 seconds")
        if res1 == ():
            return '5 to 10 cars passed in 15 seconds'
        res2 = build_db.search_credibility_knowledge("CONDITION", "5 to 10 cars passed in 15 seconds")
        if res2 == ():
            return 'no knowledge'
        rel = float(res1[0][-3])
        lamb = float(res2[0][-3])
        CF_E = float(res2[0][-4])
        if CF_E > lamb:
            CF_H = CF_E * rel
            if search_truth("ATTRIBUTE", "Green light on for 16 second") == 0:
                add_truth("Green light on for 16 second", CF_H, "Jz")
            else:
                update_truth("ATTRIBUTE", "Green light on for 16 second", "RELIABILITY", CF_H)
            return 16
        return 'fail'
    elif car_num > 10 and car_num <= 15:
        res1 = search_truth("ATTRIBUTE", "10 to 15 cars passed in 15 seconds")
        if res1 == ():
            return '10 to 15 cars passed in 15 seconds'
        res2 = build_db.search_credibility_knowledge("CONDITION", "10 to 15 cars passed in 15 seconds")
        if res2 == ():
            return 'no knowledge'
        rel = float(res1[0][-3])
        lamb = float(res2[0][-3])
        CF_E = float(res2[0][-4])
        if CF_E > lamb:
            CF_H = CF_E * rel
            if search_truth("ATTRIBUTE", "Green light on for 24 second") == 0:
                add_truth("Green light on for 24 second", CF_H, "Jz")
            else:
                update_truth("ATTRIBUTE", "Green light on for 24 second", "RELIABILITY", CF_H)
            return 24
        return 'fail'
    elif car_num > 15:
        res1 = search_truth("ATTRIBUTE", "More than 15 cars passed in 15 seconds")
        if res1 == ():
            return 'More than 15 cars passed in 15 seconds'
        res2 = build_db.search_credibility_knowledge("CONDITION", "More than 15 cars passed in 15 seconds")
        if res2 == ():
            return 'no knowledge'
        rel = float(res1[0][-3])
        lamb = float(res2[0][-3])
        CF_E = float(res2[0][-4])
        if CF_E > lamb:
            CF_H = CF_E * rel
            if search_truth("ATTRIBUTE", "Green light on for 30 second") == 0:
                add_truth("Green light on for 30 second", CF_H, "Jz")
            else:
                update_truth("ATTRIBUTE", "Green light on for 30 second", "RELIABILITY", CF_H)
            return 30
        return 'fail'
    else:
        print("通过的车辆数不可能小于0")
        return 0


def explain(light_time):
    conclusion = "Green light on for " + str(light_time) + " second"
    res = build_db.search_credibility_knowledge("CONCLUSION", conclusion)
    if res == ():
        return "THIS COULD NOT BE EXPLAINED!!!"
    return "Green light on for " + str(light_time) + " second, because " + res[0][1]


if (__name__ == "__main__"):
    # 可信度知识测试
    print("Test credibillity knowledge!")
    build_db.init(constants.HOST, constants.USER, constants.PWD, constants.DB)
    build_db.init_credibility()
    print(explain(8))
    print(explain(16))
    print(explain(24))
    print(explain(30))
    print(explain(-30))
    print(explain(30.1))
    print(explain(1))
