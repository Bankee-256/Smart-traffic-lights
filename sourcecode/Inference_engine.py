import constants

import numpy as np
import MySQLdb
import time
import datetime
import os

CONCEPT_START = "START"


def get_file_prefix():
    """获得有效的文件前缀名"""
    from datetime import datetime
    now = datetime.now()
    return "{}_{}_{}".format(now.year, now.month, now.day)


def init_file():
    for i in ["_enfuzzy.csv", "_defuzzy.csv", "_record.csv"]:
        if not os.path.exists(get_file_prefix() + i):
            with open(get_file_prefix() + i, "w") as f:
                with open("default" + i, "r") as fo:
                    f.write(fo.read())
                print("create " + get_file_prefix() + i)


def get_valid_id():
    fname = get_file_prefix() + "_enfuzzy.csv"
    lid = 0
    with open(fname, "r") as f:
        for line in f:
            lid = line.split(",")[0]
    return int(lid) + 1


def record_enfuzzy(var, val, concept):
    """记录模糊化过程"""
    fname = get_file_prefix() + "_enfuzzy.csv"
    get_id = get_valid_id()
    with open(fname, "a") as f:
        # ~ print("模糊化:::{},{},{},{},{}".format(get_id, var, val, concept, time.mktime(datetime.datetime.now().timetuple())))
        f.write("{},{},{},{},{}\n".format(get_id, var, val, concept, time.mktime(datetime.datetime.now().timetuple())))
    return get_id


def record_inference(kid, cond, res):
    """记录推理过程"""
    fname = get_file_prefix() + "_record.csv"
    with open(fname, "a") as f:
        # ~ print("推理:::{},{},{},{}".format(kid, cond, res, time.mktime(datetime.datetime.now().timetuple())))
        f.write("{},{},{},{}\n".format(kid, cond, res, time.mktime(datetime.datetime.now().timetuple())))


def record_defuzzy(var, concept, val):
    """记录去模糊化过程"""
    fname = get_file_prefix() + "_defuzzy.csv"
    with open(fname, "a") as f:
        # ~ print("去模糊化:::{},{},{},{}".format(var, concept, val, time.mktime(datetime.datetime.now().timetuple())))
        f.write("{},{},{},{}\n".format(var, concept, val, time.mktime(datetime.datetime.now().timetuple())))


def search_defuzzy(result):
    if result.count("=") != 1:
        return 0

    var, val = result.split("=")
    fname = get_file_prefix() + "_defuzzy.csv"
    data = 0
    maxTime = 0

    with open(fname, "r") as f:
        for line in f:
            d = line.rstrip("\n").split(",")
            if d[0] == var and d[2] == val:
                if eval(d[-1]) > maxTime:
                    maxTime = eval(d[-1])
                    data = d
    return data


def get_explanation(result):
    ans = search_defuzzy(result)
    if ans:
        return fuzzy_explain(ans)
    else:
        return "CAN NOT EXPLAIN"


def search_record(concept):
    fname = get_file_prefix() + "_record.csv"
    cond = 0
    maxTime = 0
    with open(fname, "r") as f:
        for line in f:
            d = line.rstrip("\n").split(",")
            if d[2] == concept:
                if maxTime < eval(d[-1]):
                    maxTime = eval(d[-1])
                    cond = d
    return cond


def get_enfuzzy(enid):
    fname = get_file_prefix() + "_enfuzzy.csv"
    with open(fname, "r") as f:
        for line in f:
            d = line.rstrip("\n").split(",")
            if d[0] == enid:
                return d
    return 0


