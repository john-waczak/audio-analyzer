import queue

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd

DEVICE = sd.default.device
CHANNELS = 1
device_info = sd.query_devices(DEVICE, 'input')
SAMPLERATE = device_info['default_samplerate']
DOWNSAMPLE = 10
WINDOW = 200
INTERVAL = 30


q = queue.Queue()


def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    q.put(indata[::DOWNSAMPLE])


def update_plot(frame):
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """
    global plotdata
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break
        shift = len(data)
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:] = data[:,0]
        line.set_ydata(plotdata)
    return line,


try:
    length = int(WINDOW * SAMPLERATE / (1000 * DOWNSAMPLE))
    plotdata = np.zeros(length)

    fig, ax = plt.subplots()
    line, = ax.plot(plotdata)
    ax.axis((0, len(plotdata), -1, 1))
    ax.set_yticks([0])
    ax.yaxis.grid(True)
    ax.tick_params(bottom=False, top=False, labelbottom=False,
                   right=False, left=False, labelleft=False)
    fig.tight_layout(pad=0)

    stream = sd.InputStream(
        device=DEVICE, channels=CHANNELS,
        samplerate=SAMPLERATE, callback=audio_callback)
    ani = FuncAnimation(fig, update_plot, interval=INTERVAL, blit=True)
    with stream:
        plt.show()
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
