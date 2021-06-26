from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from pyqtgraph.graphicsItems.ROI import CircleROI
import Inference_engine
import credibility
import constants
import MySQLdb
class Explain:
    def __init__(self):
        self.ui = uic.loadUi("./ui/explain.ui")
        ico_path = './image/light.ico'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(ico_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.setWindowIcon(icon)
        self.ui.setWindowTitle('解释器')
        self.ui.resize(500,400)
        self.ui.confirm.clicked.connect(self.explain)
    def explain(self):
        car_num = int(self.ui.cars.text())
        host = constants.HOST
        user = constants.USER
        dbname = constants.DB
        conn = MySQLdb.connect(host, user, constants.PWD)
        csr = conn.cursor()
        ling_var = ("traffic", "int")
        solution = "light_time"
        credibility_time = credibility.rel_infer(car_num)
        fuzzy_time = Inference_engine.infer(dbname, user, csr, ling_var, car_num, solution)
        credibility_explain  = '绿灯时间为'+str(credibility_time)+'s\n' + credibility.explain(credibility_time)
        fuzzy_explain  = '绿灯时间为' + str(fuzzy_time) + 's\n' + Inference_engine.explain(fuzzy_time)
        self.ui.credibility_explain.setText(credibility_explain)
        self.ui.fuzzy_explain.setText(fuzzy_explain)
