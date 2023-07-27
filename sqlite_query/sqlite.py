from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import QtWidgets, QtCore, uic, QtGui
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import sys
import sqlite3
import pandas as pd
from sqlite3 import Error
 
class AnotherWindow(QWidget):
    # create a customized signal 
    submitted = QtCore.pyqtSignal(str) # "submitted" is like a component name 
    def __init__(self):
        super().__init__()
        uic.loadUi('HW2_sub.ui', self)
        # self.setGeometry(600, 200, 400, 400)
        
        self.setWindowTitle('全文展示')
        database = r"database_test.sqlite"
        self.conn = create_connection(database)
        
        # Signal
        self.pBut_to_main.clicked.connect(self.on_submit)
        self.pBut_event_info.clicked.connect(self.event_info)
    
    def passInfo(self, paperid):
        show_authors(self, paperid)
        show_detail(self, paperid)
        self.label_ID.setText("ID:{}".format(paperid))
    
    def event_info(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("論文型態")
        dlg.setText(""" 論文型態共有 Poster, Oral, Spotlight 三種 """)
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes)
        buttonY = dlg.button(QMessageBox.StandardButton.Yes)
        buttonY.setText('OK!')
        buttonY.setStyleSheet("QPushButton{background-color: rgb(30, 100, 110);}")
        dlg.setIcon(QMessageBox.Icon.Information)
        button = dlg.exec()
     
    def on_submit(self):
        self.close()
        
