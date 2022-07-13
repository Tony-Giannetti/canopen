# To set up can0 to enable communication:
#  $ sudo ip link set up can0 type can bitrate 500000
# To fix No buffer space available:
#  $ sudo ifconfig can0 txqueuelen 1000 
# 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 

# Doc's
#   https://canopen.readthedocs.io/en/latest/

from xml.etree.ElementTree import tostring
import canopen
import time
import math

network = canopen.Network()
node_01 = canopen.RemoteNode(1, 'lichaun_servo_node_01.eds')
node_02 = canopen.RemoteNode(2, 'lichaun_servo_node_02.eds')
network.add_node(node_01)
network.add_node(node_02)

#   
device_type = node_01.sdo[0x1000]
#identity_object = node.sdo[0x1018]
control_word = node_01.sdo[0x6040]
status_word = node_01.sdo[0x6041]
Modes_of_operation = node_01.sdo[0x6060]
position_absolute_word = node_01.sdo[0x6064]
heartbeat = node_01.sdo['Producer heartbeat time']
target_position = node_01.sdo[0x607A]
profile_velocity = node_01.sdo[0x6081]
profile_acceleration = node_01.sdo[0x6083]
profile_deceleration = node_01.sdo[0x6084]
torque_slope = node_01.sdo[0x6087]
target_torque = node_01.sdo[0x6071]
target_velocity = node_01.sdo[0x60FF]

#   Display things
def print_objects():
    print("")
    print("Device type = 0x%X" % device_type.raw)
    #print(identity_object)
    print("Control word = 0x%X" % control_word.raw)
    print("Status word = 0x%X" % status_word.raw)
    print("Status word bit 10 ", status_word.bits[10])
    print("modes of operation = 0x%X" % Modes_of_operation.raw)
    print("Absolute position = 0x%X" % position_absolute_word.raw)
    print("Target position = 0x%X" % target_position.raw)
    print("Target velocity = 0x%X" % target_velocity.raw)
    #print("Profile velocity= 0x%X" % profile_velocity.raw)
    #print("Profile acceleration= 0x%X" % profile_acceleration.raw)
    #print("Profile deceleration= 0x%X" % profile_deceleration.raw)

def connect_network():
    print("Connecting CAN Socket")
    network.connect(channel='can0', bustype='socketcan')

def disconnect_network():
    network.disconnect()

#   Reset CAN
def reset_can(node):
    node.nmt.state = 'RESET'
    node.nmt.wait_for_bootup(15)
    print("Node reset")
    #time.sleep(1)

#   Search for nodes and display found nodes
def scan_nodes():
    network.scanner.search()
    time.sleep(0.05)
    for node_id in network.scanner.nodes:
        print("Found node %d!" % node_id)
        #return node_id

    #   Sync
def start_sync(node):
    interval = 0.1
    network.sync.start(interval)
    print("Network sync started")
    #print("Network sync started @ %d " % str(interval), "ms")

def enable_drive(node):
    node.sdo['Controlword'].raw = 6
    time.sleep(0.01)
    node.sdo['Controlword'].raw = 7
    time.sleep(0.01)
    node.sdo['Controlword'].raw = 15
    time.sleep(0.1)
    #   Check if drive status is enabled at 0x6041[1]
    if node.sdo[0x6041].bits[1]:
        #currentNode = tostring(node)
        print("Drive enabled!")
    else:
        print("Drive enable failed!")

def enable_drives(*args):
    for node in args:
        enable_drive(node)

def disable_drive(node):
    node.sdo['Controlword'].raw = 0
    if node.sdo['Controlword'].raw == 0:
        print("Drive disabled!")

def disable_drives(*args):
    for node in args:
        disable_drive(node)

def wait_for_target_reached(node):
    while True:
        targetReached = node.sdo[0x6041].bits[10]
        if targetReached:
            break
        time.sleep(0.01)

#   Torque mode
def run_torque(node, torque, seconds):
    node.sdo['Modes of operation'].raw = 4
    enable_drive(node)
    node.sdo['Torque slope'].raw = 5000
    node.sdo['Target torque'].raw = torque
    time.sleep(seconds)
    node.sdo['Target torque'].raw = 0

#   Speed mode
def run_speed(node, rpm, seconds):
    node.sdo['Modes of operation'].raw = 3
    #enable_drive(node)
    node.sdo['Profile acceleration'].raw = 100
    node.sdo['Profile deceleration'].raw = 100
    node.sdo['Target velocity'].raw = rpm * 10
    #time.sleep(seconds)

