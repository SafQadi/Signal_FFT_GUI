"""
A simple python GUI generated with pyQt5 Designer to calculate and show the FFT of time series
(separated by a tabulator {\t}. A low pass filter can also be applied on the series.
An input field allows the user to input the value of the cutoff frequency of the filter.

Author: Safwan Al-Qadhi
Last modified: 22.07.2021
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
import sys

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from Signal_FFT import Ui_MainWindow
from filter import MyFilter


class MainClass(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainClass, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.checkBox_f_first.setChecked(True)
        self.ui.textEdit_set_f_cut.setText("6")
        self.ui.graph_1.setBackground((80, 70, 110))
        self.ui.graph_2.setBackground((80, 70, 110))

        self.ui.load_pushButton.clicked.connect(self.load_data)
        self.ui.analyse_pushButton.clicked.connect(self.display_fft)
        self.ui.Filter_Botton.clicked.connect(self.apply_filter)

        self.ui.checkBox_f_first.stateChanged.connect(self.select_pt1_filter)
        self.ui.checkBox_f_second.stateChanged.connect(self.select_biquad_filter)
        self.ui.textEdit_set_f_cut.textChanged.connect(self.set_filter_cutoff)

        self.time = []
        self.values = []
        self.applied_filter = 'pt1'
        self.filter_cutoff = 6

    def load_data(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName()[0]
        print(fileName)
        data = np.genfromtxt(fileName, delimiter="\t", skip_header=1)   # skip_header=0:headers are NaN Values

        self.time = data[:, 0]
        self.values = data[:, 1]

        if np.isnan(np.min(self.time)) or np.isnan(np.min(self.values)):
            print("NaN values!", np.isnan(np.sum(self.values)))
            self.time = pd.Series(self.time)
            self.values = pd.Series(self.values)

            self.time = self.time.interpolate()
            self.values = self.values.interpolate()

        values_mean = np.mean(self.values)
        self.values = self.values - values_mean

        self.ui.label.setText(fileName)
        self.ui.graph_1.clear()
        self.ui.graph_2.clear()

        self.select_graph(1, self.time, self.values, filter=0)

    def select_pt1_filter(self):
        # if self.checkBox_f_first.text() == "1st":
        if self.ui.checkBox_f_first.isChecked():
            self.ui.checkBox_f_second.setChecked(False)
            print(self.ui.checkBox_f_first.text() + " is selected")

            self.applied_filter = "pt1"

    def select_biquad_filter(self):
        # if self.checkBox_f_second.text() == "2nd":
        if self.ui.checkBox_f_second.isChecked():
            self.ui.checkBox_f_first.setChecked(False)

            print(self.ui.checkBox_f_second.text() + " is selected")
            self.applied_filter = "biquad"

    def set_filter_cutoff(self):
        self.filter_cutoff = self.ui.textEdit_set_f_cut.toPlainText()
        if self.filter_cutoff != "":
            self.filter_cutoff = float(self.filter_cutoff)
        else:
            self.filter_cutoff = 6

        print(self.filter_cutoff)

    def apply_filter(self):
        filter_s = MyFilter(self.filter_cutoff, 0.02)
        filtered_values = []

        if self.applied_filter == "pt1":

            for i in self.values:
                filtered_values.append(filter_s.pt1_filter(i))

            self.ui.graph_1.clear()
            self.select_graph(1, self.time, self.values, filter=0)
            self.select_graph(1, self.time, filtered_values, filter=1)

            self.ui.graph_2.clear()
            f, y_fft = MainClass.calc_fft(self.time, self.values)
            self.select_graph(2, f, y_fft, filter=0)  # or  (Y[:501])
            f, y_fft = MainClass.calc_fft(self.time, filtered_values)
            self.select_graph(2, f, y_fft, filter=1)  # or  (Y[:501])

        elif self.applied_filter == "biquad":

            for i in self.values:
                filtered_values.append(filter_s.biquad_filter(i))

            self.ui.graph_1.clear()
            self.select_graph(1, self.time, self.values, filter=0)
            self.select_graph(1, self.time, filtered_values, filter=1)

            self.ui.graph_2.clear()
            f, y_fft = MainClass.calc_fft(self.time, self.values)
            self.select_graph(2, f, y_fft, filter=0)
            f, y_fft = MainClass.calc_fft(self.time, filtered_values)
            self.select_graph(2, f, y_fft, filter=1)

    def display_fft(self):
        F, Y_fft = MainClass.calc_fft(self.time, self.values)
        self.select_graph(2, F, Y_fft, filter=0)

    @staticmethod
    def calc_fft(t, s):
        Y = np.fft.fft(s)
        N = len(Y) / 2 + 1
        dt = t[1] - t[0]
        fa = 1.0 / dt  # sample frequency
        F = np.linspace(0, int(fa / 2), int(N), endpoint=True)
        Y_fft = np.abs(Y[:int(N)]/N)

        return F[20:], Y_fft[20:]

    def select_graph(self, graph, x, y, filter):
        if graph == 1:
            if filter == 0:
                pen = pg.mkPen(color=(255, 0, 0), width=1)
                self.ui.graph_1.plot(x, y, pen=pen, name="signal")
            elif filter == 1:
                pen = pg.mkPen(color=(0, 255, 0), width=1)
                self.ui.graph_1.plot(x, y, pen=pen, name="signal")

            self.ui.graph_1.setTitle("Signal", color="r", size="10pt")
            styles = {'color': 'w', 'font-size': '14px'}
            self.ui.graph_1.setLabel('left', 'Amplitude', **styles)
            self.ui.graph_1.setLabel('bottom', 'Time (s)', **styles)

        elif graph == 2:
            if filter == 0:
                pen = pg.mkPen(color=(255, 0, 0), width=1)
                self.ui.graph_2.plot(x, y, pen=pen, name="signal")
            elif filter == 1:
                pen = pg.mkPen(color=(0, 255, 0), width=1)
                self.ui.graph_2.plot(x, y, pen=pen, name="signal")

            self.ui.graph_2.setTitle("FFT", color="r", size="10pt")
            styles = {'color': 'w', 'font-size': '14px'}
            self.ui.graph_2.setLabel('left', 'Power', **styles)
            self.ui.graph_2.setLabel('bottom', 'frequency (Hz)', **styles)


def main():

    app = QtWidgets.QApplication(sys.argv)
    gui = MainClass()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()