def fuzzy_explain(ans):
    defuzzy = ans[1]
    inference_stack = [defuzzy]
    knowledge_stack = ["defuzzy_{}->{}".format(defuzzy, ans[2])]
    curr_concept = inference_stack[-1]
    data = ""
    while curr_concept != CONCEPT_START:
        # 推理过程
        data = search_record(curr_concept)
        curr_concept = data[1]
        inference_stack.append(curr_concept)
        knowledge_stack.append(data[0])
    else:
        # 模糊化
        enfuzzy_id = data[0]
        enfuzzy_data = get_enfuzzy(enfuzzy_id)
        inference_stack.pop(-1)
        knowledge_stack.pop(-1)
        inference_stack.append(curr_concept)
        knowledge_stack.append("enfuzzy_{}:{}->{}".format(enfuzzy_data[1], enfuzzy_data[2], enfuzzy_data[3]))

    infer_chain = ""
    know_chain = ""
    while len(inference_stack) > 0:
        infer_chain = infer_chain + inference_stack.pop(-1) + "->"
        know = knowledge_stack.pop(-1)
        try:
            x = eval(know)
            if type(x) == int:
                # 是一条知识的id
                know_chain += "knowledge({})".format(x) + "   "
        except:
            know_chain += know + "   "
    infer_chain += "END"
    know_chain += "END"
    return "\n".join([infer_chain, know_chain])


def initialize(csr, dbname, user):
    csr.execute("USE " + dbname)
    csr.execute("DROP table if EXISTS fdb")
    csr.execute("DROP table if EXISTS fdb_traffic")
    csr.execute("DROP table if EXISTS fdb_light_time")
    csr.execute("DROP table if EXISTS ks")
    ctine = "CREATE TABLE IF NOT EXISTS "
    csr.execute(ctine + "FDB"
                        "(ID int NOT NULL AUTO_INCREMENT primary key,"
                        "linguistic_variable varchar(32) NOT NULL,"
                        "fuzzy_set int NOT NULL,"
                        "used int NOT NULL default 0,"
                        "updtime datetime,"
                        "administrator varchar(32) default \"%s\")" % user)
    csr.execute(ctine + "KS"
                        "(ID int NOT NULL primary key,"
                        "concv varchar(32) not null,"
                        "closeness float(3,2) not null,"
                        "updtime datetime,"
                        "administrator varchar(32) default \"{}\")".format(user))


def getDomin(csr, ling_var):
    """
    获取语言变量的域
    :param csr:cursor
    :param ling_var:语言变量 str
    :return: 语言变量的域(numpy数组)
    """
    csr.execute("SELECT VALUE from fuzzy_concept_" + ling_var)
    return np.array(csr.fetchall()).reshape(1, -1)[0]


def fuzzing(csr, ling_var, val, sigma):
    """
    三角法模糊化
    :param conn: 数据库连接
    :param dbname: 数据库名
    :param ling_var: 语言变量的名字
    :param val: 实际测量的精确值
    :param sigma: 三角法参数
    :param lb: lower bound
    :param ub: upper bound
    :return: 模糊集
    """
    cnt = csr.execute("SELECT LingV FROM sum_lingv WHERE Lingv = '%s'" % ling_var)
    if not cnt:
        raise Exception("There is no such linguistic variable {} in the knowledge database as given!".format(ling_var))
    domin = getDomin(csr, ling_var)
    fuzzy_set = 1 - abs(domin - val) / sigma
    fuzzy_set[fuzzy_set < 0] = 0
    return fuzzy_set