def goto_pos(node, pos, rpm):
    node.sdo[0x6060].raw = 1
    node.sdo[0x6040].bits[4] = 0
    node.sdo[0x607A].raw = pos
    node.sdo[0x6081].raw = rpm * 10
    node.sdo[0x6083].raw = 100
    node.sdo[0x6084].raw = 100
    node.sdo[0x6040].bits[4] = 1
    #wait_for_target_reached(node)

def rotate_by_revs(node, revs, rpm):
    currentPos = node.sdo[0x6064].raw
    totalPulses = (revs * 131072)
    targetPos = currentPos + totalPulses
    #rpm = rpm*10
    goto_pos(node, targetPos, rpm)

def run_demo():
    rotate_by_revs(node_01, 3, 100)
    wait_for_target_reached(node_01)
    rotate_by_revs(node_02, 3, 100)
    wait_for_target_reached(node_02)
    rotate_by_revs(node_01, -10, 500)
    wait_for_target_reached(node_01)
    rotate_by_revs(node_02, -10, 500)
    wait_for_target_reached(node_02)
    rotate_by_revs(node_01, 5, 100)
    rotate_by_revs(node_02, 5, 100)
    wait_for_target_reached(node_01)
    wait_for_target_reached(node_02)
    for i in range(6):
        rotate_by_revs(node_01, 0.1, 100)
        rotate_by_revs(node_02, 0.1, 100)
        wait_for_target_reached(node_01)
        wait_for_target_reached(node_02)
        time.sleep(0.2)
        time.sleep(0.5)
    for i in range(2):
        rotate_by_revs(node_01, -15, 2500)
        rotate_by_revs(node_02, -15, 2500)
        wait_for_target_reached(node_01)
        wait_for_target_reached(node_02)
        time.sleep(0.2)
        rotate_by_revs(node_01, 15, 2500)
        rotate_by_revs(node_02, 15, 2500)
        wait_for_target_reached(node_01)
        wait_for_target_reached(node_02)
        time.sleep(0.2)
    
def set_rpdo():
    #node_01.tpdo.read()
    #node.nmt.state = 'OPERATIONAL'
    #node.nmt.wait_for_heartbeat()
    #assert node.nmt.state == 'OPERATIONAL'
    node_01.tpdo[1].clear()
    node_01.tpdo[1].add_variable(0x6041)
    node_01.tpdo[1].trans_type = 254
    node_01.tpdo[1].event_timer = 10
    node_01.tpdo[1].enabled = True
    node_01.nmt.state = 'OPERATIONAL'
    node_01.tpdo.save()
    #node.rpdo[4].start(0.1)

def move_absolute(node, pulses, rpm):
    node.sdo[0x6060].raw = 1
    node.sdo[0x6040].bits[4] = 0
    node.sdo[0x607A].raw = pulses
    node.sdo[0x6081].raw = rpm * 10
    node.sdo[0x6083].raw = 100
    node.sdo[0x6084].raw = 100
    node.sdo[0x6040].bits[4] = 1
    #wait_for_target_reached(node)

def move_relative(pulses, rpm):
    print(rpm)

def interpolate(node):
    node.sdo[0x6060].raw = 6
    enable_drive(node)
    print("Interpolation mode.")
    for i in range(1000):
        print(i*1000)
        node.sdo[0x60C1].raw = i*1000
        time.sleep(0.004)

if __name__ == '__main__':

    connect_network()
    scan_nodes()
    #node_01.nmt.state = 'OPERATIONAL'
    #interpolate(node_01)
    #node_01.nmt.send_command(0x1)
    #print(node_01.sdo_channels)
    #print(node_01.sdo[0x1006].raw)
    #print(node_01.sdo[0x60C2].bits[2])
    #node.sdo.upload(position_absolute_word, 1)
    #set_rpdo()
    #print_objects()
    #enable_drive(node_01)
    #enable_drive(node_02)
    #enable_drives(node_01, node_02)
    #run_demo()
    #run_torque(node_01, 80, 10)
    #run_speed(node_02, 1000, 3)
    #time.sleep(5)
    #goto_pos(node_01, 0, 2000)
    #goto_pos(node_02, 0, 2000)
    #move_absolute(node_02, 0, 1000)
    #wait_for_target_reached(node_02)
    #move_absolute(node_02, 0, 1000)
    #disable_drive(node_01)
    #disable_drive(node_02)
    #disable_drives(node_01, node_02)
    #network.sync.stop()
    network.disconnect()
