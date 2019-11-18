import numpy as np
import struct
import matplotlib.pyplot as plt
import pyaudio
from scipy.fftpack import fft
from scipy.signal import periodogram


# constants
CHUNK = 1024 * 2             # size of a sample
FORMAT = pyaudio.paInt16     # audio format 
CHANNELS = 1                 # single channel for microphone
RATE = 44100                 # samples per second


fig, (ax, ax2) = plt.subplots(2, figsize=(15, 7))
p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

x = np.arange(0, 2 * CHUNK, 2)
line, = ax.plot(x, np.zeros(CHUNK), '-', lw=2)

x_fft = np.linspace(0, RATE, CHUNK)
line_fft, = ax2.semilogx(x_fft, np.zeros(CHUNK), '-', lw=2)


# graph formatting
ax.set_title('AUDIO WAVEFORM')
ax.set_xlabel('samples')
ax.set_ylabel('volume')
ax.set_ylim(0, 255)
ax.set_xlim(0, 2 * CHUNK)
plt.setp(ax, xticks=[0, CHUNK, 2 * CHUNK], yticks=[ 0, 128, 255])
plt.show(block=False)

ax2.set_xlim(20, RATE/2)
ax2.set_ylim(0, 1)


print('stream started')
while True:
    #read data
    data = stream.read(CHUNK)
    # convert to integer
    data_int = struct.unpack(str(2 * CHUNK) + 'B', data)
    # shift the data so that it is centered correctly
    data_np = np.array(data_int, dtype='b')[::2] + 128
    data_power = 2*np.abs(fft(data_np))
    data_power = data_power/(256*CHUNK)
    line.set_ydata(data_np)
    line_fft.set_ydata(data_power)

    fig.canvas.draw()
    fig.canvas.flush_events()