def insert_into_FDB(dbname, csr, ling_var, fuzzy_set, c_stack):
    """
    将新事实插入到FDB
    :param dbname:
    :param csr:
    :param ling_var: (语言变量名，类型) (str,str)
    :param fuzzy_set: 模糊集(数组)
    :return:
    """
    #  如果语言变量第一次出现，为其创建一张表
    ctine = "CREATE TABLE IF NOT EXISTS "
    csr.execute(ctine + "FDB_" + ling_var[0] + "("
                                               "value " + ling_var[1] + " NOT NULL,primary key(value))")
    csr.execute(
        "select count(COLUMN_NAME) from information_schema.COLUMNS where table_schema = '{}' and table_name = 'fdb_{}';".format(
            dbname, ling_var[0]))
    num = csr.fetchone()[0]
    domin = getDomin(csr, ling_var[0])
    if num == 1:
        for val in domin:
            csr.execute("INSERT INTO fdb_" + ling_var[0] + " VALUES({})".format(val))

    c_stack.append("{}set{}".format(ling_var[0],num))
    # 插入事实到FDB
    suc = csr.execute(
        "INSERT INTO fdb(linguistic_variable, fuzzy_set, updtime) values(\"{}\",{},now())".format(ling_var[0], num))
    # 插入模糊集到对应语言变量表
    try:
        csr.execute("ALTER TABLE fdb_{}".format(ling_var[0]) + " ADD set" + str(num) + " float(3,2) not null")
        for ind in range(len(fuzzy_set)):
            csr.execute("UPDATE fdb_{}".format(ling_var[0]) + " SET set" + str(num)
                        + "={}".format(fuzzy_set[ind]) + "where value={}".format(domin[ind]))
    except:
        pass
    return suc


def getSolution(csr, dbname, solution):
    """
    尝试从事实库fdb中获取问题的解
    :param conn:
    :param dbname:
    :param solution: 为问题的解指定的语言变量 str
    :return: 问题的解的事实id
    """
    csr.execute("select id from fdb where linguistic_variable = '" + solution + "'")
    return csr.fetchall()


def defuzzing(csr, ling_var, fuzzy_set):
    """
    去模糊化
    :param ling_var: 语言变量 str
    :param fuzzy_set: 模糊集(numpy数组)
    :return: 去模糊化后的精确值
    """
    fuzzy_set = np.array(fuzzy_set)
    domin = getDomin(csr, ling_var)
    return domin[(fuzzy_set == fuzzy_set.max())[0]].mean()


def getfdb_ling_var(csr, id):
    """
    根据事实id获取事实对应的语言变量
    :param csr:
    :param id: fact id
    :return: 事实对应的语言变量 str
    """
    csr.execute("select linguistic_variable from fdb where id = {}".format(id))
    return csr.fetchone()[0]


def getfdbFuzzyset(csr, id):
    """
    根据事实id获取事实对应的模糊集
    :param csr:
    :param id:事实id
    :return:事实对应的模糊集，行向量
    """
    csr.execute("select linguistic_variable,fuzzy_set from fdb where id = {}".format(id))
    ling_var, setid = csr.fetchone()
    csr.execute("select set{} from fdb_{}".format(setid, ling_var))
    return np.array(csr.fetchall()).reshape([1, -1])


def getUnusedFact(csr):
    """
    从fdb中获取一条未使用过的事实
    :param csr:
    :return: 事实id
    """
    fact = csr.execute("select id from fdb where used=0")
    if fact > 0:
        fact = csr.fetchone()[0]
        csr.execute("update fdb set used=1 where id = {}".format(fact))
    return fact


def calCloseness(csr, ling_var, fid, kid):
    """
    calculate closeness 计算贴近度
    :param csr:
    :param fling_var: linguistic variable
    :param fid: fact id
    :param kid: knowledge id
    :return: closeness
    """
    csr.execute("select set{} from fdb_{}".format(fid, ling_var))
    fset = np.array(csr.fetchall()).reshape([1, -1])
    csr.execute("select FuzCptA from fuzzy_knowledge where id = {}".format(kid))
    kconcpt = csr.fetchone()[0]
    csr.execute("select {} from fuzzy_concept_{}".format(kconcpt, ling_var))
    kset = np.array(csr.fetchall()).reshape([1, -1])
    return 1 - np.linalg.norm(fset - kset) / np.sqrt(fset.size)
    # return (np.minimum(fset, kset).max() + 1 - np.maximum(fset, kset).min()) / 2


def calCloseness1(fset, kset):
    """
    calculate closeness 计算给定模糊集的贴近度
    :param fset: fact set
    :param kset: knowledge set
    :return: closeness
    """
    fset = np.array(fset)
    kset = np.array(kset)
    return (np.minimum(fset, kset).max() + 1 - np.maximum(fset, kset).min()) / 2


