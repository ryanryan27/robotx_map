#!/usr/bin/env python3
# license removed for brevity

import operator
import functools
import socket
import rospy
from time import localtime, strftime, asctime
from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix
from estop_msgs.msg import EstopState
# From 2014 test script
# by Bill Porter https://github.com/madsci1016/RoboNationTestServer/blob/master/RNCommsTest.py

def calcchecksum(string):
    return functools.reduce(operator.xor, map(ord, string), 0)


class HeartBeat:
    UAV_STATUS = {1:"stowed", 2:"deployed", 3:"killed"}

    TASK_STATUS = {0:1, 1:2}
    COLOUR_MAP = {1:"R", 2:"G", 3:"B"}
    
    current_task = 0

    #list of all data required for all task messages
    data = {
        'date': 'ddmmyy',
        'time': 'hhmmss',
        'team_id': 'ROBOT',
        'message_id': '$RXHRB',
        'latitude': 21.31198,
        'n/s_indicator': 'S',
        'longitude': 157.88972,
        'e/w_indicator': 'E',
        'system_mode': 1,
        'uav_status': 2,
        'active_entrance_gate': 1,
        'active_exit_gate': 1,
        'finished': 1,
        'numdected': 1,
        'wildlife_1': 'P',
        'wildlife_2': 'T',
        'wildlife_3': 'C',
        'light_pattern': 'RGB',
        'dock_colour': 'R',
        'ams_staus': 1,
        'target_colour': 'R',
        'item_status': 0,
        'object_1_reported':"R",
        'object_1_latitude':21.31198,
        'object_1_n/s_indicator':"S",
        'object_1_longitude':157.88972,
        'object_1_e/w_indicator':"E",
        'object_2_reported':"N",
        'object_2_latitude':21.31198,
        'object_2_n/s_indicator':"S",
        'object_2_longitude':157.88972,
        'object_2_e/w_indicator':"E"
    }
    
    #message format unique for each task usings keys from data dictionary
    heartbeat_msg = [
        'message_id',
        'date', 'time',
        'latitude',
        'n/s_indicator',
        'longitude',
        'e/w_indicator',
        'team_id',
        'system_mode',
        'uav_status'
    ]
    entrance_gate_msg = [
        'message_id',
        'date',
        'time',
        'team_id',
        'active_entrance_gate',
        'active_exit_gate'
    ]
    follow_path_msg = [
        'message_id',
        'date',
        'time',
        'team_id',
        'finished']
    wildlife_encounter_msg = [
        'message_id',
        'date',
        'time',
        'team_id',
        'numdected',
        'wildlife_1',
        'wildlife_2',
        'wildlife_3'
    ]
    scan_the_code_msg = [
        'message_id',
        'date',
        'time',
        'team_id',
        'light_pattern'
    ]
    detect_and_dock_msg = [
        'message_id',
        'date',
        'time',
        'team_id',
        'dock_colour',
        'ams_staus'
    ]
    find_and_fling_msg = [
        'message_id',
        'date',
        'time',
        'team_id',
        'target_colour',
        'ams_staus']
    uav_replenishment_msg = [
        'message_id',
        'date',
        'time',
        'team_id',
        'uav_status',
        'item_status'
    ]
    uav_search_and_report_msg = [
        'message_id',
        'date',
        'time',
        'object_1_reported',
        'object_1_latitude',
        'object_1_n/s_indicator',
        'object_1_longitude',
        'object_1_e/w_indicator',
        'object_2_reported',
        'object_2_latitude',
        'object_2_n/s_indicator',
        'object_2_longitude',
        'object_2_e/w_indicator',
        'team_id',
        'uav_status'
    ]

    def __init__(self):
        self.address = rospy.get_param('/wamv/judges_station/address')
        self.port = rospy.get_param('/wamv/judges_station/port')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.bind((self.address, self.port))
        self.socket.connect((self.address, self.port))

        self.data['team_id'] = rospy.get_param('/wamv/judges_station/team_id')

        self.message = str()

        rospy.init_node('judges', anonymous=False)
        rospy.Subscriber("sensors/gps/gps/fix", NavSatFix, self.fixCallback)
        rospy.Subscriber("estop/estop_state", EstopState, self.updateSystemMode)

        #subscribe to message planning node and recieve current task
        #rospy.Subscriber("missionPlanner", currentTask self.updateTask)

    def setData(self,name,value):
        self.data[name]=value

    def startMessage(self,packetId):
        self.message=packetId
        #self.addComponentToMessage(HeartBeat.TEAMNAME,comma=False)

    def addComponentToMessage(self,component,comma=True):
        if self.message != "":
            self.message=self.message+","
        if component in self.data:
            self.message=self.message+str(self.data[component])

    def endMessage(self):
        checksum = calcchecksum(self.message)
        self.message="$"+self.message+"*"+str('%X' % checksum)+"\r\n"
        print("message", self.message)

    def sendMessage(self,components):
        self.message = ""
        for component in components:
            self.addComponentToMessage(component)
        self.endMessage()
        self.socket.send(self.message.encode('utf-8'))

    def fixCallback(self,msg):
        self.data['latitude'] = round(abs(msg.latitude),5)
        self.data['longitude'] = round(abs(msg.longitude),5)
        self.data['n/s_indicator'] = "N" if msg.latitude >= 0 else "S"
        self.data['e/w_indicator'] = "E" if msg.longitude >= 0 else "W"

    def updateTask(self,msg):        
        #change msg.something to appropriate message variable
        self.currentTask = msg.currentTask

    def updateSystemMode(self,msg):
        #this dictionary mapping will need to change when subcribed to the new estop kill system   
        SYSTEM_MODE = {msg.MANUAL:1, msg.MANUAL_ASSIST:1, msg.AUTO:2, msg.STOP:3, msg.LINKLOSS:0}
                      
        self.data['system_mode'] = SYSTEM_MODE[msg.estop_state]

    def updateEntranceGate(self,msg):
        #change msg.something to appropriate message variable
        #change dictionary if internal numbers don't match the numbers in the output message
        GATE_NUMBERS = {1:1, 2:2, 3:3}
        
        self.data['active_entrance_gate'] = SYSTEM_MODE[msg.active_entrance_gate]
        self.data['active_exit_gate'] = SYSTEM_MODE[msg.active_exit_gate]

    def updateFollowPath(self,msg):
        #change msg.something to appropriate message variable
        self.data['finished'] = TASK_STATUS[msg.finished]
        
    def updateWildlife(self,msg):
        #change msg.something to appropriate message variable
        WILDLIFE_MAP = {0:"P", 1:"C", 2:"T"}
        
        self.data['numdected'] = SYSTEM_MODE[msg.numdected]
        self.data['wildlife_1'] = WILDLIFE_MAP[msg.wildlife_1]
        self.data['wildlife_2'] = WILDLIFE_MAP[msg.wildlife_2]
        self.data['wildlife_3'] = WILDLIFE_MAP[msg.wildlife_3]
        
    def updateScanCode(self,msg):
        #change msg.something to appropriate message variable
        pattern = msg.light_pattern

        #convert format from numerical(123) to colour character (RGB) will only work for single letter transformations 
        for element in pattern:
            element = COLOUR_MAP[elemnet]
            
        self.data['light_pattern'] = pattern

    def updateDetectAndDock(self,msg):
        #change msg.something to appropriate message variable
        self.data['dock_colour'] = COLOUR_MAP[msg.dock_colour]

    def updateFindAndFling(self,msg):
        #change msg.something to appropriate message variable
        self.data['target_colour'] = COLOUR_MAP[msg.target_colour]

    def main(self):
        #dictionary with the message id and message format 
        
        message_map = {
            0:{'id':"RXHRB", 'format':self.heartbeat_msg},
            1:{'id':"RXGAT", 'format':self.entrance_gate_msg},
            2:{'id':"RXPTH", 'format':self.follow_path_msg},
            3:{'id':"RXENC", 'format':self.wildlife_encounter_msg},
            4:{'id':"RXCOD", 'format':self.scan_the_code_msg},
            5:{'id':"RXDOK", 'format':self.detect_and_dock_msg},
            6:{'id':"RXFLG", 'format':self.find_and_fling_msg},
            7:{'id':"RXUAV", 'format':self.uav_replenishment_msg},
            8:{'id':"RXSAR", 'format':self.uav_search_and_report_msg}
            }
        
        rate = rospy.Rate(1) # 1hz
        while not rospy.is_shutdown():
            self.data['date'] = strftime("%d%m%y", localtime())
            self.data['time'] = strftime("%H%M%S", localtime())
            self.data['message_id'] = message_map[self.current_task]["id"]
            self.sendMessage(message_map[self.current_task]["format"])
            #self.sendLatLon()



            rate.sleep()
        
if __name__ == '__main__':
    heartbeat = HeartBeat()
    heartbeat.main()


