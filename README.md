# Three small APPs using PyQT6
There are three types of apps, which include a small statistics tool, a query database using SQLite, and crawling data from PTT (a famous web forum in Taiwan) and sports news websites. Moreover, These functions and programs are presented in the PyQT6 interface. The functions of each are introduced below.

## [Statistics tool](/statistics_tool/)
This application includes three functionality as follow:

* _Distribution_ <br>
  Collecting four different distributions, are Normal, Beta, F, and Gamma. Also, provide the plot of the cdf and pdf. Moreover, The user can observe the change in the distribution by adjusting the parameters.

* _Derivative_ <br>
    A simple application to exhibit the target function's derivative.      

* _File_ <br>
    Exhibit the Excel file (.xlsx, .csv ... etc.) to the table in the application.


## [Query database](/sqlite_query/)
Connect Python and SQLite to query the paper database ([NIPS 2015 Papers](https://www.kaggle.com/datasets/benhamner/nips-2015-papers) ; [download](https://ntpuccw.blog/qt-designer-pyqt-sqlite-%e8%b3%87%e6%96%99%e5%ba%ab%e7%9a%84%e6%8a%80%e8%a1%93%e8%88%87%e6%87%89%e7%94%a8/)). This application include the three types of query database the and provides sub-windows to view the details.

## [Webcraeler](/webcrawler/)
This application is exhibit the standings, sport news, and web forum articles. Types of sports included are as follows:

* CPBL
  * Standings
  * News from [LTN](https://sports.ltn.com.tw/cpbl) and [ETtoday](https://sports.ettoday.net/news-list/%E6%A3%92%E7%90%83/%E4%B8%AD%E8%81%B7/)
  * [Baseball](https://www.ptt.cc/bbs/Baseball/index.html) board in PTT
* NBA
  * Standings
  * News from [LTN](https://sports.ltn.com.tw/cpbl) and [ETtoday](https://sports.ettoday.net/news-list/%E7%B1%83%E7%90%83/NBA/)
  * [NBA](https://www.ptt.cc/bbs/NBA/index.html) board in PTT
* F1
  * Standings
  * Race schedule
  * [Formula1](https://www.ptt.cc/bbs/FORMULA1/index.html) board in PTT

# Reference
* [Python App Design and Programming (QT + Designer + PyQt6 + PyQtGraph + SQLite 3) - Chun-Chao Wang](https://ntpuccw.blog/python-in-learning/)
