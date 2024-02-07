#импорт необходимых модулей
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
import sqlite3
import time
import threading


#снавное(первое) окно
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled.ui', self)
        self.setFixedSize(800, 600)
        self.start.clicked.connect(self.create)
        self.pushButton.clicked.connect(self.open)
        self.setWindowTitle('Main')


    def create(self):# создать новую гонку
        self.close()
        self.create1 = Create()
        self.create1.show()


    def open(self): # открытие управления уже существующей гонки
        con = sqlite3.connect('races.sqlite')
        cur = con.cursor()
        self.regats = sorted(list(cur.execute('select name_of_race from main')))
        self.regats = list(set(map(lambda x: x[0].strip(), self.regats)))
        name, ok_pressed = QInputDialog.getItem(
            self, "ы", "Выберете название регаты",
            (el for el in self.regats), 1, False)
        if ok_pressed:
            self.year = sorted(list(set(cur.execute('select year from main where name_of_race = ?', (name, )))))
            year, ok_pressed = QInputDialog.getItem(
                self, "ы", "Выберете год проведения регаты",
                (str(el[0]) for el in self.year), 1, False)
            if ok_pressed:
                self.close()
                self.control = Control(list(cur.execute("select id from main where name_of_race = ? and year = ?",
                                                        (name, year)))[0])
                self.control.show()


