import numpy as np
import MySQLdb
import datetime
from PyQt5.QtWidgets import *

import constants

"""提供将上、下位机数据存入数据库的接口"""


def create_credibility_knowledge_table():
    db = MySQLdb.connect(host=constants.HOST, user=constants.USER, passwd=constants.PWD, db=constants.DB, port=3306,
                         charset='utf8')
    cursor = db.cursor()
    sql = """CREATE TABLE IF NOT EXISTS `credibility_knowledge` (
	`ID` INT AUTO_INCREMENT,
	`CONDITION` VARCHAR(256) NOT NULL,
	`CONCLUSION` VARCHAR(256) NOT NULL,
	`CONDITION_CREDIBILITY` DOUBLE NOT NULL,
	`KNOWLEDGE_CREDIBILITY` DOUBLE NOT NULL,
	`UPDATE_TIME` DATETIME NOT NULL,
	`UPDATE_PERSON` VARCHAR(32),
    PRIMARY KEY ( `ID` ) 
    ) DEFAULT CHARSET=UTF8"""
    cursor.execute(sql)
    db.close()


def num_of_record():
    db = MySQLdb.connect(host=constants.HOST, user=constants.USER, passwd=constants.PWD, db=constants.DB, port=3306,
                         charset='utf8')
    cursor = db.cursor()
    try:
        cursor.execute('SELECT COUNT(ID) FROM `credibility_knowledge`')
        res = cursor.fetchall()
        db.close()
        if res == ():
            return 0
        return int(res[0][0])
    except:
        print('获取记录数量失败')
        db.close()


def add_credibility_knowledge(cond, conc, cond_cred, know_cred, person=""):  # !new
    db = MySQLdb.connect(constants.HOST, constants.USER, constants.PWD, constants.DB, charset="utf8")
    cursor = db.cursor()
    sql_select = "select max(`ID`) from `credibility_knowledge`"
    cursor.execute(sql_select)
    res = cursor.fetchall()
    ID = 0
    if (res[0][0] != None):
        ID = int(res[0][0])
    sql_insert = ""
    coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    if person == "":
        sql_insert = f'INSERT INTO `credibility_knowledge` values({ID + 1},\'{cond}\',\'{conc}\',{cond_cred},{know_cred},\'{coolection_time}\',NULL)'
    else:
        sql_insert = f'INSERT INTO `credibility_knowledge` values({ID + 1},\'{cond}\',\'{conc}\',{cond_cred},{know_cred},\'{coolection_time}\',\'{person}\')'
    print(sql_insert)
    try:
        cursor.execute(sql_insert)
        db.commit()
        print("可信度知识添加成功!")
    except:
        db.rollback()
        print("可信度知识添加失败!")
    db.close()


def del_credibility_knowledge(type, content):  # type表示ID，条件，或者结论,界面中根据ID来删除
    sql = ""
    if type in ['CONDITION', 'CONCLUSION', 'UPDATE_PERSON']:
        sql = f'DELETE FROM `credibility_knowledge` WHERE `{type}` = \'{content}\''
    elif type == 'ID':
        sql = f'DELETE FROM `credibility_knowledge` WHERE `{type}` = {content}'
    else:
        print("删除所使用的条件出错!")
        return
    db = MySQLdb.connect(host=constants.HOST, port=3306, user=constants.USER, password=constants.PWD, db=constants.DB,
                         charset='utf8')
    cursor = db.cursor()
    judge = 0
    try:
        cursor.execute(sql)
        db.commit()
        judge = 1
        print(f'成功删除 {type} 为 {content} 的可信度知识!')
    except:
        db.rollback()
        print("删除失败!")
    db.close()
    if judge == 1:
        db = MySQLdb.connect(host=constants.HOST, port=3306, user=constants.USER, password=constants.PWD,
                             db=constants.DB, charset='utf8')
        cursor = db.cursor()
        try:
            cursor.execute(
                f'UPDATE `credibility_knowledge` SET ID = ID-1 WHERE ID >{content}')  # !这里因为界面根据ID删除，那么content一定是一个整数
            db.commit()
        except:
            db.rollback()
            print('未更新')


