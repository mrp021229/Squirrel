#include <cassert>
#include <cstring>
#include <iostream>
#include <string>
#include <unistd.h>
#include "client.h"
#include "yaml-cpp/yaml.h"
int main(int argc, char **argv) {
  
  YAML::Node config = YAML::LoadFile(std::string(argv[1]));

  std::string db_name = config["db"].as<std::string>();
  // client::PostgreSQLClient *test_client = new client::PostgreSQLClient;
  std::string startup_cmd = config["startup_cmd"].as<std::string>();
  
  client::DBClient *test_client = client::create_client(db_name, config);
  test_client->initialize(config);
  if (!test_client->check_alive()) {
    system(startup_cmd.c_str());
    sleep(5);
  }
  // if (test_client->connect()) {
  //   std::cout << "Success!" << std::endl;
  // } else {
  //   std::cout << "Failed!" << std::endl;
  // }
  
  sleep(300);
  test_client->clean_up_env();
  return 0;
  const char *query = "create table v0(v1 int ,v2 int);";
  
  for (int i = 0; i < 10; ++i) {
    test_client->prepare_env();
    client::ExecutionStatus result = test_client->execute(query, strlen(query));
    std::cout << "Iteration " << i << ": result = " << result << std::endl;
    assert(result == client::kNormal);
    test_client->clean_up_env();
  }
}
