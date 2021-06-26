import sys
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import *
import build_db
import datetime


class CredibilityKnowledge:
    def __init__(self):
        self.ui = uic.loadUi("./ui/credibility.ui")  # 组件名称查看credibility.ui
        self.set_ui()
        self.show_knowledge('', '')  # 展示所有知识
        self.ui.add.clicked.connect(self.add_knowledge)
        self.ui.update.clicked.connect(self.update_knowledge)
        self.ui.delete_2.clicked.connect(self.delete_knowledge)
        self.ui.search_2.clicked.connect(self.search_knowledge)
        self.ui.clear.clicked.connect(self.clear_all)
        build_db.create_credibility_knowledge_table()

    def set_ui(self):
        ico_path = './image/light.ico'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(ico_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.setWindowIcon(icon)
        self.ui.setWindowTitle('可信度知识库')
        self.ui.resize(1600, 600)
        self.ui.table.horizontalHeader().setStretchLastSection(True)
        self.ui.table.setRowCount(20)
        self.ui.table.setColumnWidth(0, 180)
        self.ui.table.setColumnWidth(1, 180)
        self.ui.table.setColumnWidth(2, 100)
        self.ui.table.setColumnWidth(3, 100)
        self.ui.table.setColumnWidth(4, 100)
        self.ui.table.setColumnWidth(5, 100)

    def show_knowledge(self, type, content):
        self.ui.table.clearContents()
        res = build_db.search_credibility_knowledge(type, content)
        line = 0
        if res != None:
            for row in range(len(res)):
                for i in range(6):
                    if i < 4:
                        item1 = QTableWidgetItem(str(res[row][i + 1]))
                        item1.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.table.setItem(row, i, item1)
                    elif i == 4:
                        item2 = QTableWidgetItem(str(res[row][6]))
                        item2.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.table.setItem(row, i, item2)
                    elif i == 5:
                        item3 = QTableWidgetItem(str(res[row][5]))
                        item3.setFlags(QtCore.Qt.ItemIsEditable)
                        self.ui.table.setItem(row, i, item3)

    def search_knowledge(self):
        msg = ''
        limit = 0
        which = 0
        condition = self.ui.condition_line.text().strip()
        if condition != '':
            limit += 1
            which = 0
        conclusion = self.ui.conclusion_line.text().strip()
        if conclusion != '':
            limit += 1
            which = 1
        condition_credibility = self.ui.condition_credibility.text().strip()
        if condition_credibility != '':
            limit += 1
            which = 2
            if (self.IsFloat(condition_credibility)):
                condition_credibility = float(condition_credibility)
                if condition_credibility > 1 or condition_credibility < 0:
                    msg += '条件可信度不在0-1之间！\n'
            else:
                msg += '表示条件可信度的不是一个数！\n'
        knowledge_credibility = self.ui.knowledge_credibility.text().strip()
        if knowledge_credibility != '':
            limit += 1
            which = 3
            if self.IsFloat(knowledge_credibility):
                knowledge_credibility = float(knowledge_credibility)
                if knowledge_credibility > 1 or knowledge_credibility < 0:
                    msg += '结论可信度不在0-1之间！\n'
            else:
                msg += '表示结论可信度的不是一个数！\n'
        update_person = self.ui.update_person.text().strip()
        if update_person != '':
            limit += 1
            which = 4
        if limit > 1:
            QMessageBox.critical(self.ui, 'Error', '只能输入一个约束条件！')
            return
        if msg != '':
            QMessageBox.critical(self.ui, 'Error', msg)
            return
        if limit == 1:
            type = ['CONDITION', 'CONCLUSION', 'CONDITION_CREDIBILITY', 'KNOWLEDGE_CREDIBILITY', 'UPDATE_PERSON']
            content = [condition, conclusion, condition_credibility, knowledge_credibility, update_person]
            self.show_knowledge(type[which], content[which])

    def update_knowledge(self):
        if build_db.num_of_record() == 0:
            QMessageBox.critical(self.ui, 'Error', '知识库中无知识')
            return
        id = self.ui.ID_line.text().strip()
        if id == '':
            QMessageBox.critical(self.ui, 'Error', 'ID为空')
            return
        if id.isnumeric():
            id = int(id)
            if id > build_db.num_of_record() or id < 0:
                QMessageBox.critical(self.ui, 'Error', 'ID超出范围')
            else:
                msg = ''
                condition = self.ui.condition_line.text().strip()
                print(type(condition))
                conclusion = self.ui.conclusion_line.text().strip()
                condition_credibility = self.ui.condition_credibility.text().strip()
                if condition_credibility != '':
                    if (self.IsFloat(condition_credibility)):
                        condition_credibility = float(condition_credibility)
                        if condition_credibility > 1 or condition_credibility < 0:
                            msg += '条件可信度不在0-1之间！\n'
                    else:
                        msg += '表示条件可信度的不是一个数！\n'
                knowledge_credibility = self.ui.knowledge_credibility.text().strip()
                if knowledge_credibility != '':
                    if self.IsFloat(knowledge_credibility):
                        knowledge_credibility = float(knowledge_credibility)
                        if knowledge_credibility > 1 or knowledge_credibility < 0:
                            msg += '结论可信度不在0-1之间！\n'
                    else:
                        msg += '表示结论可信度的不是一个数！\n'
                update_person = self.ui.update_person.text().strip()
                if msg != '':
                    QMessageBox.critical(self.ui, 'Error', msg)
                    return
                else:
                    coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                    if condition != '':
                        build_db.update_credibility_knowledge('ID', id, 'CONDITION', condition)
                        coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                        self.ui.table.item(id - 1, 5).setText(coolection_time)
                        self.ui.table.item(id - 1, 0).setText(condition)
                    if conclusion != '':
                        build_db.update_credibility_knowledge('ID', id, 'CONCLUSION', conclusion)
                        coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                        self.ui.table.item(id - 1, 5).setText(coolection_time)
                        self.ui.table.item(id - 1, 1).setText(conclusion)
                    if isinstance(condition_credibility,
                                  float) and condition_credibility < 1 and condition_credibility > 0:
                        build_db.update_credibility_knowledge('ID', id, 'CONDITION_CREDIBILITY', condition_credibility)
                        coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                        self.ui.table.item(id - 1, 5).setText(coolection_time)
                        self.ui.table.item(id - 1, 2).setText(str(condition_credibility))
                    if isinstance(knowledge_credibility,
                                  float) and knowledge_credibility < 1 and knowledge_credibility > 0:
                        build_db.update_credibility_knowledge('ID', id, 'KNOWLEDGE_CREDIBILITY', knowledge_credibility)
                        coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                        self.ui.table.item(id - 1, 5).setText(coolection_time)
                        self.ui.table.item(id - 1, 3).setText(str(knowledge_credibility))
                    if update_person != '':
                        build_db.update_credibility_knowledge('ID', id, 'UPDATE_PERSON', update_person)
                        coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                        self.ui.table.item(id - 1, 5).setText(coolection_time)
                        self.ui.table.item(id - 1, 4).setText(update_person)
                    self.clear_all()

        elif id[0] == '-' and id[1:].isnumeric():
            QMessageBox.critical(self.ui, 'Error', 'ID为负数')
        else:
            QMessageBox.critical(self.ui, 'Error', 'ID不为整数')

    def delete_knowledge(self):
        if build_db.num_of_record() == 0:
            QMessageBox.critical(self.ui, 'Error', '知识库中无知识')
            return
        id = self.ui.ID_line.text().strip()
        if id == '':
            QMessageBox.critical(self.ui, 'Error', 'ID为空')
            return
        if id.isnumeric():
            id = int(id)
            if id > build_db.num_of_record() or id < 0:
                QMessageBox.critical(self.ui, 'Error', 'ID超出范围')
            else:
                build_db.del_credibility_knowledge('ID', id)
                self.ui.table.removeRow(id - 1)
        elif id[0] == '-' and id[1:].isnumeric():
            QMessageBox.critical(self.ui, 'Error', 'ID为负数')
        else:
            QMessageBox.critical(self.ui, 'Error', 'ID不为整数')

    def add_knowledge(self):
        msg = ''
        condition = self.ui.condition_line.text().strip()
        if condition == '':
            msg += '缺少条件！\n'
        conclusion = self.ui.conclusion_line.text().strip()
        if conclusion == '':
            msg += '缺少结论！\n'
        condition_credibility = self.ui.condition_credibility.text().strip()
        if condition_credibility != '':
            if (self.IsFloat(condition_credibility)):
                condition_credibility = float(condition_credibility)
                if condition_credibility > 1 or condition_credibility < 0:
                    msg += '条件可信度不在0-1之间！\n'
            else:
                msg += '表示条件可信度的不是一个数！\n'
        else:
            msg += '缺少条件可信度！\n'
        knowledge_credibility = self.ui.knowledge_credibility.text().strip()
        if knowledge_credibility != '':
            if self.IsFloat(knowledge_credibility):
                knowledge_credibility = float(knowledge_credibility)
                if knowledge_credibility > 1 or knowledge_credibility < 0:
                    msg += '结论可信度不在0-1之间！\n'
            else:
                msg += '表示结论可信度的不是一个数！\n'
        else:
            msg += '缺少知识可信度！\n'
        update_person = self.ui.update_person.text().strip()
        if update_person == '':
            msg += '缺少更新人！\n'
        if msg != '':
            QMessageBox.critical(self.ui, 'Error', msg)
            return
        else:
            build_db.add_credibility_knowledge(condition, conclusion, condition_credibility, knowledge_credibility,
                                               update_person)  # 数据库中添加记录
            coolection_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            row = build_db.num_of_record()
            if row >= 20:
                self.ui.table.insertRow(self.ui.table.rowCount())
            row = row - 1
            self.ui.table.setItem(row, 5, QTableWidgetItem(coolection_time))
            self.ui.table.item(row, 5).setFlags(QtCore.Qt.ItemIsEditable)
            self.ui.table.setItem(row, 0, QTableWidgetItem(condition))
            self.ui.table.item(row, 0).setFlags(QtCore.Qt.ItemIsEditable)
            self.ui.table.setItem(row, 1, QTableWidgetItem(conclusion))
            self.ui.table.item(row, 1).setFlags(QtCore.Qt.ItemIsEditable)
            self.ui.table.setItem(row, 2, QTableWidgetItem(str(condition_credibility)))
            self.ui.table.item(row, 2).setFlags(QtCore.Qt.ItemIsEditable)
            self.ui.table.setItem(row, 3, QTableWidgetItem(str(knowledge_credibility)))
            self.ui.table.item(row, 3).setFlags(QtCore.Qt.ItemIsEditable)
            self.ui.table.setItem(row, 4, QTableWidgetItem(update_person))
            self.ui.table.item(row, 4).setFlags(QtCore.Qt.ItemIsEditable)
            return

    def clear_all(self):  # 清空所有的输入项
        self.ui.ID_line.clear()
        self.ui.condition_line.clear()
        self.ui.conclusion_line.clear()
        self.ui.condition_credibility.clear()
        self.ui.knowledge_credibility.clear()
        self.ui.update_person.clear()
        self.show_knowledge('', '')

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
    gui = CredibilityKnowledge()