def update_credibility_knowledge(type1, content, type2, new_content):
    if (type1 not in ['ID', 'CONDITION', 'CONCLUSION', 'UPDATE_PERSON', 'UPDATE_TIME']):
        print("定位条件出错!")
        return
    if (type2 not in ['CONDITION', 'CONCLUSION', 'CONDITION_CREDIBILITY', 'KNOWLEDGE_CREDIBILITY', 'UPDATE_PERSON',
                      'ID', 'UPDATE_TIME']):
        print(f'可信度知识没有 {type2} 属性!')
        return
    if (type2 == 'ID'):
        print(f'{type2}无法修改!')
        return
    if (type2 == 'UPDATE_TIME'):
        print("UPDATE_TIME自动修改!")
        return
    db = MySQLdb.connect(host=constants.HOST, port=3306, user=constants.USER, password=constants.PWD, db=constants.DB,
                         charset='utf8')
    cursor = db.cursor()
    sql = ""
    coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    if (type2 in ['CONDITION', 'CONCLUSION', 'UPDATE_PERSON'] and type1 in ['CONDITION', 'CONCLUSION', 'UPDATE_PERSON',
                                                                            'UPDATE_TIME']):
        sql = f'UPDATE `credibility_knowledge` SET `{type2}` = \'{new_content}\',`UPDATE_TIME` = \'{coolection_time}\' WHERE `{type1}` = \'{content}\''
    elif (type2 in ['CONDITION_CREDIBILITY', 'KNOWLEDGE_CREDIBILITY'] and type1 in ['CONDITION', 'CONCLUSION',
                                                                                    'UPDATE_PERSON', 'UPDATE_TIME']):
        sql = f'UPDATE `credibility_knowledge` SET `{type2}` = {new_content},`UPDATE_TIME` = \'{coolection_time}\' WHERE `{type1}` = \'{content}\''
    elif (type2 in ['CONDITION', 'CONCLUSION', 'UPDATE_PERSON'] and type1 == 'ID'):
        sql = f'UPDATE `credibility_knowledge` SET `{type2}` = \'{new_content}\',`UPDATE_TIME` = \'{coolection_time}\' WHERE `{type1}` = {content}'
    elif (type2 in ['CONDITION_CREDIBILITY', 'KNOWLEDGE_CREDIBILITY'] and type1 == 'ID'):
        sql = f'UPDATE `credibility_knowledge` SET `{type2}` = {new_content},`UPDATE_TIME` = \'{coolection_time}\' WHERE `{type1}` = {content}'
    try:
        cursor.execute(sql)
        db.commit()
        print("修改成功!")
        return
    except:
        db.rollback()
        print("修改失败!")
    db.close()


def search_credibility_knowledge(type, content):
    if (type not in ['ID', 'CONDITION', 'CONCLUSION', 'UPDATE_PERSON', 'UPDATE_TIME', 'CONDITION_CREDIBILITY',
                     'KNOWLEDGE_CREDIBILITY', '']):
        print(f'可信度知识没有 {type} 属性!')
        return
    sql = ""
    if (type in ['CONDITION', 'CONCLUSION', 'UPDATE_PERSON', 'UPDATE_TIME']):
        sql = f'SELECT * FROM credibility_knowledge WHERE `{type}` = \'{content}\''
    else:
        sql = f'SELECT * FROM credibility_knowledge WHERE `{type}` = {content}'
    db = MySQLdb.connect(host=constants.HOST, port=3306, user=constants.USER, password=constants.PWD, db=constants.DB,
                         charset='utf8')
    cursor = db.cursor()
    if (type == '' and content == ''):
        try:
            cursor.execute('SELECT * FROM  `credibility_knowledge`')
            res = cursor.fetchall()
            if (res == ()):
                print("查询结果为空")
                db.close()
                return None
            for row in res:
                if (row != None):
                    print(row)
            db.close()
            return res
        except:
            print("查询失败!")
            db.close()
    else:
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            if (res == ()):
                print("查询结果为空")
                db.close()
                return None
            for row in res:
                if (row != None):
                    print(row)
            db.close()
            return res
        except:
            print("查询失败!")
            db.close()


