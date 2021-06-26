import datetime
import MySQLdb
import numpy as np
import sys
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import *
from statistics import Statistics
from stats import Stats
from simulation import Simulation
from credibilityKnowledge import CredibilityKnowledge
from simulation_real_time import SimulationRealTime
import build_db
import constants
import explain

class Mainwindow:
    def __init__(self):
        self.ui = uic.loadUi("./ui/mainwindow.ui")
        ico_path = './image/light.ico'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(ico_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.setWindowIcon(icon)
        self.ui.CredibilityButton.clicked.connect(self.credibilityKnowledge)
        self.ui.FuzzyButton.clicked.connect(self.fuzzyKnowledge)
        self.ui.AnalysisButton.clicked.connect(self.analysis)
        self.ui.SimulationButton.clicked.connect(self.simulation)
        self.ui.SettingsButton.clicked.connect(self.simulation_real_time)
        self.ui.OutofButton.clicked.connect(self.exitsystem)

    def credibilityKnowledge(self):
        credibility_knowledge.ui.show()

    def fuzzyKnowledge(self):
        stats.ui.show()

    def analysis(self):
        statistics.ui.show()
        statistics.show_all()

    def simulation(self):
        sim.ui.south_north.clear()
        sim.ui.east_west.clear()
        sim.round.clear()
        sim.round.append(0)
        sim.green_time_sn.clear()
        sim.green_time_sn.append(0)
        sim.cars_sn.clear()
        sim.cars_sn.append(0)
        sim.green_time_ew.clear()
        sim.green_time_ew.append(0)
        sim.cars_ew.clear()
        sim.cars_ew.append(0)
        sim.ui.show()

    def systemSetting(self):
        pass

    def exitsystem(self):
        ex.ui.show()
        ex.ui.resize(500,400)
        

    def simulation_real_time(self):
        sim_real_time.ui.south_north.clear()
        sim_real_time.ui.east_west.clear()
        sim_real_time.round.clear()
        sim_real_time.round.append(0)
        sim_real_time.green_time_sn.clear()
        sim_real_time.green_time_sn.append(0)
        sim_real_time.cars_sn.clear()
        sim_real_time.cars_sn.append(0)
        sim_real_time.green_time_ew.clear()
        sim_real_time.green_time_ew.append(0)
        sim_real_time.cars_ew.clear()
        sim_real_time.cars_ew.append(0)
        sim_real_time.ui.show()

if __name__ == "__main__":
    host = constants.HOST
    user = constants.USER
    password = constants.PWD
    dbname = constants.DB
    conn = MySQLdb.connect(host, user, password)
    build_db.init(host, user, password, dbname)
    build_db.init_credibility()

    app = QApplication([])
    mainw = Mainwindow()
    statistics = Statistics()
    stats = Stats()
    sim = Simulation()
    ex = explain.Explain()
    sim_real_time = SimulationRealTime()
    credibility_knowledge = CredibilityKnowledge()
    
    mainw.ui.show()
    app.exec()
