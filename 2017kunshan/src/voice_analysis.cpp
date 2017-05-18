#include "ros/ros.h"
#include "std_msgs/String.h"
#include  <algorithm>
//sound client
#include <sound_play/sound_play.h>

using namespace std;

std::vector<std::string> goods = {"coffee","milk","juice","sprite","water","biscuit","chips","redbull","roll","toothpaste","terminal","continue","follow","navigation"};
sound_play::SoundClient *sc;
ros::Publisher cmd_pub;
std::string lastvoice;
bool paused = true;


vector<string> split(string str,char delimiter)
{
    vector<string> internal;
    stringstream ss(str);
    string tok;

    while(getline(ss,tok,delimiter)){
        internal.push_back(tok);
    }
    
    return internal;
}

void callback(const std_msgs::String::ConstPtr& msg)
{
    std::string voice = msg->data;

    if(voice == "continue"){
    	paused = false;
    	sc->say("I will continue listening");
    	return;
    }
    if(paused)
    	return;
    if(voice == "yes"){
        if(lastvoice != ""){
            sc->say("I get it");
            cout << "I get it : " << lastvoice << endl;
            std_msgs::String cmd;
            cmd.data = lastvoice;
            cmd_pub.publish(cmd);  
            lastvoice = "";
            paused = true;
        }
        else{
            sc->say("yes for what ?");
        }
        return;
    }
    else if(voice == "no"){
        sc->say("please say again");
        lastvoice = "";
        return;
    }

    vector<string> voice_tok = split(voice,' ');
    auto result = std::find_first_of(goods.begin(),goods.end(),voice_tok.begin(),voice_tok.end());
    if(result == goods.end()){
        sc->say("sorry, I can't understand you, please say again");
    }else{
        string good = *result;
        lastvoice = good;
        char message[20];
        sprintf(message,"do you mean %s",good.c_str());
        sc->say(message);
    }
    
}

int main(int argc, char **argv)
{
    ros::init(argc,argv,"voice_analysis_node");
    ros::NodeHandle nh;
    ros::Subscriber voice_sub = nh.subscribe("recognizer/output",1,callback);
    cmd_pub = nh.advertise<std_msgs::String>("voice_cmd",1);
    sc = new sound_play::SoundClient();
	ROS_INFO("===============voice analysis node=========================");
    ROS_INFO("node initialized.");
    
    ros::spin();
    
    return 0;
}