def cre_db(host, user, pw, dbname):
    """
    创建数据库
    :param host: 主机
    :param user: 用户名
    :param pw: 密码
    :return: 建立的连接
    """
    cnt = MySQLdb.connect(host, user, pw)
    cursor = cnt.cursor()
    cursor.execute("DROP DATABASE IF EXISTS %s" % dbname)
    cursor.execute("CREATE DATABASE IF NOT EXISTS %s" % dbname)
    return cnt


def init(host, user, pw, dbname):
    """
    initialize database
    :param host: host name, string
    :param user: user name, string
    :param pw: password, string
    :param dbname: database name, string
    :return:
    """
    cnt = cre_db(host, user, pw, dbname)
    csr = cnt.cursor()
    csr.execute("USE " + dbname)
    ctine = "CREATE TABLE IF NOT EXISTS "
    csr.execute(ctine + "progress_rate"
                        "(direction char(2) NOT NULL,progress_rate float NOT NULL,"
                        "updtime datetime,"
                        "administrator varchar(32) default \"%s\")" % user)
    csr.execute(ctine + "number"
                        "(direction char(2) NOT NULL, number int NOT NULL,"
                        "updtime datetime,"
                        "administrator varchar(32) default \"%s\")" % user)
    csr.execute(ctine + "seconds"
                        "(seconds int NOT NULL,"
                        "updtime datetime,"
                        "administrator varchar(32) default \"%s\")" % user)
    csr.execute(ctine + "feedback"
                        "(seconds int NOT NULL,"
                        "updtime datetime,"
                        "administrator varchar(32) default \"%s\")" % user)
    csr.execute(ctine + "Sum_LingV"
                        "(LingV varchar(32) NOT NULL,"
                        "type varchar(32) NOT NULL,"
                        "primary key(LingV))")
    csr.execute(ctine + "Sum_FuzCpt"  # summary fuzzy concept table
                        "(FuzCpt varchar(32) NOT NULL,"
                        "LingV varchar(32) NOT NULL,"  # Linguistic Variable
                        "primary key(FuzCpt),"
                        "foreign key(LingV) references Sum_LingV(LingV))")
    csr.execute(ctine + "fuzzy_knowledge"
                        "(ID int NOT NULL AUTO_INCREMENT,"
                        "CondV varchar(32) NOT NULL,"  # Conditional Variable
                        "FuzCptA varchar(32) NOT NULL,"  # Fuzzy Concept A
                        "ConcV varchar(32) NOT NULL,"  # Conclusion Variable
                        "FuzCptB varchar(32) NOT NULL,"  # Fuzzy Concept B
                        "CF numeric(2,1) NOT NULL,"
                        "lambda numeric(2,1) NOT NULL,"
                        "updtime datetime,"
                        "administrator varchar(32) default \"%s\","
                        "primary key(ID),"
                        "foreign key(CondV) references Sum_LingV(LingV),"
                        "foreign key(FuzCptA) references Sum_FuzCpt(FuzCpt),"
                        "foreign key(ConcV) references Sum_LingV(LingV),"
                        "foreign key(FuzCptB) references Sum_FuzCpt(FuzCpt))" % user
                )
    cnt.close()


def calmat(x, y, muA, muB):
    """
    计算模糊矩阵
    :param x: 语言变量A的论域
    :param y: 语言变量B的论域
    :param muA: 语言变量A的模糊概念的隶属函数
    :param muB: 语言变量B的模糊概念的隶属函数
    :return: 模糊矩阵
    """
    R = np.zeros((len(x), len(y)))
    for i in range(len(x)):
        for j in range(len(y)):
            R[i, j] = np.maximum(np.minimum(muA(x[i]), muB(y[j])), 1 - muA(x[i]))
    return R


def connect_db(host, user, pw, dbname):
    """
    创建数据库
    :param host: 主机
    :param user: 用户名
    :param pw: 密码
    :param dbname: 数据库名称
    :return: 建立的连接
    """
    conn = MySQLdb.connect(host, user, pw)
    cursor = conn.cursor()
    cursor.execute("use %s" % dbname)
    return conn


