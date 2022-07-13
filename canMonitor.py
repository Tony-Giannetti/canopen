
import canopen
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
import sys
import driveCommand

import time
import math
import configparser

config = configparser.ConfigParser()
#jogSpeed = config['DEFAULT']['jogSpeed']
#config['DEFAULT'] = {'JogSpeed': '200'}
config.read('config.ini')
#config['move_pos'] = {}
#with open('config.ini', 'w') as configfile:
#    config.write(configfile)

network = canopen.Network()
network.connect(channel='can0', bustype='socketcan')
node_01 = canopen.RemoteNode(1, 'lichaun_servo_node_01.eds')
node_02 = canopen.RemoteNode(2, 'lichaun_servo_node_02.eds')
network.add_node(node_01)
network.add_node(node_02)

class DemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DemoWidget, self).__init__()
        uic.loadUi('untitled.ui', self)
        #self.lbl_01.setText("Updated Text")
        self.show()

        radiobutton = QRadioButton("radioButton")
        self.radioButton.toggled.connect(self.enable_jog_selected)
        self.lineEdit_02.setText(config.get('DEFAULT', 'jogSpeed'))
        self.lineEdit_02.textChanged.connect(self.set_jog_speed)

        timer = QTimer(self)
        timer.setInterval(200)
        timer.timeout.connect(self.Update_Absolute_Pos)
        timer.start()

    def set_jog_speed(self):
        #if self.lineEdit_02 < '2500':
        speed = self.lineEdit_02.text()
        #if float(speed) < 2501:
        config.set('DEFAULT', 'jogSpeed', self.lineEdit_02.text())
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def enable_jog_selected(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            print("event")
            def keyPressEvent(self, e):
                print("key event")
                if e.key() == QtCore.Qt.Key_Up:
                    rpm = self.lineEdit_02.text()
                    driveCommand.run_speed(node_01, int(rpm), 0)
                else:
                    driveCommand.run_speed(node_01, 0, 0)

    def Update_Absolute_Pos(self):
        self.node_01_pos.setText(str(node_01.sdo[0x6064].raw))

    @QtCore.pyqtSlot(name="on_btn_start_sync_clicked")
    def btn_start_sync_clicked(self):
        driveCommand.start_sync(node_01)

    @QtCore.pyqtSlot(name="on_btn_enable_drive_clicked")
    def btn_enable_drive_clicked(self):
        driveCommand.enable_drive(node_01)

    @QtCore.pyqtSlot(name="on_btn_disable_drive_clicked")
    def btn_disable_drive_clicked(self):
        driveCommand.disable_drive(node_01)

    @QtCore.pyqtSlot(name="on_btn_reset_node_clicked")
    def btn_reset_node_clicked(self):
        driveCommand.reset_can(node_01)
 
    @QtCore.pyqtSlot(name="on_btn_run_demo_clicked")
    def btn_run_demo_clicked(self):
        driveCommand.run_demo()

    @QtCore.pyqtSlot(name="on_btn_go_clicked")
    def btn_go_clicked(self):
        pos = self.lineEdit_01.text()
        rpm = self.lineEdit_02.text()
        driveCommand.goto_pos(node_01, pos, int(rpm))

    @QtCore.pyqtSlot(name="on_btn_jog_positive_pressed")
    def btn_jog_positive_clicked(self):
        rpm = config.get('DEFAULT', 'jogSpeed')
        print(rpm)
        driveCommand.run_speed(node_01, int(rpm), 0)

    @QtCore.pyqtSlot(name="on_btn_jog_positive_released")
    def btn_jog_positive_released(self):
        driveCommand.run_speed(node_01, 0, 0)

    @QtCore.pyqtSlot(name="on_btn_jog_negative_pressed")
    def btn_jog_negative_clicked(self):
        rpm = config.get('DEFAULT', 'jogSpeed')
        driveCommand.run_speed(node_01, 0 - (int(rpm)), 0)

    @QtCore.pyqtSlot(name="on_btn_jog_negative_released")
    def btn_jog_negative_pressed(self):
        driveCommand.run_speed(node_01, 0, 0)

    @QtCore.pyqtSlot(name="on_lineEdit_01_returnPressed")
    def absolute_position_entered(self):
        pos = self.lineEdit_01.text()
        rpm = config.get('DEFAULT', 'jogSpeed')
        driveCommand.goto_pos(node_01, pos, int(rpm))

    @QtCore.pyqtSlot(name="on_btn_apply_released")
    def apply_pressed(self):
        print("apply pressed")


app = QtWidgets.QApplication(sys.argv)
window = DemoWidget()
app.exec_()
