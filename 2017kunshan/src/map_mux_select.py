#! /usr/bin/env python
#! coding=utf-8


import rospy
from topic_tools.srv import MuxSelect
from std_msgs.msg import  String
import sys

rospy.init_node("map_mux_select")
#该参数设置为false时，mux选择gmapping输出的map话题作为输入
#，反之选择map_server发布的map话题作为输入
rospy.set_param("switch_map_server",False)      

rospy.loginfo('waitting to connected to mux select service')
try:
    rospy.wait_for_service('mux/select',5)
except rospy.exceptions.ROSException:
    rospy.logerr('failed to connected to mux select service')
    sys.exit()
mux_select = rospy.ServiceProxy('mux/select',MuxSelect)
rospy.loginfo('Connected to mux select service.')

while True:
    if rospy.get_param('switch_map_server') == True:
        rospy.loginfo('switch_map_server: ' + str(True))
        #map_server 发布'static_map' gmapping 发布 ‘dynamic_map’ ， 默认选择dynamic_map
        mux_select('static_map')
        break
    else:
        rospy.loginfo('switch_map_server: ' + str(False))

rospy.loginfo('node exit')