def close_db(conn):
    """
    关闭数据库连接
    :param conn: 数据库连接
    :return:
    """
    conn.close()


def safe_commit(conn):
    """
    数据库提交
    :param conn: 数据库连接
    :return:
    """
    try:
        conn.commit()
    except:
        conn.rollback()
        print("ERROR AT COMMIT STAGE!!!")


def insert_fuzzy_set(conn, dbname, var, var_list, cpt, cpt_func):
    csr = conn.cursor()
    csr.execute("USE " + dbname)
    create_func_table(conn, dbname, var, var_list, [cpt], [[cpt_func(x) for x in var_list]])
    # cnt = csr.execute("SELECT COLUMN_NAME from information_schema.columns where"
    #                   " table_name ='fuccy_concept_%s' and column_name = "
    #                   "'%s'" % (var[0], cpt))

    try:
        csr.execute("ALTER TABLE fuzzy_concept_{}".format(var[0]) + " ADD " + cpt + " float not null")
        for x in var_list:
            csr.execute("UPDATE fuzzy_concept_{}".format(var[0]) + " SET " + cpt
                        + "={}".format(cpt_func(x)) + "where value={}".format(x))
    except:
        pass


def fuzzy_knowledge_insert(conn, dbname, var1, var1_list, cpt1, cpt1_func, var2, var2_list, cpt2, cpt2_func, cf, l,
                           id=None):
    """
    知识添加
    :param conn: 数据库连接
    :param dbname: 数据库名
    :param var1: (str, str) (变量,type)
    :param var1_list: [val, val, val...] 变量论域
    :param cpt1: str 第一个模糊概念
    :param cpt1_func: func 第一个模糊概念的隶属函数
    :param var2:
    :param var2_list:
    :param cpt2:
    :param cpt2_func:
    :param cf: cf值
    :param l: lambda值
    :param id: 待插入的知识的id值，仅修改知识时使用，可确保不会重复
    :return:
    """

    # add relationship matrix
    mat = calmat(np.array(var1_list), np.array(var2_list), cpt1_func, cpt2_func)
    csr = conn.cursor()
    csr.execute("use {}".format(dbname))
    csr.execute("DROP TABLE IF EXISTS matrix_{}_{}".format(cpt1, cpt2))
    csr.execute("CREATE TABLE IF NOT EXISTS matrix_{}_{}".format(cpt1, cpt2) +
                " (val1 {},val2 {}, R float,primary key(val1, val2))".format(var1[1], var2[1])
                )
    # add linguistic variable
    add_linguistic_variable(conn, dbname, var1)
    add_linguistic_variable(conn, dbname, var2)
    # add fuzzy concept
    add_fuzzy_concept(conn, dbname, cpt1, var1[0])
    add_fuzzy_concept(conn, dbname, cpt2, var2[0])
    # create variable table
    create_func_table(conn, dbname, var1, var1_list, [cpt1], [[cpt1_func(x) for x in var1_list]])
    create_func_table(conn, dbname, var2, var2_list, [cpt2], [[cpt2_func(x) for x in var2_list]])
    insert_fuzzy_set(conn, dbname, var1, var1_list, cpt1, cpt1_func)
    insert_fuzzy_set(conn, dbname, var2, var2_list, cpt2, cpt2_func)
    for i in range(len(var1_list)):
        for j in range(len(var2_list)):
            r_val = mat[i, j]
            try:
                csr.execute("INSERT INTO matrix_{}_{}".format(cpt1, cpt2) + " VALUES({},{},{})".format(var1_list[i],
                                                                                                       var2_list[j],
                                                                                                       r_val))
            except:
                print("this matrix_{}_{} have inserted before".format(cpt1, cpt2))

    # add knowledge
    cnt = csr.execute("SELECT * FROM fuzzy_knowledge WHERE FuzCptA = '{}' and FuzCptB = '{}'".format(cpt1, cpt2))
    if not cnt:
        if id is not None:
            csr.execute(
                "INSERT INTO fuzzy_knowledge(ID,CondV, FuzCptA, ConcV, FuzCptB, CF, lambda, updtime, administrator) "
                "VALUES( "
                "{},'{}','{}','{}','{}',{},{},now(),'admin')".format(id,
                                                                     var1[0], cpt1, var2[0], cpt2, cf, l)
            )
        else:
            csr.execute(
                "INSERT INTO fuzzy_knowledge(CondV, FuzCptA, ConcV, FuzCptB, CF, lambda, updtime, administrator) "
                "VALUES( "
                "'{}','{}','{}','{}',{},{},now(),'admin')".format(
                    var1[0], cpt1, var2[0], cpt2, cf, l)
            )
    else:
        print("this knowledge {} {} has inserted before".format(cpt1, cpt2))
        return -1
    return 1
    safe_commit(conn)


