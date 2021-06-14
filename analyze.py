import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.flowchart import Flowchart, Node
from DIPPID_pyqtnode import BufferNode, DIPPIDNode
import pyqtgraph.flowchart.library as fclib
import numpy as np


class NormalVectorNode(Node):

    nodeName = "NormalVector"

    def __init__(self, name):
        terminals = {
            'accelX': dict(io='in'),
            'accelZ': dict(io='in'),
            'rotation': dict(io='out'),
        }
        self.rotation = []
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kargs):
        x = kargs['accelX'][0]
        z = kargs['accelZ'][0]
        new_x = -x
        new_y = z
        self.rotation = np.array([[0, 0], [new_x, new_y]])
        return {'rotation': self.rotation}


fclib.registerNodeType(NormalVectorNode, [('Data',)])


class LogNode(Node):

    nodeName = 'Log'

    def __init__(self, name):
        terminals = {
            'accelX': dict(io='in'),
            'accelY': dict(io='in'),
            'accelZ': dict(io='in'),
        }
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kargs):
        x = kargs['accelX'][0]
        y = kargs['accelY'][0]
        z = kargs['accelZ'][0]
        x_text = 'Accel X: '
        y_text = ',Accel Y: '
        z_text = ',Accel Z: '
        print(x_text, x, y_text, y, z_text, z)


fclib.registerNodeType(LogNode, [('Log',)])


def create_analyzing_chart():
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('Analyze Accelerometer')
    central = QtGui.QWidget()
    win.setCentralWidget(central)
    layout = QtGui.QGridLayout()
    central.setLayout(layout)

    fc = Flowchart(terminals={'out': dict(io='out')})
    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    # plot for accel value X
    pw_1 = pg.PlotWidget()
    layout.addWidget(pw_1, 0, 1)
    pw_1.setYRange(-1, 1)
    pw_1.setTitle('Accelerometer X')
    # plot for accel value Y
    pw_2 = pg.PlotWidget()
    layout.addWidget(pw_2, 0, 2)
    pw_2.setYRange(-1, 1)
    pw_2.setTitle('Accelerometer Y')
    # plot for accel value Z
    pw_3 = pg.PlotWidget()
    layout.addWidget(pw_3, 1, 1)
    pw_3.setYRange(-1, 1)
    pw_3.setTitle('Accelerometer Z')
    # plot for normalvector
    pw_4 = pg.PlotWidget()
    layout.addWidget(pw_4, 1, 2)
    pw_4.setYRange(-1.5, 1.5)
    pw_4.setXRange(-1.5, 1.5)
    pw_4.setTitle('Normal Vector')

    # create node for each plot and connect with plot visualization
    pw_1_node = fc.createNode('PlotWidget', pos=(300, -50))
    pw_1_node.setPlot(pw_1)
    pw_2_node = fc.createNode('PlotWidget', pos=(300, 50))
    pw_2_node.setPlot(pw_2)
    pw_3_node = fc.createNode('PlotWidget', pos=(300, 100))
    pw_3_node.setPlot(pw_3)
    pw_4_node = fc.createNode('PlotWidget', pos=(300, -100))
    pw_4_node.setPlot(pw_4)
    # create node and buffernode for each accelerometer value
    dippid_node = fc.createNode("DIPPID", pos=(0, 0))
    buffer_node_1 = fc.createNode("Buffer", pos=(150, -50))
    buffer_node_2 = fc.createNode("Buffer", pos=(150, 0))
    buffer_node_3 = fc.createNode("Buffer", pos=(150, 50))
    # create node for normalvector
    normal_vector_node = fc.createNode("NormalVector", pos=(150, -100))
    # create node for logging
    log_node = fc.createNode("Log", pos=(150, 100))

    # connect all accelerometer nodes with buffer nodes and plot each
    fc.connectTerminals(dippid_node['accelX'], buffer_node_1['dataIn'])
    fc.connectTerminals(buffer_node_1['dataOut'], pw_1_node['In'])
    fc.connectTerminals(dippid_node['accelY'], buffer_node_2['dataIn'])
    fc.connectTerminals(buffer_node_2['dataOut'], pw_2_node['In'])
    fc.connectTerminals(dippid_node['accelZ'], buffer_node_3['dataIn'])
    fc.connectTerminals(buffer_node_3['dataOut'], pw_3_node['In'])
    # connect normal vector node for rotation around y
    fc.connectTerminals(dippid_node['accelX'], normal_vector_node['accelX'])
    fc.connectTerminals(dippid_node['accelZ'], normal_vector_node['accelZ'])
    fc.connectTerminals(normal_vector_node['rotation'], pw_4_node['In'])
    # connect nodes for logging
    fc.connectTerminals(dippid_node['accelX'], log_node['accelX'])
    fc.connectTerminals(dippid_node['accelY'], log_node['accelY'])
    fc.connectTerminals(dippid_node['accelZ'], log_node['accelZ'])

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stdout.write("Need a port number. E.g. 5700")
    elif len(sys.argv) > 2:
        sys.stdout.write("Only one port number necessary")
    else:
        port = sys.argv[1]

    create_analyzing_chart()
