
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
import canopen
import driveCommand
import time
import sys

network = canopen.Network()
class ObjectDictionaryMonitor(QtWidgets.QWidget):
    def __init__(self):
        super(ObjectDictionaryMonitor, self).__init__()
        uic.loadUi('objectDictionaryMonitor.ui', self)
        self.show()

    #    timer = QTimer(self)
    #    timer.setInterval(200)
    #    timer.timeout.connect(self.Update_Absolute_Pos)
    #    timer.start()

    #def Update_Absolute_Pos(self):
    #    #pos = driveCommand.
    #    self.lbl.positioActualValue.setText(str(node.sdo[0x6064].raw))

    @QtCore.pyqtSlot(name="on_btn_connectNetwork_clicked")
    def connect_network_btn_clicked(self):
        print("Connecting CAN Socket")
        network.connect(channel='can0', bustype='socketcan')
        #driveCommand.connect_network()

    @QtCore.pyqtSlot(name="on_btn_scanNodes_clicked")
    def scan_nodes_btn_clicked(self):
        network.scanner.search()
        time.sleep(0.05)
        print(network.scanner.nodes)
        for node_id in network.scanner.nodes:
            btnName = "btn_node_%d" % node_id
            btn = QPushButton(btnName, self)
            btn.setParent(self.frame_01)
            btn.setFixedSize(100, 50)
            btn.move((node_id * 100)-100, 0)
            btn.setText(btnName)
            btn.setObjectName(btnName)
            btn.setProperty(btnName)
            #print(node_id)
            print(btnName)
            #btn.clicked.connect(self.verify(node_id))
            btn.clicked.connect(lambda: self.verify(btnName))
            btn.show()
            #@QtCore.pyqtSlot(name="on_%s_clicked" % btnName)
            #def btn_clicked(self):
            #    self.verify(btnName)

    def verify(self, nodeId):
        print(nodeId)

app = QtWidgets.QApplication(sys.argv)
window = ObjectDictionaryMonitor()
app.exec()