def _fkchange(i, nd, knowledge):
    """
    修改模糊知识的辅助函数，用于修改模糊知识的某一部分
    :param i: 要修改的部分在知识中的索引，int
    :param nd: 要修改的部分的新值
    :param knowledge: 待修改的知识 list
    :return:
    """
    if nd is not None:
        knowledge[i] = nd


def check_domin(conn, dbname, var, var_list, dvar):
    """
    若语言变量已在数据库中，判断新论域var_list与原论域是否相同，若不同，返回原论域
    :param conn: 数据库连接
    :param dbname: 数据库名
    :param var: （语言变量，变量论域类型） (str,str)
    :param var_list: list 语言变量论域
    :param dvar: 语言变量 str
    :return:
    """
    if var[0] == dvar:
        csr = conn.cursor()
        csr.execute("USE " + dbname)
        csr.execute("SELECT VALUE from fuzzy_concept_" + var[0])
        domin = np.array(csr.fetchall()).reshape(1, -1)[0].tolist()
        if set(var_list) != set(domin):
            print("You can't change the domin of linguistic variable " + var[0])
            var_list = domin
    return var_list


def fuzzy_knowledge_change(conn, dbname, id, var1_list, cpt1_func, var2_list, cpt2_func, var1, var2, cpt1=None,
                           cpt2=None, cf=None, lmd=None):
    """
    修改给定id的模糊知识
    :param conn: 数据库连接
    :param dbname: 数据库名
    :param id: 待修改的模糊知识的id
    :param var1: (str, str) (变量,type)
    :param var1_list: [val, val, val...] 变量论域
    :param cpt1: str 第一个模糊概念
    :param cpt1_func: func 第一个模糊概念的隶属函数
    :param var2:
    :param var2_list:
    :param cpt2:
    :param cpt2_func:
    :param cf: cf值
    :param l: lambda值
    :return:
    """
    print("change knowledge ID={}".format(id))
    knowledge = fuzzy_knowledge_show(conn, dbname, id)
    if knowledge == None:
        return -1
    knowledge = list(knowledge)
    new_knowledge_para = [id, var1, cpt1, var2, cpt2, cf, lmd]
    fuzzy_knowledge_delete(conn, dbname, id)
    var1_list = check_domin(conn, dbname, var1, var1_list, knowledge[1])
    var2_list = check_domin(conn, dbname, var2, var2_list, knowledge[3])
    for i in range(len(new_knowledge_para)):
        _fkchange(i, new_knowledge_para[i], knowledge)
    ind = [2, 4, 6, 8]
    v = [var1_list, cpt1_func, var2_list, cpt2_func]
    for i in ind:
        knowledge.insert(i, v[int(i / 2 - 1)])
    knowledge[-2] = id

    fuzzy_knowledge_insert(conn, dbname, *knowledge[1:-1])
    return 1


def fuzzy_knowledge_find(conn, dbname, cond_a, cond_b=None):
    """
    知识查找
    :param conn: 数据库连接
    :param dbname: 数据库名
    :param cond_a: 条件变量
    :param cond_b: 结论变量(可不填)
    :return:
    """
    select_sentence = "SELECT * FROM fuzzy_knowledge WHERE CondV = '{}'".format(cond_a)
    if cond_b:
        select_sentence += " and ConcV = '{}'".format(cond_b)
    csr = conn.cursor()
    csr.execute("use {}".format(dbname))
    cnt = csr.execute(select_sentence)
    print("have found {} knowledges".format(cnt))

    if cnt:
        datas = csr.fetchall()
        print("(ID, CondV, FuzCptA, ConcV, FuzCptB, CF, lambda, updtime, administrator)")
        for i in range(cnt):
            print(datas[i])
    return datas


