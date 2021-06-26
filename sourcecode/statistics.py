''' the UI of statistics information'''

from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import *
import statistic_table


class Statistics:
    def __init__(self):
        self.ui = uic.loadUi("./ui/statistics_analysis.ui")
        self.set_ui()
        self.show_all()
        self.ui.StatisticsButton.clicked.connect(self.analyze)

    def set_ui(self):
        ico_path = './image/light.ico'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(ico_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.setWindowIcon(icon)
        self.ui.setWindowTitle('统计分析')
        self.ui.resize(950, 600)
        self.ui.setFixedSize(self.ui.width(), self.ui.height());

    def show_all(self):
        # statistic_table.add_statistic(10, 10, 0, 10)
        # statistic_table.add_statistic(10, 10, 10, 0)
        sta = statistic_table.search_statistic("", "", "")
        for row in range(len(sta)):
            for i in range(7):
                if i == 0:  # 统计时间
                    item1 = QTableWidgetItem(str(sta[row][i + 5]))
                    item1.setFlags(QtCore.Qt.ItemIsEditable)
                    self.ui.StatisticsTable.setItem(row, i, item1)
                elif 1 <= i <= 2:
                    item1 = QTableWidgetItem(str(sta[row][i]))
                    item1.setFlags(QtCore.Qt.ItemIsEditable)
                    self.ui.StatisticsTable.setItem(row, i, item1)
                elif i == 3:
                    item1 = QTableWidgetItem(str(sta[row][i + 1]))
                    item1.setFlags(QtCore.Qt.ItemIsEditable)
                    self.ui.StatisticsTable.setItem(row, i, item1)
                elif i == 4:
                    item1 = QTableWidgetItem(str(sta[row][i - 1]))
                    item1.setFlags(QtCore.Qt.ItemIsEditable)
                    self.ui.StatisticsTable.setItem(row, i, item1)
                elif i == 5:
                    if str(sta[row][i - 1]) != "0":
                        item1 = QTableWidgetItem("允许通行")
                        item1.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.StatisticsTable.setItem(row, i, item1)
                    else:
                        item1 = QTableWidgetItem("禁止通行")
                        item1.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.StatisticsTable.setItem(row, i, item1)
                elif i == 6:
                    if str(sta[row][i - 3]) != "0":
                        item1 = QTableWidgetItem("允许通行")
                        item1.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.StatisticsTable.setItem(row, i, item1)
                    else:
                        item1 = QTableWidgetItem("禁止通行")
                        item1.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.StatisticsTable.setItem(row, i, item1)

    def analyze(self):
        start = self.ui.StartTime.text().strip()  # 获取文本框内的开始时间
        finish = self.ui.FinishTime.text().strip()  # 获取文本框内的结束时间
        msg = ""
        if start == "":
            msg += "起始时间为空！\n"
        if finish == "":
            msg += "结束时间为空！\n"
        if msg != "":
            QMessageBox.about(self.ui, '错误信息', msg)
            return
        else:
            # statistic_table.add_statistic(10, 10, 0, 10)
            # statistic_table.add_statistic(10, 10, 10, 0)
            sta = statistic_table.search_statistic("UPDATE_TIME", start, finish)
            # [(1,'10','10','0','10','2021-06-25 20:27:38'),(2,'10','10','10','0','2021-06-25 20:27:38')]
            # statistic_table.search_statistic("", start, finish)
            self.ui.StatisticsTable.clearContents()
            for row in range(len(sta)):
                for i in range(7):
                    if i == 0:  # 统计时间
                        item1 = QTableWidgetItem(str(sta[row][i + 5]))
                        item1.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.StatisticsTable.setItem(row, i, item1)
                    elif 1 <= i <= 2:
                        item1 = QTableWidgetItem(str(sta[row][i]))
                        item1.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.StatisticsTable.setItem(row, i, item1)
                    elif i == 3:
                        item1 = QTableWidgetItem(str(sta[row][i + 1]))
                        item1.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.StatisticsTable.setItem(row, i, item1)
                    elif i == 4:
                        item1 = QTableWidgetItem(str(sta[row][i - 1]))
                        item1.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.StatisticsTable.setItem(row, i, item1)
                    elif i == 5:
                        if str(sta[row][i - 1]) != "0":
                            item1 = QTableWidgetItem("允许通行")
                            item1.setFlags(QtCore.Qt.ItemIsEditable)
                            self.ui.StatisticsTable.setItem(row, i, item1)
                        else:
                            item1 = QTableWidgetItem("禁止通行")
                            item1.setFlags(QtCore.Qt.ItemIsEditable)
                            self.ui.StatisticsTable.setItem(row, i, item1)
                    elif i == 6:
                        if str(sta[row][i - 3]) != "0":
                            item1 = QTableWidgetItem("允许通行")
                            item1.setFlags(QtCore.Qt.ItemIsEditable)
                            self.ui.StatisticsTable.setItem(row, i, item1)
                        else:
                            item1 = QTableWidgetItem("禁止通行")
                            item1.setFlags(QtCore.Qt.ItemIsEditable)
                            self.ui.StatisticsTable.setItem(row, i, item1)
