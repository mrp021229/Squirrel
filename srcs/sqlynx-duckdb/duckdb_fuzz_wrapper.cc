#define _POSIX_C_SOURCE 200809L
#include <duckdb.hpp>
#include <unistd.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fstream>
#include <iostream>
#include <chrono>

// AFL++ 手动持久化接口
// extern "C" {
//   void __AFL_INIT(void);
//   int __AFL_LOOP(unsigned int);
// }

#define MAX_IN (1 << 20)  // 1MB 输入上限

using namespace duckdb;

// ------------------------------------------------------------
// 全局日志句柄
std::ofstream sql_file;

// ------------------------------------------------------------
// 重置数据库文件并重新打开连接
void reset_db(std::unique_ptr<DuckDB> &db, std::unique_ptr<Connection> &conn) {
  unlink("test.duckdb");
  db = std::make_unique<DuckDB>("test.duckdb");
  conn = std::make_unique<Connection>(*db);
}

// ------------------------------------------------------------
// 导出表结构到文件（table_column_list.txt）
int dump_schema_to_file(Connection &conn, const std::string &path) {
  std::ofstream out(path);
  if (!out.is_open()) {
    perror("fopen");
    return -1;
  }

  auto result = conn.Query(
      "SELECT table_name FROM information_schema.tables "
      "WHERE table_schema = 'main' AND table_type = 'BASE TABLE' "
      "ORDER BY table_name");

  if (!result || result->HasError()) return -2;

  for (size_t i = 0; i < result->RowCount(); ++i) {
    std::string tname = result->GetValue(0, i).ToString();
    out << "Table: " << tname << "\n";

    auto col_result = conn.Query("PRAGMA table_info(" + tname + ");");
    if (!col_result || col_result->HasError()) continue;

    for (size_t j = 0; j < col_result->RowCount(); ++j) {
      std::string cname = col_result->GetValue(1, j).ToString();
      out << "  Column: " << cname << "\n";
    }
    out << "\n";
  }

  out.close();
  return 0;
}

// ------------------------------------------------------------
// 打开日志文件并递增 index
void open_log_files_from_local_index() {
  const std::string index_path = "/home/Squirrel/srcs/sqlynx-duckdb/index.txt";
  int index = 0;

  {
    std::ifstream index_file(index_path);
    if (index_file.is_open()) {
      index_file >> index;
      index_file.close();
    }
  }

  std::string sql_filename = "/home/output/sql_log_" + std::to_string(index) + ".txt";

  if (sql_file.is_open()) sql_file.close();
  sql_file.open(sql_filename, std::ios::app);

  {
    std::ofstream index_file(index_path, std::ios::trunc);
    if (index_file.is_open()) {
      index_file << (index + 1);
      index_file.close();
    }
  }
}

// ------------------------------------------------------------
// 主函数
int main() {
  __AFL_INIT();

  // 预分配输入缓冲
  static unsigned char buf[MAX_IN + 1];
  unsigned long long iters = 0;

  // 初始化数据库连接
  std::unique_ptr<DuckDB> db;
  std::unique_ptr<Connection> conn;
  reset_db(db, conn);

  // 打开 SQL 日志
  open_log_files_from_local_index();

  // 开始持久化主循环
  while (__AFL_LOOP(100000000)) {
    ssize_t len = read(STDIN_FILENO, buf, MAX_IN);
    if (len <= 0) continue;
    if (len == 1 && buf[0] == '0') continue;

    buf[len] = '\0';
    ++iters;

    // 执行 SQL
    std::string sql((char*)buf);
    auto result = conn->Query(sql);

    // 每轮导出 schema
    dump_schema_to_file(*conn, "/home/table_column_list.txt");

    // 写入 SQL 日志
    if (sql_file.is_open()) {
      sql_file.write(sql.c_str(), len);
      sql_file << "\n";
      sql_file.flush();
    }

    // 每 2000 条重置数据库
    if (iters == 2000) {
      iters = 0;
      reset_db(db, conn);
      std::ofstream ofs("/home/table_column_list.txt", std::ofstream::trunc);
      ofs.close();

      if (sql_file.is_open()) {
        sql_file << "New database\n";
        sql_file.flush();
      }
    }
  }

  // 清理资源
  sql_file.close();
  std::ofstream ofs("/home/table_column_list.txt", std::ofstream::trunc);
  ofs.close();
  return 0;
}
