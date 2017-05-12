#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped 
from move_base_msgs.msg import MoveBaseActionResult 
import tf 
import tf2_ros
from sound_play.libsoundplay import SoundClient
import sys

class TalkBack:
    def __init__(self, script_path):
        rospy.init_node('car_help')

        rospy.on_shutdown(self.cleanup)

	self.rate = rospy.get_param("~rate", 5)
        r = rospy.Rate(self.rate)
        
        # Set the default TTS voice to use
        self.voice = rospy.get_param("~voice", "voice_don_diphone")
        
        # Set the wave file path if used
        #self.wavepath = rospy.get_param("~wavepath", script_path + "/../sounds")
        
        # Create the sound client object
        self.soundhandle = SoundClient()
        
        # Wait a moment to let the client connect to the
        # sound_play server
        rospy.sleep(1)
        
        # Make sure any lingering sound_play processes are stopped.
        self.soundhandle.stopAll()
        
        # Announce that we are ready for input
        #self.soundhandle.playWave(self.wavepath + "/R2D2a.wav")
        rospy.sleep(1)
        self.soundhandle.say("Ready", self.voice)
        
        rospy.loginfo("Say one of the navigation commands...")

	#self.voice_vel_pub = rospy.Publisher('address', String, queue_size=5)
        rospy.Subscriber('/recognizer/output', String, self.talkback)
        self.pub1 = rospy.Publisher('voice_command', String, queue_size=5)
	
	##############
	#self.exit_point = PoseStamped()
	####
	#rospy.Subscriber('/move_base/result', MoveBaseActionResult, self.base_status_callback)
	####
	
				    
	self.keywords_to_command1 = {'kitchen':['bring it to the kitchen','bring'],
				     'diningroom':['take it to the dinning room','take'],
				     'livingroom':['carry it to the living room','carry'],
				     'bedroom':['get it to the bedroom','get'],
				     'car':['car','this is the car','car position','position','this is the car position'],
				     'continue':['continue','continue speech'],
				     'follow':['follow','follow me','start','start follow']}
				    
	self.keywords_to_command2 = {'yes':['yes','Yes.','right'],
				     'no':['no','No.']}



	self.c1 = ' '



                     
    def get_command1(self, data):
        # Attempt to match the recognized word or phrase to the 
        # keywords_to_command dictionary and return the appropriate
	for (command1, keywords) in self.keywords_to_command1.iteritems():        
	    for word in keywords:
                if data.find(word) > -1:
                     return command1

    def get_command2(self, data):
        # Attempt to match the recognized word or phrase to the 
        # keywords_to_command dictionary and return the appropriate
	for (command2, keywords) in self.keywords_to_command2.iteritems():        
	    for word in keywords:
                if data.find(word) > -1:
                     return command2



                     
                     
    def talkback(self, msg):
        command1 = self.get_command1(msg.data)
	command2 = self.get_command2(msg.data)

	if command1 == 'kitchen':
	    self.soundhandle.say('Do you need me go to the kitchen?')
	    self.c1 = ('kitchen')

	if command1 == 'diningroom':
	    self.c1 = ('diningroom')
	    self.soundhandle.say('Do you need me go to the diningroom?')

	if command1 == 'livingroom':
	    self.soundhandle.say('Do you need me go to the livingroom?')
	    self.c1 = ('livingroom')

	if command1 == 'bedroom':
	    self.soundhandle.say('Do you need me go to the bedroom?')
	    self.c1 = ('bedroom')


	if command1 == 'car':
	    self.pub1.publish('car')

	if command1 == 'continue':
	    self.pub1.publish('continue')

	if command1 == 'follow':
	    self.pub1.publish('follow')


	###
	if command2 == 'yes':
	    self.soundhandle.say('OK. I will. ')
	    self.pub1.publish(self.c1)
	elif command2 == 'no': 
	    self.soundhandle.say("I don't understand. Please say again.")

	 

    def cleanup(self):
        self.soundhandle.stopAll()
        rospy.loginfo("Shutting down talkback node...")
 
       
if __name__=="__main__":
    try:
        TalkBack(sys.path[0])
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("Talkback node terminated.")
