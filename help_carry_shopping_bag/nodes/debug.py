#! /usr/bin/env python

import rospy
from move_base_msgs.msg import MoveBaseActionResult

def debug():
    pub = rospy.Publisher('move_base/result',MoveBaseActionResult,queue_size=10)
    rospy.init_node('debug',anonymous=True)

    result = MoveBaseActionResult()
    result.status.status = 3
    pub.publish(result)
    rospy.loginfo('succeed sending ')


if __name__ == '__main__':
    debug()

