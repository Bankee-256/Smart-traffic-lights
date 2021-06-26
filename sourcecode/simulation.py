'''the UI of simulation'''

from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from pyqtgraph import *
from PyQt5.QtGui import QPixmap
import credibility
import Inference_engine
import sv2db
import lower_computer
import multiprocessing
from PyQt5.QtCore import QThread
import time
direction = 1 #1表示南北，0表示东西
def changeDirection(direction1,pic):
        global direction
        if direction1 ==0:
            pm = QPixmap("./image/2.png")
            pic.setPixmap(pm)
            direction = 1
        else:
            pm = QPixmap("./image/1.png")
            pic.setPixmap(pm)
            direction =0

class Thread(QThread):
    def __init__(self):
        super(Thread, self).__init__()
        self.working = True

    def run(self):
        lower_computer.communicate_with_lower_computer()
    def __del__(self):
        # 线程状态改变与线程终止
        self.working = False
        self.wait()

class Thread1(QThread):
    def __init__(self,light_time ,pic,direction):
        super(Thread1, self).__init__()
        self.working = True
        self.light_time = light_time
        self.pic = pic
        self.direction = direction
    def run(self):
        if self.light_time == 0 or self.light_time == None :
            pass
        else:
            time.sleep(self.light_time)
            changeDirection(self.direction,self.pic)
    def __del__(self):
        # 线程状态改变与线程终止
        self.working = False
        self.wait()



class Simulation:
    def __init__(self):
        self.ui = uic.loadUi("./ui/simulation.ui")
        self.round = [0]
        self.green_time_sn = [0]
        self.cars_sn = [0]
        self.green_time_ew = [0]
        self.cars_ew = [0]
        self.setUI()
        self.timer = QtCore.QTimer()
        self.ui.start.clicked.connect(self.startSimulation)
        self.ui.stop.clicked.connect(self.stopSimulation)
        


    def setUI(self):
        ico_path = './image/light.ico'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(ico_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.setWindowIcon(icon)
        self.ui.setWindowTitle('仿真')
        self.ui.setStyleSheet("background-color:#DCDCDC;")
        self.ui.resize(1200, 900)
        self.ui.start.setStyleSheet("background-color:#FFFFFF;")
        self.ui.stop.setStyleSheet("background-color:#FFFFFF;")
        self.ui.east_west.setBackground('w')
        self.ui.east_west.setYRange(min=1, max=20)
        self.ui.east_west.setXRange(min=1, max=10)
        self.ui.east_west.addLegend()
        self.ui.east_west.setMouseEnabled(x=False, y=False)
        self.ui.south_north.setBackground('w')
        self.ui.south_north.setXRange(min=1, max=10)
        self.ui.south_north.setYRange(min=1, max=20)
        self.ui.south_north.addLegend()
        self.ui.south_north.setMouseEnabled(x=False, y=False)

        self.ui.south_north.plot(self.round,
                                 self.cars_sn,
                                 pen=pg.mkPen(color=(0, 128, 0), width=3),
                                 name='cars'
                                 )
        self.ui.south_north.plot(self.round,
                                 self.green_time_sn,
                                 pen=pg.mkPen(color=(255, 215, 0), width=3),
                                 name='green_time')
        self.ui.east_west.plot(self.round,
                               self.cars_ew,
                               pen=pg.mkPen(color=(0, 128, 0), width=3),
                               name='cars'
                               )
        self.ui.east_west.plot(self.round,
                               self.green_time_ew,
                               pen=pg.mkPen(color=(255, 215, 0), width=3),
                               name='green_time')
        self.setPicture()


    def setPicture(self):
        pm = QPixmap("./image/1.png")
        self.ui.traffic.setPixmap(pm)
        # self.ui.traffic.resize(300,200)
        # self.ui.traffic.setScaledContents(True)

    def startSimulation(self):
        self.timer.timeout.connect(self.updateData)
        self.timer.start(32500)
        lower_computer.enable()
        self.thread = Thread()
        self.thread.start()

    def stopSimulation(self):
        lower_computer.unable()
        self.timer.stop()

    def updateData(self):
        global direction
        changeDirection(direction,self.ui.traffic)
        carns = sv2db.get_ns_carnum()
        carwe = sv2db.get_we_carnum()
        timens = sv2db.get_ns_time()
        timewe = sv2db.get_we_time()
        self.t = Thread1(lower_computer.lightwe,self.ui.traffic,direction)
        self.t.start()
        self.ui.show_car_ew.setText("车流量："+str(carwe))
        self.ui.show_time_ew.setText("绿灯时间："+str(lower_computer.lightwe))
        self.ui.show_car_sn.setText("车流量："+str(carns))
        self.ui.show_time_sn.setText("绿灯时间："+str(lower_computer.lightns))
        self.round.append(self.round[-1] + 1)
        self.cars_sn.append(carns)
        self.green_time_sn.append(lower_computer.lightns)
        self.ui.south_north.plot().setData(self.round, self.cars_sn, pen=pg.mkPen(color=(0, 128, 0), width=3))
        self.ui.south_north.plot().setData(self.round, self.green_time_sn, pen=pg.mkPen(color=(255, 215, 0), width=3))
        self.cars_ew.append(carwe)
        self.green_time_ew.append(lower_computer.lightwe)
        self.ui.east_west.plot().setData(self.round, self.cars_ew, pen=pg.mkPen(color=(0, 128, 0), width=3),name = 'cars')
        self.ui.east_west.plot().setData(self.round, self.green_time_ew, pen=pg.mkPen(color=(255, 215, 0), width=3),name = 'green_time')
        #QMessageBox.information(self.ui, '解释器', credibility.explain(timewe) + '\n可信度解释器结果', QMessageBox.Ok,
         #                       QMessageBox.Ok)
        #QMessageBox.information(self.ui, '解释器', Inference_engine.explain(timens) + '\n模糊解释器结果', QMessageBox.Ok,
           #                     QMessageBox.Ok)

    def closeEvent(self, event):
        self.timer.stop()


if __name__ == "__main__":
    app = QApplication([])
    sim = Simulation()
    sim.ui.show()
    app.exec()
