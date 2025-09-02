#include <cassert>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <unistd.h>
#include <vector>
#include "client.h"
#include "yaml-cpp/yaml.h"

// 读取 SQL 文件、忽略与上一行相同的“连续重复”语句，
// 并把去重后的结果写入 dedup_out_path（例如 new_crash.txt）
std::vector<std::string> read_sql_file(const std::string &filename,
                                       const std::string &dedup_out_path) {
    std::vector<std::string> sqls;

    std::ifstream infile(filename);
    if (!infile.is_open()) {
        std::cerr << "Failed to open input file: " << filename << std::endl;
        return sqls;
    }

    std::ofstream outfile(dedup_out_path, std::ios::trunc);
    if (!outfile.is_open()) {
        std::cerr << "Failed to open output file: " << dedup_out_path << std::endl;
        return sqls;
    }

    std::string line;
    std::string prev;       // 记录上一条被接受（写入/保存）的语句
    bool has_prev = false;

    while (std::getline(infile, line)) {
        if (line.empty()) {
            continue; // 跳过空行
        }
        if (has_prev && line == prev) {
            continue; // 与上一条相同则忽略
        }

        // 接受该行
        sqls.push_back(line);
        outfile << line << '\n';

        prev = line;
        has_prev = true;
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

    // 重定向 stdout 和 stderr 到日志文件
    FILE *log_fp = freopen("execution_log.txt", "w", stdout);
    if (!log_fp) {
        std::cerr << "Failed to redirect stdout to execution_log.txt" << std::endl;
    }
    FILE *err_fp = freopen("execution_log.txt", "a", stderr); // 追加模式
    if (!err_fp) {
        std::cerr << "Failed to redirect stderr to execution_log.txt" << std::endl;
    }

    client::DBClient *test_client = client::create_client(db_name, config);
    test_client->initialize(config);
    if (!test_client->check_alive()) {
        system(startup_cmd.c_str());
        sleep(5);
    }

    test_client->prepare_env();

    // 读取并去除“连续重复”，同时将结果写入 new_crash.txt
    std::vector<std::string> sqls = read_sql_file(crash_file, "new_crash.txt");

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
