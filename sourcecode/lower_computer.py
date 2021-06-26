"""
@name: lab1.py
@Describe: 通过python的串口库与下位机单片机通信
"""

import serial

import constants
from sv2db import *
import statistic_table

lightwe = 0
lightns = 0
# import build_db
en = 0


def communicate_with_lower_computer():
    global en  # 使能
    serialPort = constants.SERIALPORT  # 串口
    baudRate = 9600  # 波特率
    ser = serial.Serial(serialPort, baudRate, timeout=0.5)  # 连接串口
    print("参数设置：串口=%s ，波特率=%d" % (serialPort, baudRate))

    def func(x):
        return x % 30

    light_time = 10
    light_time1 = 10
    while 1:
        if en == 0:
            break
        c = ser.readline()
        recv = bytes.decode(c)
        # print("recv:", recv, c)

        if recv != '' and recv[0] == 'f':  # 接收反馈
            print(f'下位机成功接收亮灯信号, 即将亮灯 {int(recv[2:])} 秒')
            # ~ fb2db(int(recv[2:]))  # 将接收的反馈中的数目写入数据库 表feedback中
            continue
        elif recv == '':  # 无任何情况
            continue
        elif recv[2:6] == 'ffff':  # 检测到工作标志
            if recv[0:2] == 'WE':
                # 将接收的方向和进度写入数据库 表progress_rate中
                # ~ pgr2db('WE', int(recv[8:10]) / 100)
                print(f'正在检测东西方向, 进度:{int(recv[8:10])}%')
            else:
                # 将接收的方向和进度写入数据库 表progress_rate中
                # ~ pgr2db('NS', int(recv[8:10]) / 100)
                print(f'正在检测南北方向, 进度:{int(recv[8:10])}%')
            continue
        else:  # 收到车流
            direction = recv[0] + recv[1]  # 接收下位机上传的方向
            print("recv traffic ", recv)
            print(recv[2:])
            car_num = int(recv[2:])  # 接收下位机上传的车辆数目
            # ~ n2db(direction, car_num)  # 将接收的方向和数目写入数据库 表number中

        # ~ sec2db(light_time)  # 将发送的亮灯时长写入数据库 表seconds中

        if direction == "WE":
            light_time = decision(direction, car_num)  ### 通过知识库, 决定应该亮灯的时间
            print(f"东西方向车辆: {car_num}")

            # 添加statistic数据
            statistic_table.add_statistic(car_num, 0, light_time, 0)
        elif direction == "NS":
            print(f"南北方向车辆: {car_num}")
            light_time1 = decision(direction, car_num)  ### 通过知识库, 决定应该亮灯的时间

            light_time = int(30 * (light_time + 1) / (light_time1 + light_time + 1))
            light_time1 = int(30 - light_time)
            print(f"一次检测完成, 亮绿灯:{light_time} 亮黄灯:{light_time1}")
            global lightwe, lightns
            lightns = light_time1
            lightwe = light_time

            # int --> byte, 方便向下位机传输
            # int(参数)：参数代表要被转换的数字 ; length=2：代表要转换成几个字节  ; byteorder='big'代表高位在前，相反little
            data_byte = int(light_time).to_bytes(length=1, byteorder='big', signed=False)
            ser.write(data_byte)  # 向下位机发送亮灯时长
            # ~ sec2db(light_time)  # 将发送的亮灯时长写入数据库 表seconds中

            # 添加statistic数据
            statistic_table.add_statistic(0, car_num, 0, light_time)

    ser.close()


def unable():
    global en
    en = 0


def enable():
    global en
    en = 1
