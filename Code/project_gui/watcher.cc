#include <chrono>
#include <iostream>
#include <set>
#include <string>
#include <gazebo/msgs/msgs.hh>
#include <gazebo/util/IntrospectionClient.hh>
#include <ignition/transport.hh>

/////////////////////////////////////////////////
void cb(const gazebo::msgs::Param_V &_msg)
{
  std::cout << _msg.DebugString() << std::endl;
}

//////////////////////////////////////////////////
int main(int argc, char **argv)
{
  // Use the introspection service for finding the "sim_time" and "counter"
  // items.
  gazebo::util::IntrospectionClient client;

  // Wait for the managers to come online.
  std::set<std::string> managerIds = client.WaitForManagers(
      std::chrono::seconds(2));

  if (managerIds.empty())
  {
    std::cerr << "No introspection managers detected." << std::endl;
    std::cerr << "Is a gzserver running?" << std::endl;
    return -1;
  }

  // Pick up the first manager.
  std::string managerId = *managerIds.begin();

  // sim_time is a pre-registered item with the following URI format:
  // data://world/<world_name>?p=<variable_type>/<variable_name>
  std::string simTime = "data://world/default?p=time/sim_time";
  std::string counter = "data://my_plugin/move";

  // Check if "sim_time" is registered.
  if (!client.IsRegistered(managerId, simTime))
  {
    std::cerr << "The sim_time item is not registered on the manager.\n";
    return -1;
  }

  // Check if "counter" is registered.
  if (!client.IsRegistered(managerId, counter))
  {
    std::cerr << "The move item is not registered on the manager.\n";
    return -1;
  }

  // The variables to watch are registered with the manager

  // Create a filter for watching the items.
  std::string filterId, topic;
  if (!client.NewFilter(managerId, {simTime, counter}, filterId, topic))
    return -1;

  // Let's subscribe to the topic for receiving updates.
  ignition::transport::Node node;
  node.Subscribe(topic, cb);

  // zZZZ.
  ignition::transport::waitForShutdown();

  return 0;
}