#
class Create(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('createv21.ui', self)
        self.setFixedSize(800, 600)
        self.setWindowTitle('Сreate')
        self.pushButton.clicked.connect(self.ad)

    def ad(self):

        con = sqlite3.connect('races.sqlite')
        cur = con.cursor()
        #получение данных
        name = self.line_name.text().strip()
        year = self.line_year.text()
        flags = self.line_flags.text()
        starts = self.line_starts.text()
        minuts = 5 if self.minut3.isChecked() else 3
        is_ok = True
        #проверка даных на коректность
        try:
            int(year)
            self.line_year.setStyleSheet("border: 1px solid rgb(255, 255, 255);")
        except Exception:
            is_ok = False
            self.line_year.setStyleSheet("border: 1px solid rgb(255, 0, 0);")
        try:
            int(flags)
            self.line_flags.setStyleSheet("border: 1px solid rgb(255, 255, 255);")
        except Exception:
            is_ok = False
            self.line_flags.setStyleSheet("border: 1px solid rgb(255, 0, 0);")
        try:
            int(starts)
            self.line_starts.setStyleSheet("border: 1px solid rgb(255, 255, 255);")
        except Exception:
            is_ok = False
            self.line_starts.setStyleSheet("border: 1px solid rgb(255, 0, 0);")
        if is_ok:#запись данных в бд, в случае, если данные корректны
            cur.execute("insert into main(name_of_race, year, count_of_flags, count_of_of_starts, duration_of_starts)"
                        "values(?, ?, ?, ?, ?)", (name, year, flags, starts, minuts))
            con.commit()
            con.close()
            self.close()
            self.flags1 = Flags(name, year)
            self.flags1.show()


#
class Flags(QMainWindow):
    def __init__(self, name, year):
        super().__init__()
        self.name = name
        self.year = year
        self.ui()

    def ui(self):
        self.setWindowTitle('Сreate')
        self.setFixedSize(900, 800)
        con = sqlite3.connect('races.sqlite')
        cur = con.cursor()
        self.res = list(cur.execute("select * from main "
                               "where name_of_race = ? and year = ?", (self.name, self.year)))
        self.flags = list(cur.execute("select name from flags"))
        self.id = self.res[0][0]
        self.box_combobox = []
        self.box_startflags = []
        self.box_text = []
        self.pos = [100, 100]
        for i in range(int(self.res[0][-3])): #создание необходимого количества выподающих списков
            self.box_combobox.append(QComboBox(self))
            for el in self.flags:
                self.box_combobox[-1].addItem(el[0])
            self.box_combobox[-1].resize(140, 40)
            self.box_combobox[-1].move(*self.pos)
            self.box_startflags.append(QComboBox(self))
            self.box_startflags[-1].addItems(['Не является \nфлагом предупреждения'] +
                                             [f'Флаг предупреждения \n стартовой группы \n№ {j + 1}'
                                              for j in range(self.res[0][-2])])
            self.box_startflags[-1].resize(140, 40)
            self.box_startflags[-1].move(self.pos[0], self.pos[1] + 60)
            self.pos[0] += 200
            if self.pos[0] > 760:
                self.pos = [100, self.pos[1] + 160]

        self.addButton = QPushButton(self)
        self.addButton.move(800, 770)
        self.addButton.resize(100, 30)
        self.addButton.clicked.connect(self.add)

    def add(self):
        flag = True
        raceid = self.res[0][0]
        data = []
        #проверка на корректность данных
        for i in range(len(self.box_combobox)):
            flagid = self.box_combobox[i].currentIndex() + 1
            pos = i + 1
            try:
                is_start = int(self.box_startflags[i].currentText().split()[-1])
            except ValueError:
                is_start = 0
            data.append([raceid, flagid, pos, is_start])
        if len(set([str(el[-1]) for el in data]) - set("0")) != self.res[0][-2]:
            for el in self.box_startflags:
                el.setStyleSheet("border: 1px solid rgb(255, 0, 0);")
                flag = False
        else:
            for el in self.box_startflags:
                el.setStyleSheet("border: 1px solid rgb(255, 255, 255);")
        for el in self.box_startflags:
            if [str(el[-1]) for el in data].count(el.currentText().split()[-1]) != 1 and el.currentText().split()[0] != 'Не':
                el.setStyleSheet("border: 1px solid rgb(255, 0, 0);")
                flag = False
        if len(set([str(el[1]) for el in data])) != len(data):
            print(len(set([str(el[1]) for el in data])), len(data))
            for el in self.box_combobox:
                if [el1.currentIndex() for el1 in self.box_combobox].count(el.currentIndex()) != 1:
                    el.setStyleSheet("border: 1px solid rgb(255, 0, 0);")
                    flag = False
        else:
            for el in self.box_combobox:
                el.setStyleSheet("border: 1px solid rgb(255, 255, 255);")
        if flag:#запись данных в БД, в случае, если данные корректны
            con = sqlite3.connect('races.sqlite')
            cur = con.cursor()

            for i in range(len(data)):
                cur.execute("insert into main_race(raceid, flagid, pos, for_start) values(?, ?, ?, ?)",
                            (*data[i], ))
            con.commit()
            self.close()
            self.contor = Control((self.id, ))
            self.contor.show()


#
class Control(QMainWindow):
    def __init__(self, id):
        super().__init__()
        self.id = id[0]
        self.aufgaben = []
        self.for_function = []
        uic.loadUi('control.ui', self)
        self.UI()

    def UI(self):
        self.setWindowTitle('Control')
        self.setFixedSize(800, 600)
        con = sqlite3.connect('races.sqlite')
        cur = con.cursor()
        self.data = list(cur.execute("select m_n.flagid, m_n.pos, m_n.for_start, m.duration_of_starts "
                                     "from main_race as m_n join main as m where m_n.raceid = ? and m.id = ?",
                                     (self.id, self.id)))
        self.flags = list(map(lambda x: [int(x[0]), str(x[1])],
                              cur.execute(f"select * from flags where id in {tuple([el[0] for el in self.data])}")))
        self.flags_in_use = {}
        for el in self.flags:
            self.flags_in_use[el[1]] = el[0]
        self.comboBox_flags.addItems(list(filter(lambda x: x in ['P', 'I', 'Z', 'Черный флаг', "U"], [el[1] for el in self.flags])))
        self.comboBox_group.addItems(list(filter(lambda x: x != '0', map(lambda x: str(x[2]), self.data))))
        self.comboBox_f.addItems([el[1] for el in self.flags] + ['никакой'])
        self.comboBox_2.addItems(['Не трогать остальные флаги', 'Опустить все другие флаги'])
        self.pos = [[0] for _ in range(len(self.data))]
        print(self.data)
        print()
        print()
        self.pushButton.clicked.connect(self.start)
        self.pushButton_2.clicked.connect(self.add1)
        self.ppp = threading.Thread(target=self.add)
        self.ppp.start()


    def start(self):
        start = self.comboBox_group.currentText()
        podg = self.comboBox_flags.currentText()
        for_start = [list(filter(lambda x: str(start) == str(x[2]), self.data))[0][1], 1, 1]
        for_dur = [list(filter(lambda x: self.flags_in_use[podg] == x[0], self.data))[0][1], 1, self.data[0][-1] - 2]
        for_dur1 = [list(filter(lambda x: self.flags_in_use[podg] == x[0], self.data))[0][1], 0, 1]
        for_end = [list(filter(lambda x: str(start) == str(x[2]), self.data))[0][1], 0, 0]
        for el in [for_start, for_dur, for_dur1, for_end]:
            self.for_function.append(el)


    def add(self):
        while True:
            if self.for_function:
                print(*self.for_function[0][:2])
                t = self.for_function[0][-1]
                self.pos[self.for_function[0][0]] = 1
                self.for_function = self.for_function[1:]
                # print(self.for_function)
                time.sleep(t * 6)


    def add1(self):
        flag = self.comboBox_f.currentText()
        q = []
        if flag in self.flags_in_use:
            q.append([self.flags_in_use[flag], 1, 0])
        if self.comboBox_2.currentText() == 'Опустить все другие флаги':
            self.for_function = []
            for i in range(len(self.pos)):
                if self.pos[i] == 1:
                    q.append([i, 0, 0])
        for el in q:
            print(*el)




#
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())