class TableModel(QtCore.QAbstractTableModel):
     
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
 
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()] #pandas's iloc method
            return str(value)
 
        if role == Qt.ItemDataRole.TextAlignmentRole:          
            return Qt.AlignmentFlag.AlignVCenter + Qt.AlignmentFlag.AlignHCenter
         
        if role == Qt.ItemDataRole.BackgroundRole and (index.row()%2 == 1):
            return QtGui.QColor('#E4DACE')

        if role == Qt.ItemDataRole.BackgroundRole and (index.row()%2 == 0):
            return QtGui.QColor('#1E646E')
 
    def rowCount(self, index):
        return self._data.shape[0]
 
    def columnCount(self, index):
        return self._data.shape[1]
 
    # Add Row and Column header
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole: # more roles
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
 
            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
 
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
 
        uic.loadUi('HW2_main.ui', self)
        # self.setWindowTitle('Chen \'s APP')
        self.table = self.tableView
        
        # Signals
        database = r"database_test.sqlite"
        self.conn = create_connection(database)
        self.setWindowTitle('論文查詢系統')
        
        self.history = pd.DataFrame()
 
        # Signals
        ## Tab1_cross
        self.lineEdit_title.returnPressed.connect(self.search_cross)
        self.lineEdit_name.returnPressed.connect(self.search_cross)
        self.p_But_tab1_search.clicked.connect(self.search_cross)
        self.lineEdit_title.returnPressed.connect(self.hist_cross)
        self.lineEdit_name.returnPressed.connect(self.hist_cross)
        self.p_But_tab1_search.clicked.connect(self.hist_cross)
        self.pBut_tab1_info.clicked.connect(self.info_1)
        
        ## Tab2_condition
        self.comboBox_type.currentIndexChanged.connect(self.search_cond)
        self.lineEdit_condition.returnPressed.connect(self.search_cond)
        self.p_But_tab2_choose.clicked.connect(self.search_cond)
        self.lineEdit_condition.returnPressed.connect(self.hist_cond)
        self.p_But_tab2_choose.clicked.connect(self.hist_cond)
        self.comboBox_type.currentIndexChanged.connect(self.hist_cond)
        self.pBut_tab2_info.clicked.connect(self.info_2)
        
        ## Tab3_event
        self.comboBox_event.currentIndexChanged.connect(self.search_event)
        self.lineEdit_event.returnPressed.connect(self.search_event)
        self.p_But_tab3_event.clicked.connect(self.search_event)
        self.lineEdit_event.returnPressed.connect(self.hist_event)
        self.p_But_tab3_event.clicked.connect(self.hist_event)
        self.comboBox_event.currentIndexChanged.connect(self.hist_event)
        self.pBut_tab3_info.clicked.connect(self.info_3)
        
        ## history
        self.p_But_clear_hist.clicked.connect(self.hist_clear)
        self.p_But_tab4_info.clicked.connect(self.info_history)
        
        ## table & sub_window
        self.table.doubleClicked.connect(self.rowSelected)
        self.actionSave_Data.triggered.connect(self.saveData)
        self.pBut_gosub.clicked.connect(self.call_subWin)
        
        self.actionabout.triggered.connect(self.appAbout)
        self.actionEXIT.triggered.connect(self.appEXIT)
        
        
    # Slots
    ## Tab1_crosss
    def search_cross(self):
        title_key = self.lineEdit_title.text()
        name_key = self.lineEdit_name.text()
        '''
        select id, title, abstract 
            from Papers 
                where title like '%network%' and 
                    id in (
                        select distinct(paperid) 
                        from PaperAuthors A, Authors B, Papers C
                        where B.name like '%chen%'
                        and A.authorid = B.id and A.paperid = C.id
                        )
        '''
        sql = "select id "
         
        if self.checkBox_title.isChecked():
            sql = sql + ",title"
        if self.checkBox_type.isChecked():
            sql = sql + ",eventtype"
        if self.checkBox_abstract.isChecked():
            sql = sql + ",abstract"   
        if self.checkBox_text.isChecked():
            sql = sql + ",papertext"
         
        sql = sql + " from Papers where title like '% " + title_key + "%' and \
                        id in (select distinct(paperid) from PaperAuthors A, Authors B\
                            where B.name like '%" + name_key + "%' \
                            and A.authorid = B.id )"
                                               
        with self.conn:
            self.rows = SQLExecute(self, sql)
            if len(self.rows) > 0: 
                ToTableView(self, self.rows)
        self.label_row_number.setText(str(len(self.rows)))
    
    ## Tab2_condition
    def search_cond(self):
        sql = "select id"
        
        if self.checkBox_title_2.isChecked():
            sql = sql + ",title"
        if self.checkBox_type_2.isChecked():
            sql = sql + ",eventtype"
        if self.checkBox_abstract_2.isChecked():
            sql = sql + ",abstract"   
        if self.checkBox_text_2.isChecked():
            sql = sql + ",papertext"
        
        if self.comboBox_type.currentText() == "Title":
            title_key = self.lineEdit_condition.text()
            sql = sql + " from Papers where Title like '%" + title_key + "%'"
        
        elif self.comboBox_type.currentText() == "Abstract":
            abs_key = self.lineEdit_condition.text()
            sql = sql + " from Papers where Abstract like '%" + abs_key + "%'"
            
        elif self.comboBox_type.currentText() == "Paper Text":
            ppt_key = self.lineEdit_condition.text()
            sql = sql + " from Papers where PaperText like '%" + ppt_key + "%'"
            
        else:
            name_key = self.lineEdit_condition.text()
            sql = sql + " from Papers where id in \
                            (select distinct(paperid) from PaperAuthors A, Authors B \
                            where B.name like '%" + name_key + "%'and A.authorid = B.id )"
        
        with self.conn:
            self.rows = SQLExecute(self, sql)
            if len(self.rows) > 0: 
                ToTableView(self, self.rows)
        self.label_row_number.setText(str(len(self.rows)))
        
    ## Tab3_all        
    def search_event(self):
        event_key = self.lineEdit_event.text()
        sql = " select id "
         
        if self.checkBox_title_3.isChecked():
            sql = sql + ",title"
        if self.checkBox_type_3.isChecked():
            sql = sql + ",eventtype"
        if self.checkBox_abstract_3.isChecked():
            sql = sql + ",abstract"   
        if self.checkBox_text_3.isChecked():
            sql = sql + ",papertext"
            
        if self.comboBox_event.currentText() == "All":
            type_key = ""
        else:
            type_key = "{}".format(self.comboBox_event.currentText())
         
        sql = sql + " from Papers where eventtype like  '%" + type_key +  \
                  "%' and (title like '%" + event_key + "%' or abstract like '%" + event_key + \
                    "%' or papertext like '%" + event_key + "%') "
                
        with self.conn:
            self.rows = SQLExecute(self, sql)
            if len(self.rows) > 0: 
                ToTableView(self, self.rows)
        self.label_row_number.setText(str(len(self.rows)))
    
    ## history
    def hist_cross(self):
        
        if self.lineEdit_name.text() != "":
            if self.lineEdit_title.text() != "":
                hist_name = self.lineEdit_name.text()
                hist_title = self.lineEdit_title.text()
                hist = "{},{}".format(hist_name, hist_title)
                Type = "A"
            else:
                hist_name = self.lineEdit_name.text()
                hist_title = "全數標題"
                hist = "{},{}".format(hist_name, hist_title)
                Type = "B1"      
        else:
            if self.lineEdit_title.text() != "":
                hist_name = "全數作者"
                hist_title = self.lineEdit_title.text()
                hist = "{},{}".format(hist_name, hist_title)
                Type = "B2"
            else:
                hist_name = "全數作者"
                hist_title = "全數標題" 
                hist = "{},{}".format(hist_name, hist_title)
                Type = "C"
            
        hist_cross = pd.DataFrame({"搜尋": ["交叉搜尋"], 
                                   "型態" : [Type],
                                   "關鍵字" : [hist], 
                                   "總計" : [self.label_row_number.text()]})
        
        self.history = self.history.append(hist_cross)
        ToTableView_hist(self, self.history)
        
    def hist_cond(self):
        hist =  self.lineEdit_condition.text() 

        hist_cond = pd.DataFrame({"搜尋": ["條件搜尋"],
                                  "型態" : [self.comboBox_type.currentText()],
                                  "關鍵字" : [hist],
                                  "總計" : [self.label_row_number.text()]})
        self.history = self.history.append(hist_cond)
        ToTableView_hist(self, self.history)
    
    def hist_event(self):
        hist =   self.lineEdit_event.text() 
              
        hist_all = pd.DataFrame({"搜尋": ["型態搜尋"],
                                  "型態" : [self.comboBox_event.currentText()],
                                  "關鍵字" : [hist],
                                  "總計" : [self.label_row_number.text()]})
        self.history = self.history.append(hist_all)
        ToTableView_hist(self, self.history)
    
    def hist_clear(self):
        self.table_hist.setModel(None)
    
    def info_1(self):
        title_1 = "交叉搜尋"
        text_1 = """提供作者名稱與論文標題的關鍵字搜尋，若搜尋欄為空白表不指定特殊關鍵字"""
        return info(self, title_1, text_1)
    
    def info_2(self):
        title_2 = "條件搜尋"
        text_2 = """提供指定資料庫特定欄位進行關鍵字搜尋，若搜尋欄為空白表不指定特殊關鍵字"""
        return info(self, title_2, text_2)
    
    def info_3(self):
        title_3 = "型態搜尋"
        text_3 = """提供論文型態的關鍵字搜尋，若搜尋欄為空白表不指定特殊關鍵字"""
        return info(self, title_3, text_3)

    def info_history(self):
        title_1 = "歷程記錄"
        text_1 = """此頁面紀錄使用本系統的搜尋紀錄，並附設清除紀錄之按鍵\n\n
        [備註]\n
        交叉搜尋的型態:\n
            A  : 作者與標題皆有指定特殊關鍵字\n
            B1 : 作者指定特殊關鍵字,標題不指定\n
            B2 : 標題指定特殊關鍵字,作者不指定\n
            C  : 作者與標題皆不指定特殊關鍵字
        """
        return info(self, title_1, text_1)
        
    def rowSelected(self, mi):
        show_id(self, self.df.iloc[mi.row(), 0])
    
    def call_subWin(self):
        self.anotherwindow = AnotherWindow()
        if self.label_select_id.text() != "--":
            self.anotherwindow.passInfo(self.label_select_id.text())
            self.anotherwindow.show()
        else:
            self.label_select_id.setText( "--" )
            dlg = QMessageBox(self)
            dlg.setWindowTitle("錯誤")
            dlg.setText("請選取要查看的論文 !!!")
            dlg.setStandardButtons(QMessageBox.StandardButton.Yes)
            buttonY = dlg.button(QMessageBox.StandardButton.Yes)
            buttonY.setText('OK')
            dlg.setIcon(QMessageBox.Icon.Information)
            button = dlg.exec()
        

    def saveData(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', 
            "", "EXCEL files (*.xlsx)")
        if len(fname) != 0:
            self.df.to_excel(fname)
    
    def appAbout(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(" 關於這個APP ")
        dlg.setText("""\
        開發者 : Chun-Yi Chen \n\n
        參考資料 : \n
        [程式]\n
        Chun-Chao Wang : Python App Design and Programming \n
        (https://ntpuccw.blog/python-in-learning/) \n
        [設計] \n
        Color : https://reurl.cc/Lmmgd3\n
        icon : "https://icons8.com/icon/Y8wvT6XLnWOK/history"\n\n
        若您有使用上的問題,歡迎寄信到 asd977646@gmail.com ,很樂意為您服務 :) """)
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes)
        buttonY = dlg.button(QMessageBox.StandardButton.Yes)
        buttonY.setText('再次感謝!!!')
        buttonY.setStyleSheet("QPushButton{background-color: rgb(30, 100, 110);}")
        # dlg.setIcon(QMessageBox.Icon.Information)
        button = dlg.exec()
 
    def appEXIT(self):
        self.conn.close() # close database
        self.close() # close app
     
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
 
    return conn
 
