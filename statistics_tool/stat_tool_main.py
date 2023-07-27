from os import scandir
from turtle import width
from PyQt6 import QtWidgets, uic, QtCore, QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QPixmap
import pyqtgraph as pg
from scipy.stats import norm, beta, f, gamma
from scipy import misc
import numpy as np
import sys
from sklearn.preprocessing import scale
from sympy import symbols, diff, Function
from sympy.plotting import plot
import pandas as pd
from pathlib import Path
import sympy as sym


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
         
        if role == Qt.ItemDataRole.BackgroundRole and (index.row()%2 == 0):
            return QtGui.QColor('#a2c7ff')
        
        if role == Qt.ItemDataRole.BackgroundRole and (index.row()%2 == 1):
            return QtGui.QColor('#ffcf7d')
        
 
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
        
        # self.picName = ["Normal.png", "Beta.png", "f.png"]
 
        #Load the UI Page by PyQt6
        uic.loadUi("stat_tool.ui", self)
        self.setWindowTitle('APP')
        
        # Signales 
        ## Tab1_distribution
        self.gView.scene().sigMouseMoved.connect(self.mouseMoved)
        self.comboBox_dist.currentIndexChanged.connect(self.ParmChange)
        self.comboBox_dist.currentIndexChanged.connect(self.update_plot)
        self.comboBox_type.currentIndexChanged.connect(self.ParmChange)
        self.comboBox_type.currentIndexChanged.connect(self.update_plot)
        # self.groupBox.toggled.connect(self.pdfcdf_clicked) # suitable for checkbox, not radiobutton
        self.vSlider_para1.valueChanged.connect(self.sliderMovePara1)
        self.vSlider_para1.valueChanged.connect(self.update_plot)
        self.vSlider_para1.sliderMoved.connect(self.sliderMovePara1)
        self.vSlider_para1.sliderMoved.connect(self.update_plot)
        self.vSlider_para1.sliderMoved.connect(self.sliderRange)
        self.vSlider_para2.valueChanged.connect(self.sliderMovePara2)
        self.vSlider_para2.valueChanged.connect(self.update_plot)
        self.vSlider_para2.sliderMoved.connect(self.sliderMovePara2)
        self.vSlider_para2.sliderMoved.connect(self.update_plot)
        self.vSlider_para2.sliderMoved.connect(self.sliderRange)
        self.update_plot()
        #self.pBut_go.clicked.connect(self.go)
        
        # ## Tab2_derivative
        self.der = self.gView_Der
        self.lineEdit_fx.textChanged.connect(self.update_Der_plot)
        self.lineEdit_R_Max.textChanged.connect(self.update_Der_plot)
        self.lineEdit_R_min.textChanged.connect(self.update_Der_plot)     
        self.radioBut3.toggled.connect(self.der_clicked)
        self.radioBut4.toggled.connect(self.der_clicked)
        self.radioBut5.toggled.connect(self.der_clicked)
        self.radioBut_other.toggled.connect(self.der_clicked)
        self.update_Der_plot('3')
        # self.der.scene().sigMouseMoved.connect(self.mouseMoved_der)
        
        ## Tab3_load
        self.table = self.tableView
        win = self.graphLayoutWidget
         
        self.plt1 = win.addPlot(title="")
        # win.nextRow()
        # self.plt2 = win.addPlot(title="")
        self.actionEXIT.triggered.connect(self.fileExit)
        self.actionOpen_file.triggered.connect(self.fileOpen)
        self.comboBox_col.currentIndexChanged.connect(self.update_plt1)
        
        ## Exit
        self.pushBtn_exit.clicked.connect(self.dialogBox)
        
    # Slots:    
    #### Slots:Tab1_distribution 
    def ParmChange(self):
        if self.comboBox_dist.currentText() == 'Normal':
            self.label_para1.setText('&mu')
            self.label_para2.setText('&sigma')
            self.lineEdit_para1_U.setText('5')
            self.lineEdit_para1.setText('0')
            self.lineEdit_para1_L.setText('-5')
            self.lineEdit_para2_U.setText('5')
            self.lineEdit_para2.setText('1')
            self.lineEdit_para2_L.setText('1')
        elif self.comboBox_dist.currentText() == 'Beta':
            self.label_para1.setText('&alpha')
            self.label_para2.setText('&beta')
            self.lineEdit_para1_U.setText('5')
            self.lineEdit_para1.setText('2')
            self.lineEdit_para1_L.setText('0')
            self.lineEdit_para2_U.setText('5')
            self.lineEdit_para2.setText('2')
            self.lineEdit_para2_L.setText('0')
        elif self.comboBox_dist.currentText() == 'f':
            self.label_para1.setText('df1')
            self.label_para2.setText('df2')
            self.lineEdit_para1_U.setText('10')
            self.lineEdit_para1.setText('5')
            self.lineEdit_para1_L.setText('1')
            self.lineEdit_para2_U.setText('10')
            self.lineEdit_para2.setText('2')
            self.lineEdit_para2_L.setText('1')
        else:
            self.label_para1.setText('&alpha')
            self.label_para2.setText('&beta')
            self.lineEdit_para1_U.setText('10')
            self.lineEdit_para1.setText('2')
            self.lineEdit_para1_L.setText('0')
            self.lineEdit_para2_U.setText('10')
            self.lineEdit_para2.setText('2')
            self.lineEdit_para2_L.setText('0')
    
    def update_plot(self):
        self.gView.clear()
        x = np.linspace(-8, 8, 1000)
        if self.comboBox_dist.currentText() == 'Normal':
            cur_loc = float(self.lineEdit_para1.text())
            cur_scale = float(self.lineEdit_para2.text())
            x = np.linspace(cur_loc - cur_scale*3.1, cur_loc + cur_scale*3.1, 200)
            if  self.comboBox_type.currentText() == 'PDF':
                y = norm.pdf(x, loc = cur_loc, scale = cur_scale) 
                pen = pg.mkPen(color=(255, 255, 255), width = 5) # Qt.DotLine, Qt.DashDotLine and Qt.DashDotDotLine
                cur1 = self.gView.plot(x, y, pen = pen, name = 'Demo')
                cur2 = self.gView.plot(x, np.zeros(len(y)))
                # add color patch under curve
                patchcur = pg.FillBetweenItem(curve1 = cur1, curve2 = cur2, brush = 'g')
            else:
                y = norm.cdf(x, loc = cur_loc, scale = cur_scale)
                
        elif self.comboBox_dist.currentText() == 'Beta':
            a = float(self.lineEdit_para1.text())
            b = float(self.lineEdit_para2.text())
            x = np.linspace(-0.2, 1.2, 200)
            if  self.comboBox_type.currentText() == 'PDF':
                y = beta.pdf(x, a, b) 
                pen = pg.mkPen(color=(255, 255, 255), width = 5) # Qt.DotLine, Qt.DashDotLine and Qt.DashDotDotLine
                cur1 = self.gView.plot(x, y, pen = pen, name = 'Demo')
                cur2 = self.gView.plot(x, np.zeros(len(y)))
                # add color patch under curve
                patchcur = pg.FillBetweenItem(curve1 = cur1, curve2 = cur2, brush = 'g')
                # self.gView.addItem(patchcur)
            else:
                y = beta.cdf(x, a, b)
        
        elif self.comboBox_dist.currentText() == 'f':
            df1 = float(self.lineEdit_para1.text())
            df2 = float(self.lineEdit_para2.text())
            x = np.linspace(-0.2, 5.2, 200)
            if  self.comboBox_type.currentText() == 'PDF':
                y = f.pdf(x, df1, df2) 
                pen = pg.mkPen(color=(255, 255, 255), width = 5) # Qt.DotLine, Qt.DashDotLine and Qt.DashDotDotLine
                cur1 = self.gView.plot(x, y, pen = pen, name = 'Demo')
                cur2 = self.gView.plot(x, np.zeros(len(y)))
                # add color patch under curve
                patchcur = pg.FillBetweenItem(curve1 = cur1, curve2 = cur2, brush = 'g')
                # self.gView.addItem(patchcur)
            else:
                y = f.cdf(x, df1, df2)
        
        else:
            a = float(self.lineEdit_para1.text())
            b = float(self.lineEdit_para2.text())
            x = np.linspace(-0.2, 40, 400)
            if  self.comboBox_type.currentText() == 'PDF':
                y = gamma.pdf(x, a, b) 
                pen = pg.mkPen(color=(255, 255, 255), width = 5) # Qt.DotLine, Qt.DashDotLine and Qt.DashDotDotLine
                cur1 = self.gView.plot(x, y, pen = pen, name = 'Demo')
                cur2 = self.gView.plot(x, np.zeros(len(y)))
                # add color patch under curve
                patchcur = pg.FillBetweenItem(curve1 = cur1, curve2 = cur2, brush = 'g')
                # self.gView.addItem(patchcur)
            else:
                y = gamma.cdf(x, a, b)
         
        self.gView.plot(x,y) # generates a PlotDataItem
        # self.gView.setXRange(-5, 5, padding = 0)
        # self.gView.setYRange(0, 1, padding = 0)
        self.gView.vLine = pg.InfiniteLine(pos = 1, angle = 90, movable = False)
        self.gView.hLine = pg.InfiniteLine(pos = 0.2, angle = 0, movable = False)
        self.gView.addItem(self.gView.vLine) # add PlotDataItem in PlotWidget 
        self.gView.addItem(self.gView.hLine)
        # self.gView.setTitle(title)
        
    def mouseMoved(self, point): # returns the coordinates in pixels with respect to the PlotWidget
        p = self.gView.plotItem.vb.mapSceneToView(point) # convert to the coordinate of the plot
        if self.comboBox_dist.currentText() == 'Normal':
            cur_loc = float(self.lineEdit_para1.text())
            cur_scale = float(self.lineEdit_para2.text())
            self.lineEdit_x.setText(str(round(p.x(), 4))) 
            self.lineEdit_prop.setText(str(round(norm.cdf(p.x(), loc = cur_loc, scale = cur_scale), 4))) 
            if  self.comboBox_type.currentText() == 'PDF':
                self.gView.vLine.setPos(p.x()) # set position of the verticle line
                self.gView.hLine.setPos(norm.pdf(p.x(), loc = cur_loc, scale = cur_scale)) # set position of the horizontal line
            else:
                self.gView.vLine.setPos(p.x()) # set position of the verticle line
                self.gView.hLine.setPos(norm.cdf(p.x(), loc = cur_loc, scale = cur_scale))
            
        elif self.comboBox_dist.currentText() == 'Beta':
            a = float(self.lineEdit_para1.text())
            b = float(self.lineEdit_para2.text())
            self.lineEdit_x.setText(str(round(p.x(), 4))) 
            self.lineEdit_prop.setText(str(round(beta.cdf(p.x(), a, b), 4)))
            if  self.comboBox_type.currentText() == 'PDF':
                self.gView.vLine.setPos(p.x()) # set position of the verticle line
                self.gView.hLine.setPos(beta.pdf(p.x(), a, b)) # set position of the horizontal line
            else:
                self.gView.vLine.setPos(p.x()) # set position of the verticle line
                self.gView.hLine.setPos(beta.cdf(p.x(), a, b))
             
        
        elif self.comboBox_dist.currentText() == 'f':
            df1 = float(self.lineEdit_para1.text())
            df2 = float(self.lineEdit_para2.text())
            self.lineEdit_x.setText(str(round(p.x(), 4))) 
            self.lineEdit_prop.setText(str(round(f.cdf(p.x(), df1, df2), 4))) 
            if  self.comboBox_type.currentText() == 'PDF':
                self.gView.vLine.setPos(p.x()) # set position of the verticle line
                self.gView.hLine.setPos(f.pdf(p.x(), df1, df2)) # set position of the horizontal line
            else:
                self.gView.vLine.setPos(p.x()) # set position of the verticle line
                self.gView.hLine.setPos(f.cdf(p.x(), df1, df2))
        
        else:
            a = float(self.lineEdit_para1.text())
            b = float(self.lineEdit_para2.text())
            self.lineEdit_x.setText(str(round(p.x(), 4))) 
            self.lineEdit_prop.setText(str(round(gamma.cdf(p.x(), a, b), 4)))
            if  self.comboBox_type.currentText() == 'PDF':
                self.gView.vLine.setPos(p.x()) # set position of the verticle line
                self.gView.hLine.setPos(gamma.pdf(p.x(), a, b)) # set position of the horizontal line
            else:
                self.gView.vLine.setPos(p.x()) # set position of the verticle line
                self.gView.hLine.setPos(gamma.cdf(p.x(), a, b))
        
       
    def sliderMovePara1(self, x):
        self.lineEdit_para1.setText(str(round(x,4)))
    
    def sliderMovePara2(self, x):
        self.lineEdit_para2.setText(str(round(x,4)))
        
    def sliderRange(self):
        if self.comboBox_dist.currentText() == 'Normal':
            self.vSlider_para1.setMaximum(5)
            self.vSlider_para1.setMinimum(-5)
            self.vSlider_para2.setMaximum(5)
            self.vSlider_para2.setMinimum(0)
        elif self.comboBox_dist.currentText() == 'Beta':
            self.vSlider_para1.setMaximum(5)
            self.vSlider_para1.setMinimum(0)
            self.vSlider_para2.setMaximum(5)
            self.vSlider_para2.setMinimum(0)
        elif self.comboBox_dist.currentText() == 'f':
            self.vSlider_para1.setMaximum(10)
            self.vSlider_para1.setMinimum(1)
            self.vSlider_para2.setMaximum(10)
            self.vSlider_para2.setMinimum(1)
        else:
            self.vSlider_para1.setMaximum(10)
            self.vSlider_para1.setMinimum(1)
            self.vSlider_para2.setMaximum(10)
            self.vSlider_para2.setMinimum(1)

     
    
    #### Slots:Tab2_derivative
    def update_Der_plot(self, cho):
        self.der.clear()
        x = symbols('x', communtative = True)
        f = eval(self.lineEdit_fx.text())
        f1 = diff(f, x)
        f2 = diff(f, x, 2)
        self.lineEdit_fxx.setText(str(f1))
        self.lineEdit_fxxx.setText(str(f2))
        
        xs_min, xs_Max = int(self.lineEdit_R_min.text()), int(self.lineEdit_R_Max.text())
        xs = np.linspace(xs_min, xs_Max, 1000)
           
        if cho == 'Other':
            f_s = diff(f, x, self.lineEdit_other.text())
            self.lineEdit_f_spe.setText(str(f_s)) 
            
            y_s = [eval(self.lineEdit_f_spe.text()) for x in xs]
        else:
            f_s = diff(f, x, cho)
            self.lineEdit_f_spe.setText(str(f_s))
            
            y_s = [eval(self.lineEdit_f_spe.text()) for x in xs]
        
    
        y = [eval(self.lineEdit_fx.text()) for x in xs]
        y1 = [eval(self.lineEdit_fxx.text()) for x in xs]
        y2 = [eval(self.lineEdit_fxxx.text()) for x in xs]    

        # some regular settings
        self.der.showGrid(x = True, y = True)
        self.der.addLegend()
        self.der.setLabel('left', 'y')
        self.der.setLabel('bottom', 'x')
        self.der.setXRange(-6, 6)
        # plt.setYRange(-2.5, 2.5)
        # plt.setWindowTitle(title)
        self.der.plot(xs, y, pen = 'g', width = 2, name = 'f(x)')
        self.der.plot(xs, y1, pen = 'r', width = 2, name = 'f \'(x)')
        self.der.plot(xs, y2, pen = 'y', width = 2, name = 'f \'\'(x)')
        self.der.plot(xs, y_s, pen = 'b', width = 2, name = 'Other')
        
    def der_clicked(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            self.update_Der_plot(radioBtn.text())
            # print(radioBtn.text())
        
       
        
    #### Slots:load
    def fileExit(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("CHUN first APP")
        dlg.setText("找到這裡來! 確定要離開這個 App")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        buttonY = dlg.button(QMessageBox.StandardButton.Yes)
        buttonY.setText('說走就走')
        buttonY = dlg.button(QMessageBox.StandardButton.No)
        buttonY.setText('繼續逛')
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()
 
        if button == QMessageBox.StandardButton.Yes:
            dlg.setText("真的要離開嗎? 再看一下啦")
            dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            buttonY = dlg.button(QMessageBox.StandardButton.Yes)
            buttonY.setText('我看不下去了!!!')
            buttonY = dlg.button(QMessageBox.StandardButton.No)
            buttonY.setText('當然要留下來!!!')
            dlg.setIcon(QMessageBox.Icon.Question)
            button = dlg.exec()
            if button == QMessageBox.StandardButton.Yes:
                self.close()
            else:
                print("No!")    
        else:
            print("No!")             
 
    def fileOpen(self):
        home_dir = str(Path.home())
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 
            "", "EXCEL files (*.xlsx *.xls);;Text files (*.txt);;Images (*.png *.xpm *.jpg)")
        # print(fname[0])
        if fname[0]:
            self.df = pd.read_excel(fname[0], index_col = None, header = 0)
            self.model = TableModel(self.df)
            self.table.setModel(self.model)
 
            self.label_variable.setText(str(self.df.shape[1]))
            self.label_size.setText(str(self.df.shape[0]))
            self.comboBox_col.clear()
            self.comboBox_col.addItems(self.df.columns)
 
            self.update_plt1()
            # self.update_plt2()
             
    def update_plt1(self):
        cur_combo = self.comboBox_col.currentText()
        self.plt1.clear()
        dat = self.df['{}'.format(cur_combo)]
        y, x = np.histogram(self.df[['{}'.format(cur_combo)]])
        self.plt1.plot(x, y, stepMode="center", fillLevel=0, fillOutline=True, brush=(0,0,255,150))
        self.plt1.setTitle(cur_combo)
        self.label_mean.setText(str(round(dat.mean(), 4)))
        self.label_std.setText(str(round(dat.std(), 4)))
        self.label_range.setText(str(round(dat.max() - dat.min(), 4)))
 
    # def update_plt2(self):
    #     self.plt2.clear()
    #     if isinstance(self.df[self.df.columns[0]][0], str) or isinstance(self.df[self.df.columns[1]][0], str) :
    #         self.plt2.setLabel('bottom',"")   
    #         self.plt2.setLabel('left',"")
    #         return
    #     else :
    #     # if self.df[self.df.columns[0]][0]== float and self.df[self.df.columns[1]][0]== float :
    #         self.plt2.plot(self.df[self.df.columns[0]], self.df[self.df.columns[1]], pen=None, symbol='o', symbolSize=5)
    #         self.plt2.setLabel('bottom',self.df.columns[0])   
    #         self.plt2.setLabel('left',self.df.columns[1])  
    
    #### Slots:Exit
    def dialogBox(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("CHUN first APP")
        dlg.setText("確定要離開這個 App")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        buttonY = dlg.button(QMessageBox.StandardButton.Yes)
        buttonY.setText('確定')
        buttonY = dlg.button(QMessageBox.StandardButton.No)
        buttonY.setText('取消')
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()
 
        if button == QMessageBox.StandardButton.Yes:
            dlg.setText("真的要離開嗎? 再看一下啦")
            dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            buttonY = dlg.button(QMessageBox.StandardButton.Yes)
            buttonY.setText('我看不下去了!!!')
            buttonY = dlg.button(QMessageBox.StandardButton.No)
            buttonY.setText('當然要留下來!!!')
            dlg.setIcon(QMessageBox.Icon.Question)
            button = dlg.exec()
            if button == QMessageBox.StandardButton.Yes:
                self.close()
            else:
                print("No!")    
        else:
            print("No!")               
 
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
 
if __name__ == '__main__':
    main()