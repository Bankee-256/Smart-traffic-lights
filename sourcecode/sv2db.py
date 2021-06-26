import MySQLdb
import Inference_engine
import constants
import credibility
import baidumap
import time
import statistic_table

"""提供将上、下位机数据存入数据库的接口"""

car_num_ns = 0
car_num_we = 0
time_ns = 0
time_we = 8
time_n = 0
time_w = 0
en = 1

def pgr2db(dir, rate):
    """
    向progress_rate表中插入记录
    :param dir: direction 方向 'WE' or 'NS'
    :param rate: 保留两位小数的浮点数
    """
    if dir not in ['WE', 'NS']:
        raise ValueError("dir must be 'WE' or 'NS'!")
    if not isinstance(rate, float):
        raise ValueError("progress rate must be float!")

    db = MySQLdb.connect(constants.HOST, constants.USER, constants.PWD, constants.DB)
    cursor = db.cursor()

    ins2pgr = "INSERT INTO PROGRESS_RATE(DIRECTION,PROGRESS_RATE,UPDTIME) VALUES (%s,%.2f,now())" \
              % ('"' + dir + '"', rate)
    try:
        cursor.execute(ins2pgr)
        db.commit()
    except:
        print("PGR ERR")
        db.rollback()
    db.close()


def n2db(dir, num):
    """
    向number表中插入记录
    :param dir: direction 方向 'WE' or 'NS'
    :param num: 车辆数目 自然数
    """
    if dir not in ['WE', 'NS']:
        raise ValueError("dir must be 'WE' or 'NS'!")
    if not isinstance(num, int):
        raise ValueError("number must be an integer!")
    if num < 0:
        raise ValueError("number must be non-negative!")
    db = MySQLdb.connect(constants.HOST, constants.USER, constants.PWD, constants.DB)
    cursor = db.cursor()
    ins2num = "INSERT INTO NUMBER(DIRECTION,NUMBER,UPDTIME) VALUES (%s,%d,now())" % ('"' + dir + '"',
                                                                                     num)
    try:
        cursor.execute(ins2num)
        # print(ins2num)
        db.commit()
    except:
        print("NUM ERR")
        db.rollback()

    db.close()


def fb2db(sec):
    """
    向feedback表中插入记录
    :param sec: 反馈的秒数，自然数
    """
    if not isinstance(sec, int):
        raise ValueError("second must be an integer!")
    if sec < 0:
        raise ValueError("second must be non-negative!")
    db = MySQLdb.connect(constants.HOST, constants.USER, constants.PWD, constants.DB)
    cursor = db.cursor()
    ins2sec = "INSERT INTO FEEDBACK(SECONDS,UPDTIME) VALUES (%d,now())" % sec
    try:
        cursor.execute(ins2sec)
        db.commit()
    except:
        print("FD ERR")
        db.rollback()
    db.close()


def sec2db(sec):
    """
    向seconds表中插入记录
    :param sec: 上位机指令中亮灯秒数，自然数
    """
    if not isinstance(sec, int):
        raise ValueError("second must be an integer!")
    if sec < 0:
        raise ValueError("second must be non-negative!")
    db = MySQLdb.connect(constants.HOST, constants.USER, constants.PWD, constants.DB)
    cursor = db.cursor()
    ins2sec = "INSERT INTO SECONDS(SECONDS,UPDTIME) VALUES (%d,now())" % sec
    try:
        cursor.execute(ins2sec)
        db.commit()
    except:
        print("SEC ERR")
        db.rollback()
    db.close()


def decision(direction, car_num):
    """
     获取推理结果
    :param direction: 方向 'NS' or 'WE'
    :param car_num: 车流量 int
    :return:
    """
    db = MySQLdb.connect(constants.HOST, constants.USER, constants.PWD, constants.DB)
    cursor = db.cursor()
    global car_num_ns, time_ns, car_num_we, time_we
    if direction == "NS":
        print("正在使用模糊推理机：")
        host = constants.HOST
        user = constants.USER
        dbname = constants.DB
        conn = MySQLdb.connect(host, user, constants.PWD)
        csr = conn.cursor()
        ling_var = ("traffic", "int")
        solution = "light_time"
        time = Inference_engine.infer(dbname, user, csr, ling_var, car_num, solution)
        print(f"模糊时间{time}s")
        car_num_ns = car_num
        time_ns = time
        return time
    elif direction == "WE":
        print("正在使用可信度推理机：")
        time = credibility.rel_infer(car_num)
        print(f"可信度时间{time}s")
        car_num_we = car_num
        time_we = time
        return time


def real_time():
    global time_ns, time_we, time_w, time_n
    i = 0
    while True:
        if en == 0:
            break
        direction = "NS"
        time_ns = decision_real_time(direction)
        if i == 0: time.sleep(15)
        else: time.sleep(29-time_w)
        tmp = time_w
        direction = "WE"
        time_we = decision_real_time(direction)
        time_w = int(30 * (time_we + 1) / (time_ns + time_we + 1))
        time_n = int(30 - time_w)
        statistic_table.add_statistic(car_num_we, 0, time_w, 0)
        if i==0: time.sleep(14)
        else: time.sleep(tmp)
        statistic_table.add_statistic(0, car_num_ns, 0, time_n)
        i+=1


def decision_real_time(direction):
    global car_num_ns, time_ns, car_num_we, time_we
    if direction == "NS":
        car_num = baidumap.get_NS_traffic()
        print("正在使用模糊推理机：")
        host = constants.HOST
        user = constants.USER
        dbname = constants.DB
        conn = MySQLdb.connect(host, user, constants.PWD)
        csr = conn.cursor()
        ling_var = ("traffic", "int")
        solution = "light_time"
        time = Inference_engine.infer(dbname, user, csr, ling_var, car_num, solution)
        print(f"模糊时间{time}s")
        car_num_ns = car_num
        time_ns = time
        return time
    else:
        print("正在使用可信度推理机：")
        car_num = baidumap.get_WE_traffic()
        time = credibility.rel_infer(car_num)
        print(f"可信度时间{time}s")
        car_num_we = car_num
        time_we = time
        return time


def get_ns_carnum():
    return car_num_ns


def get_we_carnum():
    return car_num_we


def get_ns_time():
    return time_ns


def get_we_time():
    return time_we


def enable():
    global en
    en = 1


def unable():
    global en
    en = 0

if __name__ == '__main__':
    pgr2db('NS', .5)
    n2db('WE', 1)
    fb2db(10)
    sec2db(20)
