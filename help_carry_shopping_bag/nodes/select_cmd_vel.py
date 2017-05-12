#! /usr/bin/env python
#! coding=utf-8

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from topic_tools.srv import MuxSelect
from sound_play.libsoundplay import SoundClient
from move_base_msgs.msg import MoveBaseActionResult


class VoiceCmdSelect():
    def __init__(self):
        rospy.init_node('select_cmd_vel')
        rospy.on_shutdown(self.cleanup)
        
        self.rate = rospy.Rate(5)

        self.first_follow_raise = True
        self.first_car_raise = True
        self.task_done = True

        #create the sound client object
        self.soundclient = SoundClient()

        #set the sound voice
        self.voice  = 'voice_rab_diphone'

        #wait a moment to let the sound client to connect to the sound_play server
        rospy.sleep(1)

        #是否暂停解析语音指令
        self.paused = True

        #订阅voice_command
        self.voice_cmd_sub = rospy.Subscriber('voice_command',String,self.speech_callback)

        self.nav_result = rospy.Subscriber('move_base/result',MoveBaseActionResult,self.nav_result_cb)

        rospy.wait_for_service('mux/select',30)
        self.mux_select = rospy.ServiceProxy('mux/select',MuxSelect)
        
        rospy.loginfo("Connected to mux select service. ")
          
    

    def cleanup(self):
        pass

    def nav_result_cb(self,msg):
        if msg.status.status == 3:
            self.task_done = True


    #speech_callback
    def speech_callback(self,msg): 
        if msg.data == 'continue':
            if self.task_done:
                self.paused = False
                self.task_done = False
               # rospy.loginfo('I will continue listenning')
            else:
                pass
        if msg.data == 'car':
            if self.first_car_raise:
                self.mux_select('stop_cmd_vel')
                self.first_car_raise = False
                self.task_done = True
                self.paused = False
               # rospy.loginfo('I remember the car')
            else:
                pass        
        
        if self.paused:
            return 
        

        if msg.data == 'kitchen' or msg.data == 'bedroom' or msg.data == 'livingroom':
            self.task_done = False
            self.paused = True
            self.mux_select('nav_cmd_vel')

        elif msg.data == 'follow':
            if self.first_follow_raise:
                self.paused = True
                self.mux_select('follow_cmd_vel')
                self.first_follow_raise = False
                rospy.loginfo('I will follow you')
                self.soundclient.say('I will move behind you',self.voice)
            else:
                pass
        else:
            return 

if __name__ == '__main__':
    VoiceCmdSelect()
    rospy.spin()
            


