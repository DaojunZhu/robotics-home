#include "ros/ros.h"
#include <actionlib/client/simple_action_client.h>
#include <actionlib/client/terminal_state.h>
#include "utility/RotateRobotAction.h"


int main(int argc,char **argv)
{
    ros::init(argc,argv,"test_client");
    if(argc != 3){
	ROS_INFO("%d",argc);
	ROS_WARN("Usage: test_client <goal> <time_to_preempt_in_sec>");
	return 1;
	}

    actionlib::SimpleActionClient<utility::RotateRobotAction> ac("rotate_robot", true);
    
    ROS_INFO("Waiting for action server to start.");

    ac.waitForServer(); //will wait for infinite time

    utility::RotateRobotGoal goal;
    goal.target_angle = atof(argv[1]);

    ROS_INFO("Sending target angle [%f] and Preempt time of [%d]",goal.target_angle, atoi(argv[2]));
    ac.sendGoal(goal);

    ros::Duration(1).sleep();

    utility::RotateRobotGoal goal2;
    goal2.target_angle = 180;
    ac.sendGoal(goal2);

    return 0;
}