def fillKS(csr, fid):
    """
    将与事实匹配的贴近度最大的同类知识填入到ks中
    :param csr:
    :param fid: fact id
    :return:
    """
    csr.execute("select linguistic_variable from fdb where id={}".format(fid))
    fact_ling_var = csr.fetchone()[0]
    csr.execute("select id,concv,lambda from fuzzy_knowledge where condv=\"{}\"".format(fact_ling_var))
    kidlms = np.array(csr.fetchall())
    for kidlm in kidlms:
        closeness = calCloseness(csr, fact_ling_var, fid, kidlm[0])
        if closeness >= kidlm[2]:
            # print("insert into KS values({},\"{}\",{},now())".format(kidlm[0], kidlm[1], closeness))
            csr.execute(
                "insert into KS(id,concv,closeness,updtime) values({},\"{}\",{},now())".format(kidlm[0], kidlm[1],
                                                                                               closeness))
    csr.execute("select * from ks")
    csr.execute(
        "select KS.id,KS.concv,KS.closeness from KS join (select concv,max(closeness) as mc from KS group by concv) b on "
        "KS.concv=b.concv and KS.closeness=b.mc")
    kidvs = csr.fetchall()
    csr.execute("delete from ks")
    concv_set = set()
    for kidv in kidvs:
        if kidv[1] not in concv_set:
            concv_set.add(kidv[1])
            csr.execute("insert into ks(ID,concv,closeness,updtime) values({},\"{}\",{},now())".format(*kidv))


def getMat(csr, kid):
    """
    获取给定知识的模糊矩阵
    :param csr:
    :param kid: knowledge id
    :return: 模糊矩阵
    """
    csr.execute("select condv,fuzcptA,concv,fuzcptB from fuzzy_knowledge where id ={}".format(kid))
    condv, fuzcptA, concv, fuzcptB = csr.fetchone()
    cond_domin = getDomin(csr, condv)
    conc_domin = getDomin(csr, concv)
    mat = np.zeros([len(cond_domin), len(conc_domin)])
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            csr.execute("select R from matrix_{}_{} where val1={} and val2={}".format(fuzcptA, fuzcptB, cond_domin[i],
                                                                                      conc_domin[j]))
            mat[i, j] = csr.fetchone()[0]
    return mat


def hypomul(fset, fuz_mat):
    """
    hypothesis multiple 计算假言推理矩阵乘积
    :param fset: fact fuzzy set 行向量
    :param fuz_mat: fuzzy matrix
    :return:
    """
    res = np.zeros(fuz_mat.shape[1])
    for i in range(res.size):
        res[i] = np.minimum(fset, fuz_mat.T[i]).max()
    return res


def infer_by_knowledge(dbname, csr, k, fid, c_stack):
    """
    在当前事实下，根据给定的知识进行推理
    :param csr:
    :param k: 给定的ks中的知识，行向量
    :param fid: fact id
    :return:
    """
    # ling_var = getfdb_ling_var(csr,fid)
    fset = getfdbFuzzyset(csr, fid)
    fuz_mat = getMat(csr, k[0])
    # print(k)
    # print("mut")
    # print(fset)
    # print(fuz_mat)
    res_set = hypomul(fset, fuz_mat)
    csr.execute("select type from sum_lingv where lingv=\"{}\"".format(k[1]))
    lingtype = csr.fetchone()[0]
    insert_into_FDB(dbname, csr, (k[1], lingtype), res_set, c_stack)
    # print("res", res_set)


def infer_by_ks(dbname, csr, fid, c_stack, k_stack):
    """
    根据ks中的知识推理
    :param csr:
    :param fid: fact id
    :return:
    """
    csr.execute("select * from ks")
    ksk = csr.fetchall()
    for k in ksk:
        infer_by_knowledge(dbname, csr, k, fid, c_stack)
        k_stack.append(k[0])
        csr.execute("delete from ks where id = {}".format(k[0]))


