1. 启动底盘(/home/ros/catkin_ws/base_controller/su_bringupHardware.launch)
2. 启动move_base 需要将move_base输出的话题cmd_vel 映射到  nav_cmd_vel  (home/ros/robocup/amcl_dwa.launch)  
3. 启动turtlebot_follow (home/ros/robocup/turtlebot_follow/follow.launch)
2. 启动help_carry.launch  (home/ros/robocup/help_carry_shopping_bag/help_carry.launch) 
3. 启动recognizer.launch (home/ros/robocup/help_carry_shopping_bag/recognizer.launch)

4. 

4. 给出机器人开始listenning的语音命令   "start listening"
5. 给出跟随命令												 "follow me"
6. 到达车所在的位置的时候，给出车位置的命令		"this is the car position"
7. 给出目的地位置命令												"take it to the kitchen"
8. 机器人返回之后，需要再次给出"start listenning" 命令，才能继续开始识别语音指令
