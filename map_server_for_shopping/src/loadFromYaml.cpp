#include <stdio.h>
#include <stdlib.h>
#include <libgen.h>
#include <fstream>

#include "ros/ros.h"
#include "ros/console.h"
#include "map_server/image_loader.h"
#include "nav_msgs/MapMetaData.h"
#include "yaml-cpp/yaml.h"

#include "nav_msgs/SetMap.h"

#ifdef HAVE_YAMLCPP_GT_0_5_0
// The >> operator disappeared in yaml-cpp 0.5, so this function is
// added to provide support for code written under the yaml-cpp 0.3 API.
template<typename T>
void operator >> (const YAML::Node& node, T& i)
{
  i = node.as<T>();
}
#endif

class LoadMapFromYaml
{
public:
    LoadMapFromYaml(const std::string fname)
    {
        std::string mapfname = "";
        double origin[3];
        double res;
        int negate;
        double occ_th, free_th;
        MapMode mode = TRINARY;
        std::string frame_id;
        ros::NodeHandle private_nh("~");
        private_nh.param("frame_id", frame_id, std::string("map"));
        //mapfname = fname + ".pgm";
        //std::ifstream fin((fname + ".yaml").c_str());
        std::ifstream fin(fname.c_str());
        if (fin.fail()) {
          ROS_ERROR("Map_server could not open %s.", fname.c_str());
          exit(-1);
        }
#ifdef HAVE_YAMLCPP_GT_0_5_0
        // The document loading process changed in yaml-cpp 0.5.
        YAML::Node doc = YAML::Load(fin);
#else
        YAML::Parser parser(fin);
        YAML::Node doc;
        parser.GetNextDocument(doc);
#endif
        try {
          doc["resolution"] >> res;
        } catch (YAML::InvalidScalar) {
          ROS_ERROR("The map does not contain a resolution tag or it is invalid.");
          exit(-1);
        }
        try {
          doc["negate"] >> negate;
        } catch (YAML::InvalidScalar) {
          ROS_ERROR("The map does not contain a negate tag or it is invalid.");
          exit(-1);
        }
        try {
          doc["occupied_thresh"] >> occ_th;
        } catch (YAML::InvalidScalar) {
          ROS_ERROR("The map does not contain an occupied_thresh tag or it is invalid.");
          exit(-1);
        }
        try {
          doc["free_thresh"] >> free_th;
        } catch (YAML::InvalidScalar) {
          ROS_ERROR("The map does not contain a free_thresh tag or it is invalid.");
          exit(-1);
        }
        try {
          std::string modeS = "";
          doc["mode"] >> modeS;

          if(modeS=="trinary")
            mode = TRINARY;
          else if(modeS=="scale")
            mode = SCALE;
          else if(modeS=="raw")
            mode = RAW;
          else{
            ROS_ERROR("Invalid mode tag \"%s\".", modeS.c_str());
            exit(-1);
          }
        } catch (YAML::Exception) {
          ROS_DEBUG("The map does not contain a mode tag or it is invalid... assuming Trinary");
          mode = TRINARY;
        }
        try {
          doc["origin"][0] >> origin[0];
          doc["origin"][1] >> origin[1];
          doc["origin"][2] >> origin[2];
        } catch (YAML::InvalidScalar) {
          ROS_ERROR("The map does not contain an origin tag or it is invalid.");
          exit(-1);
        }
        try {
          doc["image"] >> mapfname;
          // TODO: make this path-handling more robust
          if(mapfname.size() == 0)
          {
            ROS_ERROR("The image tag cannot be an empty string.");
            exit(-1);
          }
          if(mapfname[0] != '/')
          {
            // dirname can modify what you pass it
            char* fname_copy = strdup(fname.c_str());
            mapfname = std::string(dirname(fname_copy)) + '/' + mapfname;
            free(fname_copy);
          }
        } catch (YAML::InvalidScalar) {
          ROS_ERROR("The map does not contain an image tag or it is invalid.");
          exit(-1);
        }

        ROS_INFO("Loading map from image \"%s\"", mapfname.c_str());
        map_server::loadMapFromFile(&map_resp_,mapfname.c_str(),res,negate,occ_th,free_th, origin, mode);
        map_resp_.map.info.map_load_time = ros::Time::now();
        map_resp_.map.header.frame_id = frame_id;
        map_resp_.map.header.stamp = ros::Time::now();
        ROS_INFO("Read a %d X %d map @ %.3lf m/cell",
        map_resp_.map.info.width,
        map_resp_.map.info.height,
        map_resp_.map.info.resolution);
        meta_data_message_ = map_resp_.map.info;
    }
    void getmap(nav_msgs::OccupancyGrid &map)
    {
        map = map_resp_.map;
    }
    void getmapinfo(nav_msgs::MapMetaData &mapinfo)
    {
        mapinfo = meta_data_message_;
    }
private:
    nav_msgs::MapMetaData meta_data_message_;
    nav_msgs::GetMap::Response map_resp_;
};

int main(int argc,char **argv)
{
    ros::init(argc,argv,"yamlToMap");
    ros::NodeHandle nh;
    ros::Publisher pub = nh.advertise<nav_msgs::OccupancyGrid>("map",1,true);
    LoadMapFromYaml obj("/home/ros/robocup/map/demo.yaml");
    nav_msgs::OccupancyGrid map;
    obj.getmap(map);
    pub.publish(map);
    std::cout << "publish map.." << std::endl;
    ros::spin();
    return 0;
}


