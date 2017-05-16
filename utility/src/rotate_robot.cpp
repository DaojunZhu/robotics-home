#include "ros/ros.h"
#include "nav_msgs/Odometry.h"
#include "std_msgs/Float32.h"
#include "tf/tf.h"
#include "tf/tfMessage.h"
#include "geometry_msgs/Twist.h"
#include <tf/transform_listener.h>	//tf :: TransformListener
#include "actionlib/server/simple_action_server.h"
#include "utility/RotateRobotAction.h"

#define PI 3.14159

using namespace std;

double start_angle;           //起始角度
double target_angle;            //目标角度
double curr_angle;             //当前角度

tf::TransformListener *listener;	//  tf transform listener 
ros::Publisher vel_pub;

actionlib::SimpleActionServer<utility::RotateRobotAction> *as;
utility::RotateRobotFeedback feedback;
utility::RotateRobotResult result;

double get_odom_angle()
{
    tf::StampedTransform trans;
    try{
        listener->lookupTransform("odom","base_footprint",ros::Time(0),trans);
        tf::Quaternion quat = trans.getRotation();
        tf::Matrix3x3 quat_mat(quat);
        double yaw,pitch,roll;
        quat_mat.getEulerYPR(yaw,pitch,roll);
        return yaw*180/PI+180;
    }catch(...)
    {
        ROS_ERROR("tf error");
        return 1;
    }
}

void executeCB(const utility::RotateRobotGoalConstPtr &goal)
{
    if(!as->isActive() || as->isPreemptRequested())
        return;
    ROS_INFO("action server get client request, target angle: %f", goal->target_angle);
    
    start_angle = get_odom_angle();
    target_angle = goal->target_angle;
    curr_angle = start_angle;
    std::cout << "Start angle: " << start_angle << std::endl;
    geometry_msgs::Twist vel;      
    vel.angular.z = target_angle > 0 ? 0.5 : -0.5;
    ros::Rate rate(20);

    double condition = (start_angle+target_angle)<=360 ?  (curr_angle-start_angle-target_angle) : (start_angle+target_angle-curr_angle-360);

    while(abs(condition)>=0 ){      //允许误差范围为3度
        //Check for ROS
        if(!ros::ok()){
            as->setAborted(result,"I failed");
            ROS_INFO("action server shutdown.");
            vel_pub.publish(geometry_msgs::Twist());
            break;
        }

        if(!as->isActive() || as->isPreemptRequested()){
            vel_pub.publish(geometry_msgs::Twist());
            return;
        }

        
        if(abs(condition)<=1){
            ROS_INFO("target goal reached.target angle: %f",goal->target_angle);
            as->setSucceeded(result);
            vel_pub.publish(geometry_msgs::Twist());
        }else{
            //ROS_INFO("Setting to goal %f / %f",feedback.past_angle,goal->target_angle);
            feedback.past_angle = abs(curr_angle-start_angle);
            as->publishFeedback(feedback);
        }
        rate.sleep();
       
        vel_pub.publish(vel);
        curr_angle = get_odom_angle();
        condition = (start_angle+target_angle)<=360 ?  (curr_angle-start_angle-target_angle) : (start_angle+target_angle-curr_angle-360);
    }
}


void preemptCB()
{
    ROS_WARN("goal got preempted.");
    as->setPreempted();
}

int main(int argc,char **argv)
{
    ros::init(argc,argv,"rotate_robot");
    ros::NodeHandle nh;
    listener = new tf::TransformListener();
    // ros::Subscriber odom_sub = nh.subscribe("odom",1,odomcallback);
    vel_pub = nh.advertise<geometry_msgs::Twist>("cmd_vel",1);
    std::string node_name = ros::this_node::getName();
    as = new actionlib::SimpleActionServer<utility::RotateRobotAction>(nh,node_name,executeCB,false);
    as->registerPreemptCallback(preemptCB);
    as->start();
    ros::spin();
    return 0;

}