def fuzzy_knowledge_show(conn, dbname, id):
    """
    根据id查找知识
    :param conn: 数据库连接
    :param dbname: 数据库名
    :param id: 主码
    :return:
    """
    csr = conn.cursor()
    csr.execute("use {}".format(dbname))
    csr.execute("select * from fuzzy_knowledge where ID={}".format(id))
    data = csr.fetchone()
    if data:
        print("(ID, CondV, FuzCptA, ConcV, FuzCptB, CF, lambda, updtime, administrator)")
        print(data)
    else:
        print("can not find knowledge ID={}".format(id))
    return data


def fuzzy_knowledge_delete(conn, dbname, id):
    """
    删除某条知识
    :param conn: 数据库连接
    :param dbname: 数据库名
    :param id: 主码
    :return:
    """
    csr = conn.cursor()
    csr.execute("use {}".format(dbname))
    cnt = csr.execute("select * from fuzzy_knowledge where ID={}".format(id))
    if cnt:
        data = csr.fetchone()
        csr.execute("DELETE FROM fuzzy_knowledge WHERE ID={}".format(id))
        print("delete knowledge ID={}".format(id))
        csr.execute("DROP TABLE matrix_{}_{}".format(data[2], data[4]))
        print("DROP TABLE matrix_{}_{}".format(data[2], data[4]))
    safe_commit(conn)
    return cnt


def create_func_table(conn, dbname, var, var_list, cpt_list, cpt_data_list):
    """
    创建隶属函数表
    :param conn: 数据库连接
    :param dbname: 数据库名
    :param var: (str,str) (变量,type)
    :param var_list: [val, val, val...] 变量论域
    :param cpt_list: [str, str, str...] 变量对应的所有模糊概念
    :param cpt_data_list: [[val...], [val...], [val...] ...] 每个模糊概念对应的隶属度列表
    :return:
    """
    csr = conn.cursor()
    csr.execute("use {}".format(dbname))
    ctine = "CREATE TABLE IF NOT EXISTS "
    table_name = "fuzzy_concept_{}".format(var[0])
    value_list_str = ""
    for cpt in cpt_list:
        value_list_str += "{} float NOT NULL,".format(cpt)
    csr.execute(ctine + table_name +
                "(value {},".format(var[1]) + value_list_str +
                "primary key(value))")
    for i in range(len(var_list)):
        values = " VALUES({}".format(var_list[i])
        for item in range(len(cpt_list)):
            values += ",{}".format(cpt_data_list[item][i])
        values += ")"
        try:
            csr.execute("INSERT INTO " + table_name + values)
        except:
            # print("you have insert the data before")
            return
    safe_commit(conn)


def add_linguistic_variable(conn, dbname, var_pair):
    """
    添加模糊变量表
    :param conn: 数据库连接
    :param dbname: 数据库名
    :param var_pair: (str, str) (变量,type)
    :return:
    """
    csr = conn.cursor()
    csr.execute("use {}".format(dbname))
    cnt = csr.execute("SELECT LingV FROM sum_lingv WHERE Lingv = '%s'" % var_pair[0])
    if not cnt:
        try:
            csr.execute("INSERT INTO Sum_LingV VALUES('{}','{}')".format(var_pair[0], var_pair[1]))
        except:
            print("this linguistic variable:{} has inserted before".format(var_pair))
            return
    safe_commit(conn)


def add_fuzzy_concept(conn, dbname, fuzzy_concept, var_name):
    """
    添加模糊概念
    :param conn: 数据库连接
    :param dbname: 数据库名
    :param fuzzy_concept: str 模糊概念
    :param var_name: str 变量名
    :return:
    """
    csr = conn.cursor()
    csr.execute("use {}".format(dbname))
    cnt = csr.execute("SELECT LingV FROM sum_fuzcpt WHERE FuzCpt = '%s'" % fuzzy_concept)
    if not cnt:
        try:
            csr.execute("INSERT INTO Sum_FuzCpt VALUES('{}','{}')".format(fuzzy_concept, var_name))
        except:
            print("this fuzzy concept:{} has inserted before".format(fuzzy_concept))
            return
    safe_commit(conn)


