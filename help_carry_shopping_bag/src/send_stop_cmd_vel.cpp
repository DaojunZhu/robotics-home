#include <ros/ros.h>
#include <geometry_msgs/Twist.h>

int main(int argc,char **argv)
{
    ros::init(argc,argv,"send_stop_cmd_vel_node");
    ros::NodeHandle nh;
    ros::Rate loop_rate(10);
    ros::Publisher pub = nh.advertise<geometry_msgs::Twist>("stop_cmd_vel",1);
    ROS_INFO("start sending stopping velocity to the robot....");
    while(ros::ok())
    {
        geometry_msgs::Twist vel;
        pub.publish(vel);
        loop_rate.sleep();
    }

    return 0;
}