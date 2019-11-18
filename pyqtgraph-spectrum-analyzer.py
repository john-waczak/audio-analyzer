from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import numpy as np
import struct
import pyaudio
from scipy.fftpack import fft
from scipy.signal import periodogram
import sys


class SpectrumAnalyzer(object):
    def __init__(self):
        # microphone setup
        self.chunk = 1024*2
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100


        # set up graph
        pg.setConfigOptions(antialias=True)
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle("Spectrum Analyzer")

        self.waveform = self.win.addPlot(
            title = "Waveform",
        )

        self.win.nextRow()
        self.spectrum = self.win.addPlot(
            title = "Spectrum",
        )

        self.traces = dict()   # to hold the data we will plot

        # set up audio stream
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.format,
            channels = self.channels,
            rate = self.rate,
            input = True,
            output = True,
            frames_per_buffer = self.chunk
        )


        self.t = np.linspace(0, self.chunk/self.rate, self.chunk)  # dt is just 1/(sample rate)
        self.f = np.linspace(0, self.rate, self.chunk)  # We can only go up to half of the sample frequency to satisfy NYQUIST sampling condition

    def start(self):
        QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, data_x, data_y):
        # if the trace exists, update the plot
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)

        # Otherwise, add the trace to the dictionary
        else:
            if name == "waveform":
                self.traces[name] = self.waveform.plot(pen='c', width=3)
                self.waveform.setXRange(0, self.chunk/self.rate, padding=0)
                self.waveform.setYRange(0, 255, padding=0)

            if name == "spectrum":
                self.traces[name] = self.spectrum.plot(pen='m', width=3)
                self.spectrum.setXRange(20, self.rate/2, padding=0)
                self.spectrum.setYRange(0, 1, padding=0)

    def update(self):
        waveform = self.stream.read(self.chunk)
        waveform = struct.unpack(str(2*self.chunk)+'B', waveform)
        waveform = np.array(waveform, dtype='b')[::2] + 128
        self.set_plotdata(name="waveform", data_x = self.t, data_y = waveform)

        spectrum = 2*np.abs(fft(waveform))**2
        spectrum = spectrum/np.amax(spectrum[1:])
        self.set_plotdata(name="spectrum", data_x = self.f[2:], data_y = spectrum[2:])

    def run(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()



if __name__ == '__main__':

    SA = SpectrumAnalyzer()
    SA.run()











