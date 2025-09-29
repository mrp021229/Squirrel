// g++ -std=c++17 -O2 -I/usr/include -L/usr/lib -lclickhouse-cpp-lib -lpthread -o ch_dump ch_dump.cpp
// 根据你的安装路径调整 -I/-L 与 -l 名称（常见为 -lclickhouse-cpp-lib 或 -lclickhouse-cpp-client）
//
// 功能：
// 1) exec_sql：执行任意 SQL，失败时打印错误
// 2) dump_schema_to_file：将当前数据库下所有表及其列名写入指定文件

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <stdexcept>

#include <clickhouse/client.h>

using namespace clickhouse;

// 执行任意 SQL（不关心返回结果）
static int exec_sql(Client& client, const std::string& sql) {
    try {
        client.Execute(sql);
        return 0;
    } catch (const std::exception& e) {
        std::fprintf(stderr, "[exec_sql] error: %s\n", e.what());
        return -1;
    }
}

// 将当前数据库下所有用户表及其列名导出到文件
int dump_schema_to_file(Client& client, const char* path) {
    FILE* fp = std::fopen(path, "w");
    if (!fp) {
        std::perror("fopen");
        return -1;
    }

    // 1) 获取当前库下的所有表名（排除非当前库）
    //    你也可以在 WHERE 中加更多过滤（如排除视图等），这里保持与原功能接近：把“表”（包括 MergeTree/Memory 等）都列出来
    const std::string q_tables =
        "SELECT name "
        "FROM system.tables "
        "WHERE database = currentDatabase() "
        "ORDER BY name";

    std::vector<std::string> table_names;
    try {
        client.Select(q_tables, [&](const Block& block) {
            if (block.GetColumnCount() == 0) return;
            auto col = block[0]->As<ColumnString>();
            size_t rows = block.GetRowCount();
            for (size_t i = 0; i < rows; ++i) {
                auto sv = col->At(i);
                table_names.emplace_back(std::string(sv.data(), sv.size()));
            }
        });
    } catch (const std::exception& e) {
        std::fprintf(stderr, "query tables failed: %s\n", e.what());
        std::fclose(fp);
        return -2;
    }

    // 2) 对每张表查询列名并写入文件
    for (const auto& tname : table_names) {
        std::fprintf(fp, "Table: %s\n", tname.c_str());

        // 在 system.columns 中按 position 顺序输出列
        // 注意：这里使用字符串字面量拼接；tname 来源于 system 表，可信。
        std::string q_cols =
            "SELECT name "
            "FROM system.columns "
            "WHERE database = currentDatabase() AND table = '" + tname + "' "
            "ORDER BY position";

        try {
            client.Select(q_cols, [&](const Block& block) {
                if (block.GetColumnCount() == 0) return;
                auto col = block[0]->As<ColumnString>();
                size_t rows = block.GetRowCount();
                for (size_t i = 0; i < rows; ++i) {
                    auto sv = col->At(i);
                    std::string cname(sv.data(), sv.size());
                    std::fprintf(fp, "  Column: %s\n", cname.c_str());
                }
            });
        } catch (const std::exception& e) {
            std::fprintf(stderr, "prepare columns failed for %s: %s\n",
                         tname.c_str(), e.what());
            // 不中断，继续下一张表
        }

        std::fprintf(fp, "\n");
    }

    std::fclose(fp);
    return 0;
}

int main() {
    // 连接参数按需修改
    ClientOptions opts;
    opts.SetHost("127.0.0.1")
        .SetPort(9000)
        .SetDefaultDatabase("default");
        // 如需账号密码：
        // .SetUser("default")
        // .SetPassword("your_password");

    try {
        Client client(opts);

        // 示例：创建两张测试表（与原 SQLite 示例等价的字段）
        // ClickHouse 需要指定引擎；这里用 Memory，便于快速试跑
        exec_sql(client, "DROP TABLE IF EXISTS v258478");
        exec_sql(client, "DROP TABLE IF EXISTS v258484");

        exec_sql(client,
            "CREATE TABLE v258478 ("
            "  v258479 Int32,"
            "  v258480 String"
            ") ENGINE = Memory");

        exec_sql(client,
            "CREATE TABLE v258484 ("
            "  v258485 String,"
            "  v258486 Int32"
            ") ENGINE = Memory");

        // 导出 schema
        if (dump_schema_to_file(client, "/home/src/table.txt") == 0) {
            std::printf("Schema dumped to table.txt\n");
        } else {
            std::fprintf(stderr, "Schema dump failed\n");
        }

    } catch (const std::exception& e) {
        std::fprintf(stderr, "Cannot connect or operate: %s\n", e.what());
        return 1;
    }

    return 0;
}
