# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 15:31:43 2018

@author: Sanjiv
"""

import sys
import random
import matplotlib

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget
from numpy import arange, sin, pi, random
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
matplotlib.use("Qt5Agg")

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    
    def __init__(self, parent=None, width=10, height=4, dpi=100):
        
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
       
        
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    
class FirstOrderDeadTime(MyMplCanvas):
    
    t=[]
    y=[]
    x=[]
    counter = 0
    step=0.05
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_model)
        timer.start(1000)
        self.x_init = 1.5
    
    def update_model(self):
        _t = self.t
        _x = self.x
        _y = self.y
        _dt = self.step
        
        
        
        # Increment the counter for each timestep
        self.counter+=_dt
        _t.append(self.counter)
        
        # Update x
        if self.counter <= _dt:
            _x.append(self.x_init)
        else:
            _x.append(_x[-1])
            
        _y.append(0.2)
            
        print(_x)
        self.axes.plot(_t, _x, 'b',_t, _y,'r')
        self.axes.set_xlabel('time')
        self.axes.set_title('Model response vs time')
        self.axes.legend(['PV', 'SP'])
        self.draw()
        
        

class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""
    t=[]
    sp=[]
    pv=[]
    cnt=[]
    counter = 0
    min_sp_counter = 50
    max_sp_counter = 200
    step = 0.05
    amp = 50
    def __init__(self, *args, **kwargs):
        
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)
        self.pv_init = 200.0
        
    def calcPV(self, t, pv, sp):
        i = len(t)-2
        error = sp[i]-pv[i]
        Kc = 0.1
        return pv[i] + Kc*error
    
    #def
            
    

        
        
    def update_figure(self):
       
        # Defined the variables to simplify
        _t = self.t
        _sp = self.sp
        _pv = self.pv
        _dt = self.step
        _cnt = self.cnt
        _amp = self.amp
        
        
        # Increment the counter for each timestep
        self.counter+=_dt
        _t.append(self.counter)
        
        # Update PV
        if self.counter <= _dt:
            _pv.append(self.pv_init)
                       
        else:
            # Add noise to the PV signal to make it realistic  
            _pv.append(self.calcPV(_t, _pv, _sp)*(1+random.randint(-2.5,2.5)/100))
            _cnt.append(_cnt[-1]-1)
        
        if (self.counter <=_dt) or (_cnt[-1] <= 0):
            _cnt.append(random.randint(self.min_sp_counter,self.max_sp_counter))
        else:            
            _cnt.append(_cnt[-1]-1)
        
        # Update SP
        # Generate a PRBS - we are using cnt to see if the previous value is < 0
        # If it is, then we reset the cnt to a random value. This is to hold the
        # SP until the next change
        
        if self.counter <=_dt:
            _sp.append(random.randint(-100*_amp, 100*_amp)/100)
        else:
            if _cnt[-1] > 0:
                _sp.append(_sp[-1])
            else:
                _sp.append(random.randint(-100*_amp, 100*_amp)/100)
                
        # Plot            
        self.axes.plot(_t, _pv, 'b',_t, _sp,'r')
        self.axes.set_xlabel('time')
        self.axes.set_title('PV, SP vs time')
        self.axes.legend(['PV', 'SP'])
        self.draw()

class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("PID Tuning")

        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QWidget(self)

        l = QVBoxLayout(self.main_widget)        
        dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        dc2 = FirstOrderDeadTime(self.main_widget, width=5, height=4, dpi=100)        
        l.addWidget(dc)
        l.addWidget(dc2)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("Tuning in progress!", 2000000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QMessageBox.about(self, "About","""Simple PID Controller simulation""")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    aw = ApplicationWindow()
    aw.setWindowTitle("PyQt5 PID Example")
    aw.show()
    #sys.exit(qApp.exec_())
app.exec_()