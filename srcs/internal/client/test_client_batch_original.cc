#include <cassert>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <unistd.h>
#include <vector>
#include <regex>
#include <map>
#include <filesystem>

#include "client.h"
#include "yaml-cpp/yaml.h"

namespace fs = std::filesystem;

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

// 将 stdout/stderr 重定向到指定路径（覆盖写）
void redirect_std_to_file(const std::string &log_path) {
    // 以写模式打开 stdout，随后以追加模式把 stderr 指到同一个文件
    FILE* f_out = freopen(log_path.c_str(), "w", stdout);
    if (!f_out) {
        std::cerr << "Failed to redirect stdout to " << log_path << std::endl;
    }
    FILE* f_err = freopen(log_path.c_str(), "a", stderr);
    if (!f_err) {
        // 尽量在原 stderr 上报告
        std::cerr << "Failed to redirect stderr to " << log_path << std::endl;
    }
}

// 处理单个 crash 文件：按照原逻辑执行一遍
void process_crash_file(const std::string& db_name,
                        const YAML::Node& config,
                        const std::string& startup_cmd,
                        const std::string& crash_file,
                        const std::string& log_path) {
    // 为本次文件处理设置独立日志
    redirect_std_to_file(log_path);

    // 初始化并检查/启动数据库
    client::DBClient *test_client = client::create_client(db_name, config);
    test_client->initialize(config);

    if (!test_client->check_alive()) {
        // 如未启动则拉起并等待
        system(startup_cmd.c_str());
        sleep(5);
    }

    // 准备环境，执行 SQL，清理环境
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
}

int main(int argc, char **argv) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <config.yml> <crash_dir>" << std::endl;
        return 1;
    }

    const std::string config_path = argv[1];
    const std::string crash_dir = argv[2];

    // 读取配置
    YAML::Node config = YAML::LoadFile(config_path);
    std::string db_name = config["db"].as<std::string>();
    std::string startup_cmd = config["startup_cmd"].as<std::string>();

    // 准备结果目录
    const fs::path result_dir = "/home/Squirrel/build/result-original";
    

    // 扫描 crash_dir，匹配 crash_(\d+)\.txt，并按编号排序
    std::regex pat(R"(crash_(\d+)\.txt)");
    std::map<int, fs::path> ordered_files; // 使用 map 按编号有序

    if (!fs::exists(crash_dir)) {
        std::cerr << "Crash directory does not exist: " << crash_dir << std::endl;
        return 1;
    }

    for (const auto &entry : fs::directory_iterator(crash_dir)) {
        if (!entry.is_regular_file()) continue;
        const std::string fname = entry.path().filename().string();
        std::smatch m;
        if (std::regex_match(fname, m, pat)) {
            // 提取编号
            int idx = std::stoi(m[1].str());
            ordered_files[idx] = entry.path();
        }
    }

    if (ordered_files.empty()) {
        std::cerr << "No files matching pattern crash_(x).txt found in " << crash_dir << std::endl;
        return 1;
    }

        // 逐个文件处理
    for (const auto& [idx, path] : ordered_files) {
        // 日志命名为 crash_x_log.txt
        fs::path log_path = result_dir / ("crash_" + std::to_string(idx) + "_log.txt");
        process_crash_file(db_name, config, startup_cmd, path.string(), log_path.string());

        // 每个文件处理完确保缓冲区落盘
        fflush(stdout);
        fflush(stderr);
    }


    return 0;
}
