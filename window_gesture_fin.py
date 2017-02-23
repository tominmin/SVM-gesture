import serial
from PyQt4 import QtGui
import time
import csv
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
        FigureCanvasQTAgg as FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar)
import os,sys
from PyQt4.uic import loadUiType
from PyQt4 import QtGui,QtCore
from PyQt4.QtCore import *

#GUI for collecting data of gesture motions
#gesture_neural.ui designed by using QtDesigner
#

Ui_MainWindow,QMainWindow=loadUiType("gesture_neural.ui")
time_out=3
samples=1

#output csv to each motion
file1="data/50-up_flick.csv"
file2="data/50-down_flick.csv"
file3="data/50-left_flick.csv"
file4="data/50-right_flick.csv"
file5="data/50-near_2.csv"
file6="data/50-far_2.csv"
file7="data/50-D-U_2.csv"
file8="data/50-R-D.csv"

class Main(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        super(Main,self).__init__(parent)
        self.setupUi(self)
        self.connect(self.pushButton_9,SIGNAL("clicked()"),self,SLOT("start()"))
        self.connect(self.pushButton,SIGNAL("clicked()"),self,SLOT("one()"))
        self.connect(self.pushButton_2,SIGNAL("clicked()"),self,SLOT("two()"))
        self.connect(self.pushButton_3,SIGNAL("clicked()"),self,SLOT("three()"))
        self.connect(self.pushButton_4,SIGNAL("clicked()"),self,SLOT("four()"))
        self.connect(self.pushButton_5,SIGNAL("clicked()"),self,SLOT("five()"))
        self.connect(self.pushButton_6,SIGNAL("clicked()"),self,SLOT("six()"))
        self.connect(self.pushButton_7,SIGNAL("clicked()"),self,SLOT("seven()"))
        self.connect(self.pushButton_8,SIGNAL("clicked()"),self,SLOT("eight()"))
        self.connect(self.pushButton_10,SIGNAL("clicked()"),self,SLOT("confirm_size()"))
        self.textEdit.append("push getsure")
        self.df=[]
        self.sensor=[]
    def addmpl(self,fig):
        self.canvas=FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
    def rmmpl(self):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()

#--------------------button-------
    @pyqtSlot()
    def start(self):
        self.listen_for_gestures()
    @pyqtSlot()
    def confirm_size(self):
        list=[]
        list.append(file1)
        list.append(file2)
        list.append(file3)
        list.append(file4)
        list.append(file5)
        list.append(file6)
        list.append(file7)
        list.append(file8)
        for i in range(len(list)):
            ans=[]
            try:
                df=pd.read_csv(list[i],header=None)
                ans.append(str(list[i]))
                ans.append(df.shape)
                self.textEdit.append(str(ans))
            except:
                print "file none.."

    def listen_for_gestures(self):
        print"start"
        ser=serial.Serial("COM5",9600,timeout=time_out)#optional COM port
        for n in range(0,samples):
            total=[]
            try:
                print "Listening for gesture"
               # self.textEdit.append("Listening for gesture for "+str(time_out)+"seconds...")
                for line in ser:
                    line=line.decode()
                    line=line.split(" ")
                    del line[-1]
                    values=list(map(int,line))
                    total=total+values
            except serial.SerialException:
                print"caught serial exception"
            self.textEdit.append("measurement end ...")
            print "end.."
            sensor1=[]
            sensor2=[]
            sensor3=[]
            sensor4=[]
            for j in range(0,len(total),4):
                sensor1.append(total[j+0])
                sensor2.append(total[j+1])
                sensor3.append(total[j+2])
                sensor4.append(total[j+3])
            time.sleep(2)
            sensor3.extend(sensor4)
            sensor2.extend(sensor3)
            sensor1.extend(sensor2)
          #  print total
            if len(sensor1)>0:
                sensor1=map(float,sensor1)
                sensor1=self.trim_data(sensor1)
            print sensor1
            #self.textEdit.append("wait......")
            time.sleep(2)
            self.sensor=sensor1
           # self.df=pd.DataFrame(sensor1)
            self.plot_four(sensor1)
            ser.close()
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
#---------------------------------------            
    @pyqtSlot()
    def one(self):
        self.textEdit.append("one")
        self.save_csv(file1)
        self.textEdit.append("saved....["+str(file1)+"]")
    @pyqtSlot()
    def two(self):
        self.textEdit.append("two")
        self.save_csv(file2)
        self.textEdit.append("saved....["+str(file2)+"]")
    @pyqtSlot()
    def three(self):
        self.textEdit.append("three")
        self.save_csv(file3)
        self.textEdit.append("saved...["+str(file3)+"]")
    @pyqtSlot()
    def four(self):
        self.textEdit.append("four")
        self.save_csv(file4)
        self.textEdit.append("saved....["+str(file4)+"]")
    @pyqtSlot()
    def five(self):
        self.textEdit.append("five")
        self.save_csv(file5)
        self.textEdit.append("saved....[5]")
    @pyqtSlot()
    def six(self):
        self.textEdit.append("six")
        self.save_csv(file6)
        self.textEdit.append("saved....[6]")
    @pyqtSlot()
    def seven(self):
        self.textEdit.append("seven")
        self.save_csv(file7)
        self.textEdit.append("saved....[7]")
    @pyqtSlot()
    def eight(self):
        self.textEdit.append("eight")
        self.save_csv(file8)
        self.textEdit.append("saved....[8]")

    def save_csv(self,file_name):
        f=open(file_name,"ab")
        csvwriter=csv.writer(f)
        csvwriter.writerow(self.sensor)
        f.close()
    def plot_four(self,sensor1):
        fig1=Figure()
        sensor1=np.array(sensor1)
        print sensor1
        sensor1=sensor1.reshape(4,32)
        print sensor1.T
        ax1=fig1.add_subplot(411)
        ax1.set_title("UP")
        ax1.plot(np.arange(32),sensor1[0,:])
        ax2=fig1.add_subplot(412)
        ax2.set_title("DOWN")
        ax2.plot(np.arange(32),sensor1[1,:])
        ax3=fig1.add_subplot(413)
        ax3.set_title("LEFT")
        ax3.plot(np.arange(32),sensor1[2,:])        
        ax4=fig1.add_subplot(414)
        ax4.set_title("RIGHT")
        ax4.plot(np.arange(32),sensor1[3,:])
        self.rmmpl()
        self.addmpl(fig1)

if __name__=="__main__":
    fig1=Figure()
    ax1=fig1.add_subplot(411)
    ax1.plot(np.random.rand(5))
    ax2=fig1.add_subplot(412)
    ax2.plot(np.random.rand(10))
    ax3=fig1.add_subplot(413)
    ax3.plot(np.random.rand(5))
    ax4=fig1.add_subplot(414)
    ax4.plot(np.random.rand(5))

    app=QtGui.QApplication(sys.argv)
    main=Main()
    main.addmpl(fig1)
    main.show()
    sys.exit(app.exec_())