def show_all_fuzzy_knowledge(conn, dbname):
    csr = conn.cursor()
    csr.execute("use {}".format(dbname))
    csr.execute("select * from fuzzy_knowledge")
    return csr.fetchall()


def fuzzy_insert_all(host, user, pw, dbname):
    """
    添加所有知识
    :param host: str 主机
    :param user: str 用户
    :param pw: str 密码
    :param dbname: str 数据库名
    :return:
    """
    conn = MySQLdb.connect(host, user, pw)

    # variable
    var_time = ("light_time", "int")
    time_list = np.arange(5, 110, 2)
    var_car_traffic = ("traffic", "int")
    traffic_list = np.arange(21)

    add_linguistic_variable(conn, dbname, var_time)
    add_linguistic_variable(conn, dbname, var_car_traffic)

    # Fuzzy Concept
    # for traffic
    sigma = 5
    lambda_large_5 = lambda inp: 1 if inp > 20 else (0 if inp < 15 else (inp - 15) / sigma)
    large_5 = "large_5"
    large_traffic_5 = [lambda_large_5(d) for d in traffic_list]

    lambda_large_4 = lambda inp: (1 - abs(inp - 15) / sigma) if abs(inp - 15) < sigma else 0
    large_4 = "large_4"
    large_traffic_4 = [lambda_large_4(d) for d in traffic_list]

    lambda_large_3 = lambda inp: (1 - abs(inp - 10) / sigma) if abs(inp - 10) < sigma else 0
    large_3 = "large_3"
    large_traffic_3 = [lambda_large_3(d) for d in traffic_list]

    lambda_large_2 = lambda inp: (1 - abs(inp - 5) / sigma) if abs(inp - 5) < sigma else 0
    large_2 = "large_2"
    large_traffic_2 = [lambda_large_2(d) for d in traffic_list]

    lambda_large_1 = lambda inp: 1 if inp <= 0 else (0 if inp > 5 else (5 - inp) / sigma)
    large_1 = "large_1"
    large_traffic_1 = [lambda_large_1(d) for d in traffic_list]

    # for light_time
    lambda_long_5 = lambda inp: 0 if inp < 80 else (1 if inp >= 100 else (inp - 80) / 20)
    long_5 = "long_5"
    long_time_5 = [lambda_long_5(d) for d in time_list]

    lambda_long_4 = lambda inp: (100 - inp) / 20 if 100 > inp >= 80 else ((inp - 60) / 20 if 80 > inp >= 60 else 0)
    long_4 = "long_4"
    long_time_4 = [lambda_long_4(d) for d in time_list]

    lambda_long_3 = lambda inp: (80 - inp) / 20 if 80 > inp >= 60 else ((inp - 40) / 20 if 60 > inp >= 40 else 0)
    long_3 = "long_3"
    long_time_3 = [lambda_long_3(d) for d in time_list]

    lambda_long_2 = lambda inp: (60 - inp) / 20 if 60 > inp >= 40 else ((inp - 20) / 20 if 40 > inp >= 20 else 0)
    long_2 = "long_2"
    long_time_2 = [lambda_long_2(d) for d in time_list]

    lambda_long_1 = lambda inp: 1 if inp <= 20 else (0 if inp > 40 else (40 - inp) / 20)
    long_1 = "long_1"
    long_time_1 = [lambda_long_1(d) for d in time_list]

    # create the table of {time} and {traffic}
    long_list = [long_5, long_4, long_3, long_2, long_1]
    long_time_list = [long_time_5, long_time_4, long_time_3, long_time_2, long_time_1]
    long_time_func = [lambda_long_5, lambda_long_4, lambda_long_3, lambda_long_2, lambda_long_1]
    create_func_table(conn, constants.DB, var_time, time_list, long_list, long_time_list)  # create func table
    for fuzzy_concept in long_list:
        add_fuzzy_concept(conn, dbname, fuzzy_concept, var_time[0])  # create concept table

    large_list = [large_5, large_4, large_3, large_2, large_1]
    large_traffic_list = [large_traffic_5, large_traffic_4, large_traffic_3, large_traffic_2, large_traffic_1]
    large_traffic_func = [lambda_large_5, lambda_large_4, lambda_large_3, lambda_large_2, lambda_large_1]
    create_func_table(conn, constants.DB, var_car_traffic, traffic_list, large_list, large_traffic_list)
    for fuzzy_concept in large_list:
        add_fuzzy_concept(conn, dbname, fuzzy_concept, var_car_traffic[0])

    for i in range(len(large_list)):
        curr_large = large_list[i]
        curr_large_func = large_traffic_func[i]
        curr_long = long_list[i]
        curr_long_func = long_time_func[i]

        # add knowledge
        fuzzy_knowledge_insert(conn, dbname, var_car_traffic, traffic_list, curr_large, curr_large_func, var_time,
                               time_list,
                               curr_long, curr_long_func, 0.8, 0.6)

    close_db(conn)


