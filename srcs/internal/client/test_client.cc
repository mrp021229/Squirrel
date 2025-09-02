#include <cassert>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <unistd.h>
#include <vector>
#include "client.h"
#include "yaml-cpp/yaml.h"

// 读取 SQL 文件的每一行
std::vector<std::string> read_sql_file(const std::string &filename) {
    std::vector<std::string> sqls;
    std::ifstream infile(filename);
    std::string line;
    while (std::getline(infile, line)) {
        if (!line.empty()) {
            sqls.push_back(line);
        }
    }
    return sqls;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <config.yml> <crash_sql.txt>" << std::endl;
        return 1;
    }

    YAML::Node config = YAML::LoadFile(std::string(argv[1]));
    std::string db_name = config["db"].as<std::string>();
    std::string startup_cmd = config["startup_cmd"].as<std::string>();
    std::string crash_file = argv[2];

    // 重定向 stdout 和 stderr 到 log 文件
    freopen("execution_log.txt", "w", stdout);
    freopen("execution_log.txt", "a", stderr); // 追加模式

    client::DBClient *test_client = client::create_client(db_name, config);
    test_client->initialize(config);
    if (!test_client->check_alive()) {
        system(startup_cmd.c_str());
        sleep(5);
    }

    test_client->prepare_env();
    std::vector<std::string> sqls = read_sql_file(crash_file);

    for (const std::string &sql : sqls) {
        try {
            test_client->execute(sql.c_str(), sql.size());
        } catch (const std::exception &e) {
            std::cerr << e.what() << std::endl;
        } catch (...) {
            std::cerr << "Unknown error" << std::endl;
        }
    }

    test_client->clean_up_env();
    return 0;
}
