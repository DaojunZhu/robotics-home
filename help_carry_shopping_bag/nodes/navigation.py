#! /usr/bin/env python
#! coding=utf-8

import rospy
from std_msgs.msg import String
from std_msgs.msg import Int16
import actionlib
import actionlib_msgs.msg
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal, MoveBaseResult
from geometry_msgs.msg import Pose,Point,Quaternion
from nav_msgs.msg import Odometry
from sound_play.libsoundplay import SoundClient
import tf
from std_srvs.srv import Empty


class Navigation():
    def __init__(self):
        rospy.init_node('nav_go_and_back')
        rospy.on_shutdown(self.cleanup)

        self.goals={
            'kitchen' : Pose(Point(-5.698276,3.290836,0.000000 ),Quaternion(0.000000,0.000000,0.744343,0.667798)),
            'bedroom' : Pose(Point(-10.218601,-3.692067,0.000000),Quaternion(0.000000,0.000000,-0.686431,0.727195)),
            'livingroom' : Pose(Point(-4.656111,-2.341600,0.000000),Quaternion(0.000000,0.000000,0.746823,0.665023)),
            'dinningroom' : Pose(Point(-9.157221,3.012569,0.000000),Quaternion(0.000000,0.000000,0.812395,0.583108)),
            #'dinningroom' : Pose(Point(-11.898957,2.615039,0.000000),Quaternion(0.000000,0.000000,0.828396,0.560144))
        }
        #the coordinate of the exit
        self.exit = Pose(Point(43.783617,17.165935,0.000000),Quaternion(0.000000,0.000000,0.994197,-0.107573))

        #create the sound client object
        self.soundclient = SoundClient()

        #create the tf transform listener object
        self.tflistener = tf.TransformListener()

        #set the sound voice
        self.voice  = 'voice_rab_diphone'

        #wait a moment to let the sound client to connect to the sound_play server
        rospy.sleep(1)

        #pause speech
        self.paused = True

        self.car_pose = Pose()
        self.cur_pose = Pose()

        self.actionCarPose = MoveBaseGoal()

        self.actionGoals = list()

        for (name,pose) in self.goals.iteritems():
            actionGoal = MoveBaseGoal()
            #actionGoal.target_pose.header.stamp = rospy.Time.now()
            actionGoal.target_pose.header.frame_id = 'map'
            actionGoal.target_pose.pose = pose
            self.actionGoals.append(actionGoal)
	
	for elem in self.actionGoals:
		rospy.loginfo(elem.target_pose.pose.position.x)


        
        self.goal = MoveBaseGoal()


        #subscriber from voice_commands
        self.voice_cmd_sub = rospy.Subscriber('voice_command',String,self.voice_to_nav)

         #subscriber from Odometry
        self.odom_sub = rospy.Subscriber('odom',Odometry,self.get_cur_pose)

        #subscriber from challenge timeout flag
        self.timeout_flag_sub = rospy.Subscriber('challenge_time_over_flag',Int16,self.timeout_callback)


        self.move_base_client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        connected_befor_timeout = self.move_base_client.wait_for_server(rospy.Duration(2.0))
        if connected_befor_timeout:
            rospy.loginfo('succeeded connecting to move_base server')
        else:
            rospy.logerr('failed connecting to move_base server')
            return

        rospy.wait_for_service('move_base/clear_costmaps',5.0)
        self.service_clear_costmap_client = rospy.ServiceProxy('move_base/clear_costmaps',Empty)
  
        rospy.loginfo('node initialized...')
    
    def cleanup(self):
        pass

    def timeout_callback(self,msg):
        if msg.data == 30:
            self.move_base_client.cancel_goal()
            rospy.loginfo('the challenge time is over , I will leave..' )
            self.soundclient.say('sorry, I donnot have enough time to continue, I will leave')
            goal = MoveBaseGoal()
            goal.target_pose.header.frame_id = 'map'
            goal.target_pose.header.stamp = rospy.Time.now()
            goal.target_pose.pose = self.exit
            self.move_base_client.send_goal(goal)
        else:
            pass

    
    #remember the car position
    def get_cur_pose(self,msg):
        self.cur_pose = msg.pose.pose

    def voice_to_nav(self,msg):
        if msg.data == 'pause':
            self.paused = True
            rospy.loginfo('I will pause listening...')
        elif msg.data == 'continue':
            rospy.loginfo('I will listening...')
            self.soundclient.say('I will listening...',self.voice)
            self.paused = False

        if self.paused:
            return 

        if msg.data == 'car':
            self.tflistener.waitForTransform('/map','/base_footprint',rospy.Time(),rospy.Duration(4.0))
            try:
                (trans,rot) = self.tflistener.lookupTransform('/map','/base_footprint',rospy.Time(0))
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                rospy.logerr('Error occure when remember the car position.')
                return 
            '''
            self.car_pose.position.x = self.cur_pose.position.x + trans[0]
            self.car_pose.position.y = self.cur_pose.position.y + trans[1]
            self.car_pose.position.z = self.cur_pose.position.z + trans[2]
            self.car_pose.orientation.x = self.cur_pose.orientation.x + rot[0]
            self.car_pose.orientation.y = self.cur_pose.orientation.y + rot[1]
            self.car_pose.orientation.z = self.cur_pose.orientation.z + rot[2]
            self.car_pose.orientation.w = self.cur_pose.orientation.w + rot[3]
            rospy.loginfo('I remember it.')
            self.soundclient.say('I remember it.',self.voice)
            self.actionCarPose = MoveBaseGoal()
            self.actionCarPose.target_pose.header.stamp = rospy.Time.now()
            self.actionCarPose.target_pose.header.frame_id = 'map'
            self.actionCarPose.target_pose.pose = self.car_pose
            '''
            self.car_pose.position.x = trans[0]
            self.car_pose.position.y = trans[1]
            self.car_pose.position.z = trans[2]
            self.car_pose.orientation.x = rot[0]
            self.car_pose.orientation.y = rot[1]
            self.car_pose.orientation.z = rot[2]
            self.car_pose.orientation.w = rot[3]
            rospy.loginfo('I remember the car position')
            self.soundclient.say('I remember it',self.voice)
            self.actionCarPose = MoveBaseGoal()
            self.actionCarPose.target_pose.header.frame_id = 'map'
            self.actionCarPose.target_pose.pose = self.car_pose
        elif msg.data == 'kitchen':
            rospy.loginfo('I will go to the kitchen...')
            self.soundclient.say('I will go to the kitchen',self.voice)
            self.paused = True
            self.goal = self.actionGoals[3]
	    self.goal.target_pose.header.stamp = rospy.Time.now()					
            self.move_base_client.send_goal(self.goal,done_cb=self.go_done_cb)
            self.move_base_client.wait_for_result()
        elif msg.data == 'bedroom':
            rospy.loginfo('I will go to the bedroom...')
            self.soundclient.say('I will go to the bedroom',self.voice)
            self.paused = True
            self.goal = self.actionGoals[1]
	    self.goal.target_pose.header.stamp = rospy.Time.now()
            self.move_base_client.send_goal(self.goal,done_cb=self.go_done_cb) 
            self.move_base_client.wait_for_result()
        elif msg.data == 'livingroom':
            rospy.loginfo('I will go to the living room...')
            self.soundclient.say('I will go to the living room',self.voice)
            self.paused = True
            self.goal = self.actionGoals[2]
	    self.goal.target_pose.header.stamp = rospy.Time.now()
            self.move_base_client.send_goal(self.goal,done_cb=self.go_done_cb)   
            self.move_base_client.wait_for_result() 
        else:
            return       
            
    def go_done_cb(self,state,result):
        #go succeeded
        if state == 3:
            rospy.loginfo('I success getting to goal pose')
            self.soundclient.say('I success getting to goal pose',self.voice)
            #stay for a moment befor back
            rospy.sleep(10)
            rospy.loginfo('I will back')
            self.soundclient.say('I will back',self.voice)
            self.move_base_client.send_goal(self.actionCarPose,done_cb=self.back_done_cb)
            self.move_base_client.wait_for_result()
            rospy.loginfo('Debug message : 1')
        #go failed
        else:   
            rospy.loginfo('I fail on the way, I will restart going to the goal...')
            self.soundclient.say('I failed on the way, I will replanning',self.voice)
            self.soundclient.say('clear costmaps',self.voice)
            self.service_clear_costmap_client()
            self.move_base_client.send_goal(self.goal,done_cb=self.go_done_cb)
            self.move_base_client.wait_for_result()

    def back_done_cb(self,state,result):
        #back succeeded
        rospy.loginfo('back_done_cb called...')
        if state == 3:
            rospy.loginfo('back nav state : %d '%state)
            rospy.loginfo('I success backing to the car pose')
            self.soundclient.say('sir, I have succeeded',self.voice)
        #back failed
        else:
            rospy.loginfo('I fail on the way, I will restart backing to the car....')
            self.soundclient.say('I failed on the way, I will replanning',self.voice)
            self.soundclient.say('clear costmaps',self.voice)
            self.service_clear_costmap_client()
            self.move_base_client.send_goal(self.actionCarPose,done_cb=self.back_done_cb)
            self.move_base_client.wait_for_result()


if __name__ == '__main__':
    try:
      Navigation()
      rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("Talkback node terminated.")        

        