if __name__ == '__main__':
    y = np.arange(0, 21, 1)
    x = np.arange(0, 1.1, .1)
    # init database
    init(constants.HOST, constants.USER, constants.PWD, constants.DB)

    # 可信度知识测试
    print("Test credibillity knowledge!")
    # test1
    create_credibility_knowledge_table()
    add_credibility_knowledge("The traffic lights do not work", "Traffic light failure", 0.1, 0.5, 'Jason')
    add_credibility_knowledge("The traffic lights are on", "The traffic lights work normally", 0.9, 0.9, 'Jason')
    add_credibility_knowledge("No vehicle detected in 24 hours", "Abnormal sensor", 0.01, 0.99, 'Jason')
    add_credibility_knowledge("More than 100 vehicles pass in 15 seconds", "Sensor failure", 0.01, 0.99, 'Jason')

    # test2
    update_credibility_knowledge("CONDITION", "The traffic lights do not work", "CONDITION_CREDIBILITY", 0.2)
    # test3
    del_credibility_knowledge("CONCLUSION", "Sensor failure")
    # test4
    search_credibility_knowledge('CONDITION', 'The traffic lights are on')
    # test5
    search_credibility_knowledge('', '')
    print("Credibillity knowledge test ends!")

    # 测试模糊知识
    print("Test Fuzzy knowledge!")
    # insert knowledge 增
    fuzzy_insert_all(constants.HOST, constants.USER, constants.PWD, constants.DB)
    conn = MySQLdb.connect(constants.HOST, constants.USER, constants.PWD)

    # 查
    data_list = fuzzy_knowledge_find(conn, constants.DB, "traffic")
    fuzzy_knowledge_show(conn, constants.DB, data_list[-1][0])

    # 删  删前先查找
    # fuzzy_knowledge_delete(conn, constants.DB", data_list[0][0])
    # fuzzy_knowledge_show(conn, constants.DB", data_list[0][0])
    #
    # # 改 = 先删再添加
    # fuzzy_knowledge_change(conn, constants.DB", data_list[1][0], var1=("traffic1", "int"), var1_list=[2, 4, 6, 8, 10],
    #                        cpt1="large_6",
    #                        cpt1_func=lambda x: x / 10, var2=("light_time", "int"), var2_list=[10, 20, 50, 120],
    #                        cpt2="long_6", cpt2_func=lambda x: x / 120, cf=0,
    #                        lmd=1)
    # fuzzy_knowledge_show(conn, constants.DB", data_list[1][0])
    print("Fuzzy knowledge test ends!")
    # ppt上计算关系矩阵例子
    # foo1 = lambda inp: np.array([1, 0.8, 0.5, 0, 0])[inp]
    # foo2 = lambda inp: np.array([0, 0, 0.5, 0.8, 1])[inp]
    # data = calmat([0, 1, 2, 3, 4], [0, 1, 2, 3, 4], foo1, foo2)
    # print("The instance of calculating fuzzy matrix in PPT:")
    # print(data)

    print("test end")