def SQLExecute(self, SQL):
    self.cur = self.conn.cursor()
    self.cur.execute(SQL)
    rows = self.cur.fetchall()
 
    if len(rows) == 0: 
        dlg = QMessageBox(self)
        dlg.setWindowTitle("SQL Information: ")
        dlg.setText("No data match the query !!!")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes)
        buttonY = dlg.button(QMessageBox.StandardButton.Yes)
        buttonY.setText('OK')
        dlg.setIcon(QMessageBox.Icon.Information)
        button = dlg.exec()
        # return
    return rows
 
def ToTableView(self, rows):
    names = [description[0] for description in self.cur.description]# extract column names
    self.df = pd.DataFrame(rows)
    self.model = TableModel(self.df)
    self.table.setModel(self.model)
    self.df.columns = names
    self.df.index = range(1, len(rows)+1)
     
def show_id(self, paperid):
    self.label_select_id.setText(str(paperid))

def show_authors(self, paperid):
    sql = "select Name \
            from Authors A, PaperAuthors B \
            where B.Paperid = " + str(paperid) + " and A.Id=B.AuthorId"
    with self.conn:
        self.rows = SQLExecute(self, sql)
        names =""
        for row in self.rows:
            names = names + row[0] +" \n"
        self.textBrowser_Authors.setText(names)

