import sys,os,time
from PyQt4 import QtCore,QtGui
import serial,math,csv
import numpy as np
import warnings
import random as r
from sklearn import preprocessing,svm,cross_validation
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import grid_search,metrics
import pandas as pd

def motion_check(y):
    data=[]
    for i in range(len(y)):
        if y[i]=="down":
            data.append(3)
        elif y[i]=="up":
            data.append(4)
        elif y[i]=="left":
            data.append(2)
        elif y[i]=="right":
            data.append(1)
        elif y[i]=="near":
            data.append(5)
        elif y[i]=="far":
            data.append(6)        
        elif y[i]=="left_flick":
            data.append(7)
        elif y[i]=="right_flick":
            data.append(8)
        elif y[i]=="up_flick":
            data.append(9)
        elif y[i]=="down_flick":
            data.append(10)
        elif y[i]=="shake":
            data.append(11)
        elif y[i]=="L-D":
            data.append(12)
        elif y[i]=="R-D":
            data.append(13)
        elif y[i]=="D-U":
            data.append(14)
    return data
X=np.loadtxt("data/motion14.csv",delimiter=",")
y=pd.read_csv("data/motion14_ans.csv",header=None)
y=y.as_matrix()
y=motion_check(y)
samples_per_label=50
loops=10
baud_rate=9600
port="COM5" #selecting optional COM Port
data=[]
def gesture_check(y):
    if y==3:
        return "down"
    elif y==4:
        return "up"
    elif y==2:
        return "left"
    elif y==1:
        return "right"
    elif y==5:
        return "near"
    elif y==6:
        return "far"
    elif y==7:
        return "left_flick"
    elif y==8:
        return "right_flick"
    elif y==9:
        return "up_flick"
    elif y==10:
        return "down_flick"
    elif y==11:
        return "shake"
    elif y==12:
        return "L-D"
    elif y==13:
        return "R-D"
    elif y==14:
        return "D-U"

class Walker(QtCore.QThread):
    sig_status=QtCore.pyqtSignal(long)
    def __init__(self,parent=None):
        super(Walker,self).__init__(parent)
        self.path=""
        self.stopped=False
        self.mutex=QtCore.QMutex()
        self.classifier="svm"
    def setup(self):
        self.path=path
        self.stopped=False
    def stop(self):
        #with QtCore.QMutexLocker(self.mutex):
        self.stopped=True
        self.ser.close()
    def restart(self):
        #with QtCore.QMutexLocker(self.mutex):
        self.stopped=False
    def run(self):
        self.num=0
        while True:
            self.ser=serial.Serial(port,baud_rate,timeout=3)
            while True:
                total=[]
                while self.stopped:
                    self.msleep(100)
                try:
                    for line in self.ser:
                        line=line.decode()
                        line=line.split(' ')
                        del line[-1]
                        values=list(map(int,line))
                        total=total+values
                except serial.SerialException as e:
                    print("caught SerialException")
                sensor1=[]
                sensor2=[]
                sensor3=[]
                sensor4=[]
                for j in range(0,len(total),4):
                    sensor1.append(total[j+0])
                    sensor2.append(total[j+1])
                    sensor3.append(total[j+2])
                    sensor4.append(total[j+3])
                sensor3.extend(sensor4)
                sensor2.extend(sensor3)
                sensor1.extend(sensor2)
                if  len(sensor1)>0:
                    print"catch"
                    sensor1=map(float,sensor1)
                    self.sensor1=self.trim_data(sensor1)
                    self.predict=self.online_classify(self.sensor1)
                    self.ser.write(self.predict)     
                    self.sig_status.emit(self.predict)
            #self.ser.close()

        self.stop()
        self.finished.emit()
    def trim_data(self,d,n=128,m=255):
        l=len(d)
        histogram=[0]*n
        s=int(l/n)
        if s==0:
            s=int(1./(float(l)/float(n)))
            for i,x in enumerate(d):
                histogram[i*s]=x/m
        else:
            for i in range(0,n):
                histogram[i]=sum(d[i*s:(i+1)*s])/(m*s)
        return histogram
    def online_classify(self,d):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if self.classifier=="svm":
                prediction=self.svc.predict(d)
                print "svm"
            elif self.classifier=="log":
                prediction=self.log.predict(d)
                print "log"
            elif self.classifier=="rf":
                prediction=self.rf.predict(d)
                print "randomforest"
        print(gesture_check(prediction))
        data.append(self.sensor1)
        return prediction
    def train_classifier(self):
        X_train,X_test,y_train,y_test=cross_validation.train_test_split(X,y,test_size=0.25)
        parameters={"C":np.logspace(1,2,base=10),
                "gamma":np.logspace(-2,-1,base=10)}
        print "Grid_search start"
        grsrch=grid_search.GridSearchCV(svm.SVC(),parameters,n_jobs=-1,scoring="accuracy",verbose=100)
        grsrch.fit(X_train,y_train)
        print grsrch.best_estimator_
        self.svc=grsrch.best_estimator_
        self.svc.fit(X_train,y_train)
        self.log=LogisticRegression().fit(X_train,y_train)
        self.rf=RandomForestClassifier().fit(X_train,y_train)
        print "score\n"
        self.log_score=self.log.score(X_test,y_test)
        self.svc_score=self.svc.score(X_test,y_test)
        self.rf_score=self.rf.score(X_test,y_test)


