#include "ros/ros.h"
#include "sensor_msgs/Image.h"
#include <signal.h>
#include <fstream>


std::ofstream write_to_file;
int count = 0;
ros::Publisher image_pub ;

void callback(const sensor_msgs::Image::ConstPtr image_msg)
{
    ROS_INFO("record....");
    std::cout << "height" <<  image_msg->height << " " << "width" << image_msg->width << std::endl;
    std::cout << "step" << image_msg->step << std::endl;
    count ++;
    write_to_file << "=========" << count << "=================\n";
    // int i = 0;
    // for(; i < image_msg->data.size() ; i = i+ 3){
    //     //if(image_msg->data[i] != 128 && image_msg->data[i] !=0){
    //         //std::cout << i << " " << image_msg->data[i]  << std::endl;
    //         //break;
    //     //}
    //         //write_to_file << (unsigned short)image_msg->data[i]<< "  ";

        
    // }
    // std:: cout << "i " << i <<  std::endl;
    // int min_row,min_col,max_row,max_col;
    // bool min_row_flag = false;

    // for(int i=0; i<image_msg->width;i++)
    // {
    //     for(int j=0;j<image_msg->height * 3;j=j+3)
    //     {
    //         if(image_msg->data[i*768 + j] != 128 || image_msg->data[i*768 + j+1]!=0 || image_msg->data[i*768 + j + 2] != 0)
    //            {
    //                min_row_flag = true;
    //                break;
    //            }            
    //     }
    //     if(min_row_flag)
    //     {
    //         std:: cout << "min row: " << i << std::endl;
    //         break;   
    //     }

    //  }

    sensor_msgs::Image  img;
    img.header.frame_id = image_msg->header.frame_id;
    img.header.stamp = ros::Time::now();
    img.height = 50;
    img.width = 50 ;
    img.step = 150;
    img.encoding = image_msg->encoding;
    img.is_bigendian = image_msg->is_bigendian;

    img.data.resize(50*150);

    for(int i=0; i<50;i++){
        for(int j=0;j<50*3;j=j+3){
            img.data[i*150+j]=image_msg->data[(110+i)*768+110+j];
            img.data[i*150+j+1]=image_msg->data[(110+i)*768+110+j+1];
            img.data[i*150+j+2]=image_msg->data[(110+i)*768+110+j+2];
            // img.data[i*150+j]=image_msg->data[i*768+j];
            // img.data[i*150+j+1]=image_msg->data[i*768+j+1];
            // img.data[i*150+j+2]=image_msg->data[i*768+j+2];
        }
        
    }

    image_pub.publish(img);

    write_to_file << "===========================================\n";
    ROS_INFO("end.....");
}

void mySigintHandle(int sig)
{

    ROS_INFO("call ros::shutdown()");
    write_to_file.close();
    ROS_INFO("close file");
    ros::shutdown();
}

int main(int argc,char **argv)
{
    ros::init(argc,argv,"bag_image_data_record");
    ros::NodeHandle nh;

    signal(SIGINT,mySigintHandle);
    ros::Subscriber image_sub = nh.subscribe("ibeo_map/scan_matcher/rviz_grid",10000,&callback);
    image_pub = nh.advertise<sensor_msgs::Image>("new_image",50);
    ROS_INFO("open file");
    write_to_file.open("image_data.txt");
    write_to_file << "open file\n"; 
    ROS_INFO("node initialized");
    ros::spin();

    return 0;
}