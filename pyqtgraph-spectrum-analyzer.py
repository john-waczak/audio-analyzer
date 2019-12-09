from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import numpy as np
import struct
import pyaudio
from scipy.fftpack import fft
from scipy.signal import periodogram
import sys
from scipy import signal

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

        self.spectrum = self.win.addPlot(
            title = "Spectrum",
        )

        # make window for spectrogram plot
        self.win.nextRow()
        self.spectrogram = self.win.addPlot()
        self.img = pg.ImageItem()
        self.spectrogram.addItem(self.img)
        self.data = np.zeros((500, int(self.chunk/10)))
#        self.data = np.random.rand(500 ,int(self.chunk/4))
        self.img.setImage(self.data)
        self.spectrogram.hideAxis('bottom')
        self.spectrogram.hideAxis('left')


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


        # set up notch filter for middle c (261.63 hz)
        self.b_notch, self.a_notch = signal.iirnotch(261.63, 1.0, self.rate)

        nyq = self.rate/2
        self.max_freq = 1000/nyq
        self.min_freq = 100/nyq
        # use fifth order butterworth band-pass filter
        self.b_band, self.a_band = signal.butter(5, [self.min_freq, self.max_freq], btype='band')
        self.filteredWaveform = self.win.addPlot(
            title = "Filtered Waveform"
        )

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
                self.spectrum.setLogMode(x=True, y=False)
                self.spectrum.setXRange(np.log10(20), np.log10(self.rate/2), padding=0)
                # self.spectrum.setXRange(20, self.rate/2, padding=0)
                self.spectrum.setYRange(0, 1, padding=0)
            if name == "filtered":
                self.traces[name] = self.filteredWaveform.plot(pen='c', width=3)
                # self.filteredWaveform.setXRange(0, self.chunk/self.rate, padding=0)
                self.filteredWaveform.setXRange(0.01, 0.04, padding=0)
                self.filteredWaveform.setYRange(-128, 128, padding=0)


    def update(self):
        waveform = self.stream.read(self.chunk)



        waveform = struct.unpack(str(2*self.chunk)+'B', waveform)
        waveform = np.array(waveform, dtype='b')[::2] + 128


        self.set_plotdata(name="waveform", data_x = self.t, data_y = waveform)

        spectrum = np.abs(fft(waveform))**2
        spectrum = spectrum/(self.chunk*self.rate) # scale by sample frequency and length of sample
        numToSkip = 4  #ignore the zero frequency when plotting otherwise you wont see anything
        normalizedForPlotting = spectrum[numToSkip:]/np.amax(spectrum[numToSkip:])
        # only go up to half of the sampling frequency to satisfy nyquist condition
        self.set_plotdata(name="spectrum", data_x = self.f[numToSkip:], data_y = normalizedForPlotting)


        # shift data one column to right and make first column the new frequency data
        self.data = np.roll(self.data, 1, axis=0)
        self.data[0,:] = normalizedForPlotting[:int(self.chunk/10)]
        self.img.setImage(self.data)

        # create filtered waveform
        filtered = signal.filtfilt(self.b_notch, self.a_notch, waveform)

        filtered = signal.filtfilt(self.b_band, self.a_band, filtered)

        self.set_plotdata(name="filtered", data_x = self.t, data_y = filtered)



    def run(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()



if __name__ == '__main__':

    SA = SpectrumAnalyzer()
    SA.run()











