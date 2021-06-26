'''the UI of fuzzy knowledge management'''
import constants
import utils
import datetime
import MySQLdb
import numpy as np
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import *


class Stats:

    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = uic.loadUi("./ui/fuzzytable.ui")
        self.conn = MySQLdb.connect(constants.HOST, constants.USER, constants.PWD)
        self.show_knowledge("", "")  # 显示所有知识
        self.ui.resize(1400, 700)
        ico_path = './image/light.ico'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(ico_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.setWindowIcon(icon)
        self.ui.setWindowIcon(icon)
        self.ui.InsertButton_3.clicked.connect(self.insert_knowledge)
        self.ui.DeleteButton_3.clicked.connect(self.delete_knowledge)
        self.ui.UpdateButton_3.clicked.connect(self.update_knowledge)
        self.ui.QueryButton_3.clicked.connect(self.query_knowledge)
        self.ui.ClearButton_3.clicked.connect(self.clear_all)
        # self.ui.button.clicked.connect(self.handleCalc)

    def insert_knowledge(self):
        msg = ''
        dbname = "traffic_light"
        # condition = "traffic"
        condition = str(self.ui.ConditionalVar_3.text().strip())

        # condvartype = "int"
        condvartype = str(self.ui.ConditionalVarType_3.text().strip())

        # FuzzyConA = "large_6"
        FuzzyConA = str(self.ui.FuzzyConA_3.text().strip())

        # FuzzyFuncA = "lambda inp: (1 - abs(inp - 15) / 5) if abs(inp - 15) < 5 else 0"
        FuzzyFuncA = str(self.ui.FuzzyFuncA_3.text().strip())

        # conclusion = "light_time"
        conclusion = str(self.ui.ConclusionVar_3.text().strip())

        # concvartype = "float"
        concvartype = str(self.ui.ConclusionVarType_3.text().strip())

        # FuzzyConB = "long_6"
        FuzzyConB = str(self.ui.FuzzyConB_3.text().strip())

        # FuzzyFuncB = "lambda inp: (100 - inp) / 20 if 100 > inp >= 80 else ((inp - 60) / 20 if 80 > inp >= 60 else 0)"
        FuzzyFuncB = str(self.ui.FuzzyFuncB_3.text().strip())

        # condition_credibility = "0.6"
        condition_credibility = str(self.ui.ConditionalCre_3.text().strip())

        # knowledge_credibility = "0.8"
        knowledge_credibility = str(self.ui.KnowledgeCre_3.text().strip())

        # update_person = "admin"
        update_person = str(self.ui.UpdatePeople_3.text().strip())

        # id = "6"
        id = str(self.ui.ID_3.text().strip())
        '''print(type(condition))
        print(condvartype)
        print(FuzzyConA)
        print(FuzzyFuncA)'''

        if id == "":
            id = None
            msg += "缺少ID！\n"
        if condition == "":
            msg += "缺少条件变量！\n"
        if condvartype == "":
            msg += "缺少条件变量类型！\n"
        if FuzzyConA == "":
            msg += "缺少模糊概念A！\n"
        if FuzzyFuncA == "":
            msg += "缺少隶属函数A！\n"
        if FuzzyFuncB == "":
            msg += "缺少隶属函数B！\n"
        if conclusion == "":
            msg += "缺少结论变量！\n"
        if concvartype == "":
            msg += "缺少结论变量类型！\n"
        if FuzzyConB == "":
            msg += "缺少模糊概念B！\n"
        if condition_credibility != '':
            if (self.IsFloat(condition_credibility)):
                condition_credibility = float(condition_credibility)
                if condition_credibility > 1 or condition_credibility < 0:
                    msg += '条件可信度不在0-1之间！\n'
            else:
                msg += '表示条件可信度的不是一个数！\n'
        else:
            msg += '缺少条件可信度！\n'
        if knowledge_credibility != '':
            if self.IsFloat(knowledge_credibility):
                knowledge_credibility = float(knowledge_credibility)
                if knowledge_credibility > 1 or knowledge_credibility < 0:
                    msg += '结论可信度不在0-1之间！\n'
            else:
                msg += '表示结论可信度的不是一个数！\n'
        else:
            msg += '缺少知识可信度！\n'
        if update_person == '':
            msg += '缺少更新人！\n'
        if msg != '':
            QMessageBox.about(self.ui, '错误信息', msg)
            return
        else:
            func = {}
            var1 = [condition, condvartype]
            var1_list = np.arange(21)
            try:
                exec("cpt1_func = " + FuzzyFuncA, func)
            except:
                QMessageBox.about(self.ui, "错误", "隶属函数不合规范")
                self.clear_all()
                return
            var2 = [conclusion, concvartype]
            try:
                exec("cpt2_func = " + FuzzyFuncB, func)
            except:
                QMessageBox.about(self.ui, "错误", "隶属函数不合规范")
                self.clear_all()
                return
            time_list = np.arange(5, 110, 2)
            cf = float(condition_credibility)
            l = float(knowledge_credibility)
            flag = utils.fuzzy_knowledge_insert(self.conn, dbname, var1, var1_list, FuzzyConA, func["cpt1_func"], var2,
                                                time_list, FuzzyConB, func["cpt2_func"], cf, l, id)
            self.show_knowledge("", "")
            self.clear_all()
            if flag != -1:
                QMessageBox.about(self.ui, "成功", "添加成功")
            else:
                QMessageBox.about(self.ui, "失败", "添加失败")

    def delete_knowledge(self):
        dbname = "traffic_light"
        id = self.ui.ID_3.text().strip()
        if id == "":
            QMessageBox.about(self.ui, "错误", "ID为空")
            return
        else:
            num = utils.fuzzy_knowledge_delete(self.conn, dbname, id)
            if num:
                self.show_knowledge("", "")
                self.clear_all()
                QMessageBox.about(self.ui, "成功", "删除成功")
            else:
                QMessageBox.about(self.ui, "错误", "ID不存在")

    def update_knowledge(self):
        msg = ''
        dbname = "traffic_light"
        # condition = "traffic1"
        condition = self.ui.ConditionalVar_3.text().strip()

        # condvartype = "int"
        condvartype = self.ui.ConditionalVarType_3.text().strip()

        # FuzzyConA = "large_4"
        FuzzyConA = self.ui.FuzzyConA_3.text().strip()

        # FuzzyFuncA = "lambda inp: (1 - abs(inp - 15) / 5) if abs(inp - 15) < 5 else 0"
        FuzzyFuncA = self.ui.FuzzyFuncA_3.text().strip()

        # conclusion = "light_time2"
        conclusion = self.ui.ConclusionVar_3.text().strip()

        # concvartype = "float"
        concvartype = self.ui.ConclusionVarType_3.text().strip()

        # FuzzyConB = "long_4"
        FuzzyConB = self.ui.FuzzyConB_3.text().strip()

        # FuzzyFuncB = "lambda inp: (100 - inp) / 20 if 100 > inp >= 80 else ((inp - 60) / 20 if 80 > inp >= 60 else 0)"
        FuzzyFuncB = self.ui.FuzzyFuncB_3.text().strip()

        # update_person = "admin"
        update_person = self.ui.UpdatePeople_3.text().strip()

        # id = "1"
        id = self.ui.ID_3.text().strip()
        # print("!!!!!")
        # print(FuzzyFuncA)

        if id == "":
            id = None
            msg += "缺少ID！\n"
        if condition == "":
            msg += "缺少条件变量！\n"
        if condvartype == "":
            msg += "缺少条件变量类型！\n"
        if FuzzyFuncA == "":
            msg += "缺少隶属函数A！\n"
        if FuzzyFuncB == "":
            msg += "缺少隶属函数B！\n"
        if conclusion == "":
            msg += "缺少结论变量！\n"
        if concvartype == "":
            msg += "缺少结论变量类型！\n"
        if update_person == '':
            msg += '缺少更新人！\n'
        if msg != '':
            QMessageBox.about(self.ui, '错误信息', msg)
            return
        else:
            func = {}
            var1 = [condition, condvartype]
            var1_list = np.arange(21)
            var2 = [conclusion, concvartype]
            time_list = np.arange(5, 110, 2)
            try:
                exec("cpt1_func = " + FuzzyFuncA, func)
            except:
                QMessageBox.about(self.ui, "错误", "隶属函数不合规范")
                self.clear_all()
                return
            var2 = [conclusion, concvartype]
            try:
                exec("cpt2_func = " + FuzzyFuncB, func)
            except:
                QMessageBox.about(self.ui, "错误", "隶属函数不合规范")
                self.clear_all()
                return
            flag = utils.fuzzy_knowledge_change(self.conn, dbname, id, var1_list, func["cpt1_func"], time_list,
                                                func["cpt2_func"], var1, var2)
            self.show_knowledge("", "")
            self.clear_all()
            # print(flag)
            if flag != -1:
                QMessageBox.about(self.ui, "成功", "更新成功")
            else:
                QMessageBox.about(self.ui, "失败", "更新失败")


    def query_knowledge(self):
        # 利用id查找模糊知识
        id = self.ui.ID_3.text().strip()
        cond_a = self.ui.ConditionalVar_3.text().strip()
        if id != "":
            self.show_knowledge(id, "")
        elif cond_a != "":
            self.show_knowledge("", cond_a)

    def clear_all(self):
        self.ui.ID_3.clear()
        self.ui.ConditionalVar_3.clear()
        self.ui.ConditionalVarType_3.clear()
        self.ui.FuzzyConA_3.clear()
        self.ui.FuzzyFuncA_3.clear()
        self.ui.ConclusionVar_3.clear()
        self.ui.ConclusionVarType_3.clear()
        self.ui.FuzzyConB_3.clear()
        self.ui.FuzzyFuncB_3.clear()
        self.ui.KnowledgeCre_3.clear()
        self.ui.ConditionalCre_3.clear()
        self.ui.UpdatePeople_3.clear()
        self.show_knowledge("", "")

    def show_knowledge(self, id, cond_a):
        self.ui.FuzzyKtable_3.clearContents()
        if id != "":
            data_list_id = utils.fuzzy_knowledge_show(self.conn, "traffic_light", id)
            if data_list_id == None:
                QMessageBox.about(self.ui, '错误', "ID不存在！")
            else:
                for i in range(8):
                    if i < 6:
                        item1 = QTableWidgetItem(str(data_list_id[i + 1]))
                        item1.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.FuzzyKtable_3.setItem(0, i, item1)
                    elif i == 6:
                        item2 = QTableWidgetItem(str(data_list_id[7]))
                        item2.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.FuzzyKtable_3.setItem(0, i, item2)
                    elif i == 7:
                        item3 = QTableWidgetItem(str(data_list_id[8]))
                        item3.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.FuzzyKtable_3.setItem(0, i, item3)
        if cond_a != "":
            data_list_cond = utils.fuzzy_knowledge_find(self.conn, "traffic_light", cond_a)
            if data_list_cond == None:
                QMessageBox.about(self.ui, '错误', "变量不存在！")
            else:
                for row in range(len(data_list_cond)):
                    for i in range(8):
                        if i < 6:
                            item1 = QTableWidgetItem(str(data_list_cond[row][i + 1]))
                            item1.setFlags(QtCore.Qt.ItemIsEditable)
                            self.ui.FuzzyKtable_3.setItem(row, i, item1)
                        elif i == 6:
                            item2 = QTableWidgetItem(str(data_list_cond[row][7]))
                            item2.setFlags(QtCore.Qt.ItemIsEditable)
                            self.ui.FuzzyKtable_3.setItem(row, i, item2)
                        elif i == 7:
                            item3 = QTableWidgetItem(str(data_list_cond[row][8]))
                            item3.setFlags(QtCore.Qt.ItemIsEditable)
                            self.ui.FuzzyKtable_3.setItem(row, i, item3)
        if id == "" and cond_a == "":
            data_list = utils.show_all_fuzzy_knowledge(self.conn, "traffic_light")
            for row in range(len(data_list)):
                for i in range(8):
                    if i < 6:
                        item1 = QTableWidgetItem(str(data_list[row][i + 1]))
                        item1.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.FuzzyKtable_3.setItem(row, i, item1)
                    elif i == 6:
                        item2 = QTableWidgetItem(str(data_list[row][7]))
                        item2.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.FuzzyKtable_3.setItem(row, i, item2)
                    elif i == 7:
                        item3 = QTableWidgetItem(str(data_list[row][8]))
                        item3.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.FuzzyKtable_3.setItem(row, i, item3)

    def IsFloat(self, str):
        s = str.split('.')
        if len(s) > 2:
            return False
        else:
            for si in s:
                if not si.isnumeric():
                    return False
            return True


if __name__ == "__main__":
    app = QApplication([])
    stats = Stats()
    stats.ui.show()
    app.exec()
    # print("!!!!!")
