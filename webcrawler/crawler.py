from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
# from PyQt6.QtWebEngineWidgets import QWebEngineView 
from PyQt6 import QtCore, QtWidgets, QtGui, uic
from PyQt6.QtWidgets import QWidget, QMessageBox, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from bs4 import BeautifulSoup
from matplotlib import dates
import pyqtgraph as pg
import pandas as pd
import numpy as np
import requests
import urllib3
import folium
import sys
import io
import os

class PTT_Window(QWidget):
    # create a customized signal 
    submitted = QtCore.pyqtSignal(str) # "submitted" is like a component name 
    def __init__(self):
        super().__init__()
        uic.loadUi('crawler_sub_PTT.ui', self)
        # self.setGeometry(600, 200, 400, 400)
        
        self.setWindowTitle('文章展示')
        
        #Signal
        self.pBut_to_main.clicked.connect(self.on_submit)
        
    # Slot
    def passInfo(self, url):
        self.label_board.setText(url)
        self.PTT_main(url)
        self.Comments(url)
    
    def PTT_main(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        header = soup.find_all('span','article-meta-value')

        # 作者
        author = header[0].text
        # 看版
        board = header[1].text
        # 標題
        title = header[2].text
        # 日期
        date = header[3].text
        
        self.label_author.setText(author)
        self.label_board.setText(board)
        self.label_title.setText(title)
        self.label_time.setText(date)
        
        main_container = soup.find(id='main-container')
        all_text = main_container.text
        pre_text = all_text.split('--')[0]
        texts = pre_text.split('\n') 
        contents = texts[2:]
        content = '\n'.join(contents)
        self.textBrowser_Papertext.setText(content)
    
    def Comments(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        main_container = soup.find(id='main-container')
        comments = main_container.find_all("div", class_="push")
            
        Push_tag = [i.find("span", class_="push-tag").text for i in comments]
        Push_userid = [i.find("span", class_="push-userid").text for i in comments]
        Push_content = [i.find("span", class_="push-content").text.strip().lstrip(":") for i in comments]
        Push_time = [i.find("span", class_="push-ipdatetime").text for i in comments]
        
        self.df = pd.DataFrame({
            "Tag" : Push_tag,
            "ID" : Push_userid,
            "Content" : Push_content,
            "Time" : Push_time
        })
        self.model = TableModel(self.df)
        self.tableView_Comment.setModel(self.model)

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
            # return Qt.AlignmentFlag.AlignVCenter + Qt.AlignmentFlag.AlignLeft
         
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
 
            # if orientation == Qt.Orientation.Vertical:
            #     return str(self._data.index[section])
 
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('crawler_main.ui', self)
        self.setWindowTitle('運動速報')
        self.PTT_show_baseball()
        self.PTT_show_NBA()
        self.PTT_show_FORMULA1()
        self.CPBL_standings()
        self.CPBL_standings_spe()
        self.NBA_standings()
        self.F1_standings()
        self.LTN_titleSearch()
        self.ETtoday_titleSearch()
        self.F1_Circuit()
        
        # Signals
        self.tView_PTT_baseball.doubleClicked.connect(self.rowSelected_baseball)
        self.tView_PTT_NBA.doubleClicked.connect(self.rowSelected_NBA)
        self.tView_PTT_FORMULA1.doubleClicked.connect(self.rowSelected_FORMULA1)
        
        self.pBut_re_baseball.clicked.connect(self.PTT_show_baseball)
        self.pBut_re_NBA.clicked.connect(self.PTT_show_NBA)
        self.pBut_re_F1.clicked.connect(self.PTT_show_FORMULA1)
        self.pBut_info_baseball.clicked.connect(self.info_1)
        self.pBut_info_NBA.clicked.connect(self.info_2)
        self.pBut_info_F1.clicked.connect(self.info_3)
        
        self.actionbaseball.triggered.connect(self.saveData_baseball)
        self.actionNBA.triggered.connect(self.saveData_NBA)
        self.actionFormula1.triggered.connect(self.saveData_FORMULA1)
        self.actionNBA_EAST.triggered.connect(self.saveData_NBA_E)
        self.actionNBA_WEST.triggered.connect(self.saveData_NBA_W)
        self.actionF1_drivers.triggered.connect(self.saveData_F1_C)
        self.actionF1_constructor.triggered.connect(self.saveData_F1_D)
        self.actionF1_sch.triggered.connect(self.saveData_F1_sch)
        
        self.actionabout.triggered.connect(self.appAbout)
        self.actionEXIT.triggered.connect(self.appEXIT)
        
    # Slots
    def CPBL_standings(self):
        urllib3.disable_warnings() 
        url = "https://www.cpbl.com.tw/standings/season"
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        # 排名
        results = soup.find_all("div", class_ = "team-w-trophy")
        for i in range(5):   
            rank = results[i+1]('a')[0].text
            setlabel = "self.label_CPBL_rank_"+str(i+1)+".setText(rank)"
            exec(setlabel)
        
        for i in range(5):   
            rank = results[i+1]('a')[0].text
            setlabel = "self.label_CPBL_rank_"+str(i+1)+"_2.setText(rank)"
            exec(setlabel)
        
        # 數據
        results_table = soup.find_all("td", class_ = "num")
        WIN = []
        for i in range(5):
            for j in range(5):
                win = results_table[13*i + j].text
                WIN.append(win)
        
        ## 數據填入
        header = ['game', 'win', 'rate', 'diff', 'loss'] # 出賽, 戰績, 勝率, 勝場差, 淘汰指數
        for j in header:
            for i in range(5):
                num = WIN[i*5 + header.index(j)]
                setlabel = "self.label_CPBL_rank_"+str(i+1)+"_{}.setText(num)".format(j)
                exec(setlabel)
        
    def CPBL_standings_spe(self):
        urllib3.disable_warnings() 
        url = "https://www.cpbl.com.tw/standings/special"
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 數據
        results_table = soup.find_all("td", class_ = "num")
        WIN = []
        for i in range(5):
            for j in range(6):
                win = results_table[6*i + j].text
                WIN.append(win)
        
        ## 數據填入
        header = ['game', 'win', 'rate', 'diff', 'loss', 'ot'] 
        for j in header:
            for i in range(5):
                num = WIN[i*6 + header.index(j)]
                setlabel = "self.label_CPBL_rank_"+str(i+1)+"_{}_2.setText(num)".format(j)
                exec(setlabel)
    
    def NBA_standings(self):
        url = "https://www.cbssports.com/nba/standings/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        
        rank = soup.find_all("span", class_ = "TeamName")
        Rank = [i.text for i in rank]
        
        table = soup.find_all("td", class_ = "TableBase-bodyTd TableBase-bodyTd--number")
        Team_E = []
        for i in range(15):
            team = []
            for j in range(4):
                t = table[13*i+j].string.replace(" ", "").replace("\n",  "")
                team.append(t)
            Team_E.append(team)
        
        self.df_NBA_E = pd.DataFrame({
            "Rank" : pd.Series(np.arange(1,16)),
            "Team" : Rank[0:15],
            "W" : [i[0] for i in Team_E],
            "L" : [i[1] for i in Team_E],
            "PCT" : [i[2] for i in Team_E],
            "GB" : [i[3] for i in Team_E]
        })
        self.tView_NBA_E.setModel(TableModel(self.df_NBA_E))
        
        Team_W = []
        for i in range(15, 30):
            team = []
            for j in range(4):
                t = table[13*i+j].string.replace(" ", "").replace("\n",  "")
                team.append(t)
            Team_W.append(team)

        self.df_NBA_W = pd.DataFrame({
            "Rank" : pd.Series(np.arange(1,16)),
            "Team" : Rank[15:30],
            "W" : [i[0] for i in Team_W],
            "L" : [i[1] for i in Team_W],
            "PCT" : [i[2] for i in Team_W],
            "GB" : [i[3] for i in Team_W]
        })
        self.tView_NBA_W.setModel(TableModel(self.df_NBA_W))
    
    def F1_standings(self):
        url = "https://www.bbc.com/sport/formula1/drivers-world-championship/standings"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser") 
        table = soup.find_all("span", class_ = "gs-u-vh")
        
        Drivers = []
        for i in range(21):
            team = []
            for j in range(5):
                t = table[2+5*i+j].string
                team.append(t)
            Drivers.append(team)

        self.df_F1_D = pd.DataFrame({
            "Rank" : [i[0] for i in Drivers],
            "Driver" : [i[1] for i in Drivers],
            "Team" : [i[2] for i in Drivers],
            "Wins" : [i[3] for i in Drivers],
            "Points" : [i[4] for i in Drivers]
        })
        self.tView_F1_driver.setModel(TableModel(self.df_F1_D))
        
        url = "https://www.bbc.com/sport/formula1/constructors-world-championship/standings"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser") 
        table = soup.find_all("span", class_ = "gs-u-vh")
        
        Constructors = []
        for i in range(10):
            constructors = []
            for j in range(4):
                c = table[2+4*i+j].string
                constructors.append(c)
            Constructors.append(constructors)

        df_F1_C = pd.DataFrame({
            "Rank" : [i[0] for i in Constructors],
            "Team" : [i[1] for i in Constructors],
            "Wins" : [i[2] for i in Constructors],
            "Points" : [i[3] for i in Constructors]
        })
        self.tView_F1_constructor.setModel(TableModel(df_F1_C))
               
    def PTT_show_baseball(self):
        self.df_baseball = PTT_search_all("baseball", 3)
        self.model = TableModel(self.df_baseball)
        self.tView_PTT_baseball.setModel(self.model)
        
    def PTT_show_NBA(self):
        self.df_NBA = PTT_search_all("NBA", 3)
        self.model = TableModel(self.df_NBA)
        self.tView_PTT_NBA.setModel(self.model)
    
    def PTT_show_FORMULA1(self):
        self.df_FORMULA1 = PTT_search_all("FORMULA1", 3)
        self.model = TableModel(self.df_FORMULA1)
        self.tView_PTT_FORMULA1.setModel(self.model)
        
    def rowSelected_baseball(self, mi):
        url_select = self.df_baseball.iloc[mi.row(), 4] # HREF
        if url_select == "--":
            url = "--"
        else:
            url = "https://www.ptt.cc" + url_select
        self.call_PTTsubWin(url)
        
    def rowSelected_NBA(self, mi):
        url_select = self.df_NBA.iloc[mi.row(), 4] # HREF
        if url_select == "--":
            url = "--"
        else:
            url = "https://www.ptt.cc" + url_select
        self.call_PTTsubWin(url)
    
    def rowSelected_FORMULA1(self, mi):
        url_select = self.df_FORMULA1.iloc[mi.row(), 4] # HREF
        if url_select == "--":
            url = "--"
        else:
            url = "https://www.ptt.cc" + url_select
        self.call_PTTsubWin(url)
    
    def info_1(self):
        title_1 = "中華職棒 (CPBL)"
        text_1 = """此頁提供中華職棒(CPBL)的團隊戰績與特殊球場統計,右側提供 PTT 棒球版的即時資訊,表格上點擊兩下即可查看該篇文章"""
        return info(self, title_1, text_1)
    
    def info_2(self):
        title_2 = "美國職業籃球聯賽(NBA)"
        text_2 = """此頁提供美國職業籃球聯賽(NBA)的東西區團隊戰績,右側提供 PTT NBA版的即時資訊,表格上點擊兩下即可查看該篇文章"""
        return info(self, title_2, text_2)
    
    def info_3(self):
        title_3 = "一級方程式賽車(Formula1, F1)"
        text_3 = """此頁提供一級方程式賽車(F1)的選手戰績、車隊戰績與本賽季的賽程,右側提供 PTT Formula1版的即時資訊,表格上點擊兩下即可查看該篇文章"""
        return info(self, title_3, text_3)

       
    def call_PTTsubWin(self, url):
        self.PTT_Window = PTT_Window()
        if url != "--":
            self.PTT_Window.passInfo(url)
            self.PTT_Window.show()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("錯誤")
            dlg.setText("此文章已被刪除,太慢來囉~")
            dlg.setStandardButtons(QMessageBox.StandardButton.Yes)
            buttonY = dlg.button(QMessageBox.StandardButton.Yes)
            buttonY.setText('OK')
            dlg.setIcon(QMessageBox.Icon.Information)
            button = dlg.exec()
        
    def LTN_titleSearch(self):
        board = ["baseball", "nba"]
        for j in board:
            url = "https://sports.ltn.com.tw/{}".format(j)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("div", "h3", class_="preview", limit = 3+5)
        
            for i in range(len(results)-3):   
                title = results[i+3].text.strip().replace("                        \n\n", "    ")
                setlabel = "self.title_"+str(i+1)+"_{}.setText(title)".format(j)
                exec(setlabel)
    
    def ETtoday_titleSearch(self):
        board = ["/%E6%A3%92%E7%90%83/%E4%B8%AD%E8%81%B7", "/%E7%B1%83%E7%90%83/NBA"]
        
        for j in board:
            url = "https://sports.ettoday.net/news-list{}".format(j)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("div", "h3", class_="box_0 clearfix", limit = 5)
            
            if j == "/%E6%A3%92%E7%90%83/%E4%B8%AD%E8%81%B7":
                Board = "baseball"
            else:
                Board = "nba"
                
            for i in range(len(results)):   
                title = results[i].text.strip()
                setlabel = "self.title_"+str(i+1)+"_{}_2.setText(title)".format(Board)
                exec(setlabel)
    
    def F1_Circuit(self):
        urllib3.disable_warnings() 
        url = "https://www.espn.com/f1/schedule"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        cir = soup.find_all("td", class_ = "date__col Table__TD")
        date = [i.text for i in cir]

        cir = soup.find_all("td", class_ = "race__col Table__TD")
        race = [i.text for i in cir]

        cir = soup.find_all("td", class_ = "winnerLightsOut__col Table__TD")
        Winner = [i.text for i in cir]
        
        self.df_F1_sch = pd.DataFrame({
            "DATE" : date,
            "RACE" : race,
            "WINNER/LIGHTS OUT" : Winner
        })
        self.tView_F1_sch.setModel(TableModel(self.df_F1_sch))
    
    def saveData_baseball(self):
        self.saveData("baseball")
    
    def saveData_NBA(self):
        self.saveData("NBA")  
    
    def saveData_FORMULA1(self):
        self.saveData("FORMULA1")  
        
    def saveData_NBA_W(self):
        self.saveData("NBA_W")  
        
    def saveData_NBA_E(self):
        self.saveData("NBA_E")  
        
    def saveData_baseball(self):
        self.saveData("baseball")    
    
    def saveData_F1_D(self):
        self.saveData("F1_D")  
    
    def saveData_F1_C(self):
        self.saveData("F1_C")  
    
    def saveData_F1_sch(self):
        self.saveData("F1_sch")     
    
    
    
    def saveData(self, text):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', 
            "", "EXCEL files (*.xlsx)")
        if len(fname) != 0:
            file = "self.df_{}.to_excel(fname)".format(text)
            exec(file)
    
    def appAbout(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(" 關於這個APP ")
        dlg.setText("""\
        開發者 : Chun-Yi Chen \n\n
        參考資料 : \n
        [程式]\n
        Chun-Chao Wang : Python App Design and Programming \n
        (https://ntpuccw.blog/python-in-learning/) \n
        [新聞來源]\n
        自由電子報, ETtoday, PTT(baseball, NBA, FORMULA1), ESPN \n
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
        self.close() # close app

def PTT_search_all(board, k_page):
    Nrec, Title, Author, Date, Href = [], [], [], [], []
    url = "https://www.ptt.cc/bbs/{}/index.html".format(board)
    k_page = 0
    while (k_page < 3) :
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        table_nrec = soup.find_all("div", class_ = "nrec")
        table_title = soup.select("div.r-ent div.title")
        table_author = soup.find_all("div", class_ = "author")
        table_date = soup.find_all("div", class_ = "date")
        table_href = soup.select('div.r-ent div.title a')

        nrec = [i.text for i in table_nrec]
        title = [i.text.strip() for i in table_title]
        author = [i.text for i in table_author]
        date = [i.text for i in table_date]
        href = [i.get("href") for i in table_href]
                
        
        nrec = np.reshape(nrec, int(len(nrec)))
        title = np.reshape(title, int(len(title)))
        author = np.reshape(author, int(len(author)))
        date = np.reshape(date, int(len(date)))
        href = np.reshape(href, int(len(href)))
        
        nrec[:] = nrec[::-1]
        title[:] = title[::-1]
        author[:] = author[::-1]
        date[:] = date[::-1]
        href[:] = href[::-1]
        
        Nrec.extend(nrec)
        Title.extend(title)
        Author.extend(author)
        Date.extend(date) 
        Href.extend(href)  
        
        paging_div = soup.find('div', 'btn-group btn-group-paging')
        url = "https://www.ptt.cc" + paging_div.find("a", string="‹ 上頁")["href"]
        
        k_page += 1

    PTT_dataframe = pd.DataFrame({
        "Nrec" : Nrec,
        "Title" : Title,
        "Author" : Author,
        "Time" : Date
    })
    NONE_author = PTT_dataframe.index[PTT_dataframe['Author'] == '-'].tolist() #找出沒作者 == 文章被刪除
    for m in NONE_author:
        Href.insert(m , '--')
    PTT_dataframe["Href"] = Href
    
    return PTT_dataframe

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

