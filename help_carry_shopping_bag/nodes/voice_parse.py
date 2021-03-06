#! /usr/bin/env python

import rospy
from std_msgs.msg import String
from sound_play.libsoundplay import SoundClient

class VoiceParse:
	def __init__(self):
		rospy.init_node('voice_to_command')
		self.voice = 'voice_don_diphone'
		self.soundhandle = SoundClient()
		rospy.sleep(1)
		self.soundhandle.say("Ready", self.voice)
		rospy.loginfo("Say one of the navigation commands...")
		rospy.Subscriber('/recognizer/output', String, self.talkback)
		self.pub = rospy.Publisher('voice_command', String, queue_size=5)
		self.command  = String()
		self.verify = False
		rospy.loginfo("initialized....")

	def talkback(self,msg):
		rospy.loginfo(str(msg.data))
		data1 = msg.data.split()
		command = data1[0]
		rospy.loginfo(command)

		if command == 'continue':
			self.command = 'continue'
			self.pub.publish('continue')
			return
		elif msg.data.find('follow') > -1:
			self.command = 'follow'
			self.pub.publish('follow')
			return 
		elif msg.data.find('car') > -1:
			self.command = 'car'
			self.pub.publish('car')
			return

		if command == 'yes' or command == 'no':
			if command == 'yes':
				self.verify = True
			else:
				self.verify = False
				self.soundhandle.say('please try again')
		else:
			if command == 'take':
				self.command = 'kitchen'
				rospy.sleep(1)
				self.soundhandle.say('Do you need me go to the kitchen?')
			elif command == 'bring':
				self.command = 'bedroom'
				rospy.sleep(1)
				self.soundhandle.say('Do you need me go to the bedroom?')
			elif command == 'get':
				self.command = 'dinningroom'
				rospy.sleep(1)
				self.soundhandle.say('Do you need me go to the diningroom?')
			elif command == 'carry':
				self.command = 'livingroom'
				rospy.sleep(1)
				self.soundhandle.say('Do you need me go to the livingroom?')
			else:
				self.command = 'unknown'
				rospy.sleep(1)
				self.soundhandle.say("I don't understand. Please say again.")
		
		if self.command == 'kitchen' and self.verify :
			self.pub.publish('kitchen')
			self.verify = False
			#self.soundhandle.say('I will go to kitchen')
		elif self.command == 'bedroom' and self.verify :
			self.pub.publish('bedroom')
			self.verify = False
			#self.soundhandle.say('I will go to bedroom')
		elif self.command == 'dinningroom' and self.verify :
			self.pub.publish('dinningroom')
			self.verify = False
			#self.soundhandle.say('I will go to dinning room')
		elif self.command == 'livingroom' and self.verify:
			self.pub.publish('livingroom')
			self.verify = False
			#self.soundhandle.say('I will go to living room')

       
if __name__=="__main__":
    try:
        VoiceParse()
        rospy.spin()
    except :
        rospy.loginfo(" node terminated.")


		