def show_detail(self, paperid):
    sql = "select Title, Abstract, EventType, PaperText, imagefile\
            from Papers \
            where Id = " + str(paperid) 
    
    with self.conn:
        self.rows = SQLExecute(self, sql)
        self.label_title.setText(self.rows[0][0])
        self.textBrowser_Abstract.setText(self.rows[0][1])
        self.label_Eventtype.setText(self.rows[0][2])
        self.textBrowser_Papertext.setText(self.rows[0][3])
        self.label_image.setPixmap(QPixmap(u"NIP2015_Images/" + str(self.rows[0][4])))

def ToTableView_hist(self, rows):
    hist_names = ["搜尋", "型態", "關鍵字", "總計"] # extract column names
    self.hist_df = pd.DataFrame(rows)
    self.hist_model = TableModel(self.hist_df)
    self.table_hist.setModel(self.hist_model)
    self.hist_df.columns = hist_names
    self.hist_df.index = range(1, len(rows)+1)


def info(self, title, text):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        dlg.setText(text)
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes)
        buttonY = dlg.button(QMessageBox.StandardButton.Yes)
        buttonY.setText('OK!')
        buttonY.setStyleSheet("QPushButton{background-color: rgb(30, 100, 110);}")
        dlg.setIcon(QMessageBox.Icon.Information)
        button = dlg.exec()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
 
if __name__ == '__main__':
    main()