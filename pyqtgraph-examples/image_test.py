from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg


app = QtGui.QApplication([])
## Create window with GraphicsView widget
# win = pg.GraphicsLayoutWidget()
win = pg.GraphicsWindow()
win.show()

view = win.addPlot()
# view = win.addViewBox()
view.setAspectLocked(True)

# img = pg.ImageItem(border='w')
img = pg.ImageItem()
view.addItem(img)


## Create random image
data = np.random.normal(size=(15, 600, 600), loc=1024, scale=64).astype(np.uint16)
i = 0


def updateData():
    global img, data, i

    ## Display the data
    img.setImage(data[i])
    i = (i+1) % data.shape[0]
    QtCore.QTimer.singleShot(1, updateData)

updateData()

if __name__ == '__main__':
    QtGui.QApplication.instance().exec_()
