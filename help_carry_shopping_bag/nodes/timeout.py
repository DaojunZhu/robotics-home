#! /usr/bin/env python
import rospy
from std_msgs.msg import Int16
from std_msgs.msg import String

class Timeout():
    def __init__(self):
        rospy.init_node('Timeout')
        #set the challenge time for 6 minutes
        self.time_remain = 360
        self.r = rospy.Rate(1)
        self.challenge_start_flag = False
        #publish the flag of challenge time ended
        self.pub = rospy.Publisher('challenge_time_over_flag',Int16,queue_size=10)
        self.sub = rospy.Subscriber('voice_command',String,self.voice_cmd_cb)
        
    def voice_cmd_cb(self,msg):
        if msg.data == 'continue':
            self.challenge_start_flag = True
        
    def execute(self):
        rospy.loginfo('wait challenge to start...')
        while not rospy.is_shutdown():   
            if self.challenge_start_flag:
                while self.time_remain:
                    self.pub.publish(self.time_remain)
                    self.time_remain -= 1
                    #debug
                    rospy.loginfo('the time remainning: %d' % self.time_remain)
                    #sleep
                    self.r.sleep()
            else:
                pass
               

if __name__ == '__main__':
    try:
        obj = Timeout()
        obj.execute()
    except rospy.ROSInterruptException:
        rospy.loginfo("node terminated.")   