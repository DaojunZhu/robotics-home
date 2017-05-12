#! /usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Point
from geometry_msgs.msg import Quaternion


def debug():
    rospy.init_node('DEBUG')
    rospy.loginfo('start..')
    pub = rospy.Publisher('/move_base_simple/goal',PoseStamped,queue_size=1)
    position = Pose(Point(-5.698276,3.290836,0.000000 ),Quaternion(0.000000,0.000000,0.744343,0.667798))
    goal = PoseStamped()
    goal.header.frame_id = 'map'
    goal.header.stamp = rospy.Time.now()
    goal.pose = position
    pub.publish(goal)

debug()