def infer_by_number_table(conn, dbname, user):
    """
    读取number表，根据从number表中读出的车流量进行推理。number表存放从下位机传来的检测到的车流量大小。
    :param conn:
    :param dbname:
    :param user:
    :return:
    """
    # initialize(conn, dbname, user)
    # print("Succeeded initializing inference engine!")
    csr = conn.cursor()
    csr.execute("USE " + dbname)
    ling_var = ("traffic", "int")
    solution = "light_time"
    if csr.execute("select number from number where used = 0 and direction = 'NS'"):
        val = csr.fetchone()[0]
        csr.execute("update number set used = 1 where number = {} and direction = 'NS'".format(val))  #
        lt = infer(dbname, user, csr, ling_var, val, solution)
        # try:
        csr.execute(
            "insert into seconds(direction,number,seconds, updtime) values('{}',{},{},now())".format('NS', val, lt))
        csr.execute("commit")
        # print("insert into seconds(number,seconds, updtime) values({},{},now())".format(val, lt))
        # except:
        #     print("Error in infer_by_number_table!")
        #     csr.execute("rollback")

def infer(dbname, user, csr, ling_var, val, solution):
    """
    推理机过程实现
    :param conn:
    :param dbname:
    :param user:
    :param ling_var: (语言变量名,类型) (str,str)
    :param val: 接收到传感器传来的值
    :param solution: 问题的解 是个语言变量
    :return: 推理结果
    """
    stack_1 = ["START"]
    stack_2 = []

    initialize(csr, dbname, user)
    fuzzy_set = fuzzing(csr, ling_var[0], val, 5)
    insert_into_FDB(dbname, csr, ling_var, fuzzy_set, stack_1)

    # insert_into_FDB(conn, dbname, ling_var, fuzzing(conn, dbname, ling_var[0], 6, 2))
    solutions = getSolution(csr, dbname, solution)
    while len(solutions) == 0:
        fid = getUnusedFact(csr)
        if fid > 0:
            fillKS(csr, fid)
            infer_by_ks(dbname, csr, fid, stack_1, stack_2)
        else:
            return -1
        solutions = getSolution(csr, dbname, solution)
    result_fuzzy_set = getfdbFuzzyset(csr, solutions[0][0])
    defuzzy_data = round(defuzzing(csr, solution, result_fuzzy_set) / 3, 2)

    # TODO 解释器
    # print(stack_1)
    # print(stack_2)
    # assert len(stack_1)-2 == len(stack_2)
    enfuzzy_id = record_enfuzzy(ling_var[0], val, stack_1[1])
    stack_2.insert(0, enfuzzy_id)
    for i in range(len(stack_1)-1):
        record_inference(stack_2[i],stack_1[i],stack_1[i+1])
    record_defuzzy("light_time", stack_1[-1], defuzzy_data)
    return defuzzy_data


def explain(light_val):
    return get_explanation("light_time={}".format(light_val))


if __name__ == "__main__":
    init_file()
    host = constants.HOST
    user = constants.USER
    dbname = constants.DB
    conn = MySQLdb.connect(host, user, constants.PWD)
    solution = "light_time"
    ling_var = ("traffic", "int")
    csr = conn.cursor()
    csr.execute("use " + dbname)

    val = 5
    d = infer(dbname, user, csr, ling_var, val, solution)
    print(val, d)
    print(get_explanation("light_time={}".format(d)))    # 调用赋值型的解释器
    print(explain(d))                                    # 直接调用数字解释器 二者完全等价

    print(explain(15))
    print(explain(25))
    # val = np.arange(21)
    # data = []
    # for v in val:
    #     initialize(csr, dbname, user)
    #     d = infer(dbname, user, csr, ling_var, v, solution)
    #     print(v, solution, "=", d)
    #     data.append(d)
    #
    # print(get_explanation("light_time={}".format(data[3])))