class Dialog(QtGui.QDialog):
    def __init__(self,parent=None):
        super(Dialog,self).__init__(parent)
        self.directory=QtGui.QTextEdit("default classifier\n svm \n")
        self.label=QtGui.QLabel("num:0")
        self.search_button=QtGui.QPushButton("&search")
        self.search_button.clicked.connect(self.search_files)
        self.stop_button=QtGui.QPushButton("&stop")
        self.stop_button.clicked.connect(self.stop_search)
        self.default_num=0.5
        self.xx=[]

        self.svm_button=QtGui.QPushButton("&svm")
        self.svm_button.clicked.connect(self.change_svm)
        self.log_button=QtGui.QPushButton("&logistic")
        self.log_button.clicked.connect(self.change_log)
        self.rf_button=QtGui.QPushButton("&randomforest")
        self.rf_button.clicked.connect(self.change_rf)

        self.uhr=QtGui.QLCDNumber()
        self.uhr.display(self.default_num)
        self.uhr2=QtGui.QLCDNumber()
        self.uhr2.display(self.default_num)
        self.uhr3=QtGui.QLCDNumber()
        self.uhr3.display(self.default_num)
        palette=self.uhr.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(85,85,255))
        palette.setColor(palette.Background,QtGui.QColor(0,170,255))
        palette.setColor(palette.Light,QtGui.QColor(255,0,0))
        palette.setColor(palette.Dark,QtGui.QColor(0,255,0))
        self.uhr.setPalette(palette)
        
        palette=self.uhr2.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(255,255,255))
        palette.setColor(palette.Background,QtGui.QColor(255,255,255))
        palette.setColor(palette.Light,QtGui.QColor(255,255,255))
        palette.setColor(palette.Dark,QtGui.QColor(255,255,255))
        self.uhr2.setPalette(palette)
        palette=self.uhr3.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(255,255,255))
        palette.setColor(palette.Background,QtGui.QColor(255,255,255))
        palette.setColor(palette.Light,QtGui.QColor(255,255,255))
        palette.setColor(palette.Dark,QtGui.QColor(255,255,255))
        self.uhr3.setPalette(palette)
        self.checker=False
        #-----------------
        vbox=QtGui.QVBoxLayout()
        vbox.addWidget(self.search_button)
        vbox.addWidget(self.stop_button)
        hbox=QtGui.QHBoxLayout()
        hbox.addWidget(self.directory)
        hbox.addLayout(vbox)
        hbox.addWidget(self.label)
        #----------------------
        vbox_lcd_1=QtGui.QVBoxLayout()
        vbox_lcd_1.addWidget(self.svm_button)
        vbox_lcd_1.addWidget(self.uhr)

        vbox_lcd_2=QtGui.QVBoxLayout()
        vbox_lcd_2.addWidget(self.log_button)
        vbox_lcd_2.addWidget(self.uhr2)

        vbox_lcd_3=QtGui.QVBoxLayout()
        vbox_lcd_3.addWidget(self.rf_button)
        vbox_lcd_3.addWidget(self.uhr3)
        hbox2=QtGui.QHBoxLayout()
        hbox2.addLayout(vbox_lcd_1)
        hbox2.addLayout(vbox_lcd_2)
        hbox2.addLayout(vbox_lcd_3)
        #------------------------
        vbox_total=QtGui.QVBoxLayout()
        vbox_total.addLayout(hbox)
        vbox_total.addLayout(hbox2)
        self.vbox_plt_1=QtGui.QVBoxLayout()
        vbox_total.addLayout(self.vbox_plt_1)
        
        self.setLayout(vbox_total)
        self.setWindowTitle("signal and slot")
        self.resize(350,100)
        self.path=None
        self.walker=Walker()
        self.walker.sig_status.connect(self.update_status)
        self.walker.finished.connect(self.finish_search)
    @QtCore.pyqtSlot()
    def search_files(self):
        self.search_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        #----------------
        if self.walker.isRunning:
            self.walker.terminate()
            self.walker.wait()
        if self.checker==True:
            self.search_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.walker.restart()
            self.checker=False
        else:
            self.walker.train_classifier()
            self.uhr.display(self.walker.svc_score)
            self.uhr2.display(self.walker.log_score)
            self.uhr3.display(self.walker.rf_score) 
        self.walker.start()
    @QtCore.pyqtSlot()
    def stop_search(self):
        self.walker.stop()
        self.search_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.checker=True

    @QtCore.pyqtSlot(long)
    def update_status(self,status):
        if status==0:
            status="loss"
        elif status==3:
            status="down"
        elif status==4:
            status="up"
        elif status==2:
            status="left"
        elif status==1:
            status="right"
        elif status==5:
            status="near"
        elif status==6:
            status="far"
        elif status==7:
            status="left_flick"
        elif status==8:
            status="right_flick"
        elif status==9:
            status="up_flick"
        elif status==10:
            status="down_flick"
        elif status==11:
            status="shake"
        elif status==12:
            status="L-D"
        elif status==13:
            status="R-D"
        elif status==14:
            status="D-U"
        self.xx.append(status)
        if len(self.xx)>4:
            self.xx=[]
            self.directory.clear()
        self.directory.append(status)
    @QtCore.pyqtSlot()
    def finish_search(self):
        self.search_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    @QtCore.pyqtSlot()
    def change_svm(self):
        self.walker.classifier="svm"    
        self.directory.append("svm")
        palette=self.uhr.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(85,85,255))
        palette.setColor(palette.Background,QtGui.QColor(0,170,255))
        palette.setColor(palette.Light,QtGui.QColor(255,0,0))
        palette.setColor(palette.Dark,QtGui.QColor(0,255,0))
        self.uhr.setPalette(palette)
        palette=self.uhr2.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(255,255,255))
        palette.setColor(palette.Background,QtGui.QColor(255,255,255))
        palette.setColor(palette.Light,QtGui.QColor(255,255,255))
        palette.setColor(palette.Dark,QtGui.QColor(255,255,255))
        self.uhr2.setPalette(palette)
        palette=self.uhr3.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(255,255,255))
        palette.setColor(palette.Background,QtGui.QColor(255,255,255))
        palette.setColor(palette.Light,QtGui.QColor(255,255,255))
        palette.setColor(palette.Dark,QtGui.QColor(255,255,255))
        self.uhr3.setPalette(palette)
    @QtCore.pyqtSlot()
    def change_log(self):
        self.walker.classifier="log"
        self.directory.append("log")
        palette=self.uhr2.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(85,85,255))
        palette.setColor(palette.Background,QtGui.QColor(0,170,255))
        palette.setColor(palette.Light,QtGui.QColor(255,0,0))
        palette.setColor(palette.Dark,QtGui.QColor(0,255,0))
        self.uhr2.setPalette(palette)
        palette=self.uhr.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(255,255,255))
        palette.setColor(palette.Background,QtGui.QColor(255,255,255))
        palette.setColor(palette.Light,QtGui.QColor(255,255,255))
        palette.setColor(palette.Dark,QtGui.QColor(255,255,255))
        self.uhr.setPalette(palette)
        palette=self.uhr3.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(255,255,255))
        palette.setColor(palette.Background,QtGui.QColor(255,255,255))
        palette.setColor(palette.Light,QtGui.QColor(255,255,255))
        palette.setColor(palette.Dark,QtGui.QColor(255,255,255))
        self.uhr3.setPalette(palette)
    @QtCore.pyqtSlot()
    def change_rf(self):
        self.walker.classifier="rf"
        self.directory.append("randomforest")
        palette=self.uhr3.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(85,85,255))
        palette.setColor(palette.Background,QtGui.QColor(0,170,255))
        palette.setColor(palette.Light,QtGui.QColor(255,0,0))
        palette.setColor(palette.Dark,QtGui.QColor(0,255,0))
        self.uhr3.setPalette(palette)
        palette=self.uhr.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(255,255,255))
        palette.setColor(palette.Background,QtGui.QColor(255,255,255))
        palette.setColor(palette.Light,QtGui.QColor(255,255,255))
        palette.setColor(palette.Dark,QtGui.QColor(255,255,255))
        self.uhr.setPalette(palette)
        palette=self.uhr2.palette()
        palette.setColor(palette.WindowText,QtGui.QColor(255,255,255))
        palette.setColor(palette.Background,QtGui.QColor(255,255,255))
        palette.setColor(palette.Light,QtGui.QColor(255,255,255))
        palette.setColor(palette.Dark,QtGui.QColor(255,255,255))
        self.uhr2.setPalette(palette)
def main():
    app=QtGui.QApplication(sys.argv)
    dialog=Dialog()
    dialog.show()
    sys.exit(app.exec_())
if __name__=="__main__":
    main()

