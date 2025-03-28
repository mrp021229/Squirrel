#include "client_postgresql.h"

#include <unistd.h>
#include <fstream>
#include <ctime>
#include <cstring>
#include <deque>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>

#include "absl/strings/str_format.h"
#include "client.h"
#include "libpq-fe.h"

using namespace std;
namespace {
PGconn *create_connection(std::string_view db_name) {
  std::string conninfo =
      absl::StrFormat("hostaddr=%s port=%d dbname=%s connect_timeout=4",
                      "127.0.0.1", 5432, db_name);

  std::cerr << "Connection info: " << conninfo << std::endl;
  PGconn *result = PQconnectdb(conninfo.c_str());
  if (PQstatus(result) == CONNECTION_BAD) {
    fprintf(stderr, "Error1: %s\n", PQerrorMessage(result));
    std::cerr << "BAd" << std::endl;
  }
  return result;
}

void reset_database(PGconn *conn) {
  auto res = PQexec(conn, "DROP SCHEMA public CASCADE; CREATE SCHEMA public;");
  PQclear(res);
}
};  // namespace

namespace client {

void PostgreSQLClient::initialize(YAML::Node config) {
  host_ = config["host"].as<std::string>();
  port_ = config["port"].as<std::string>();
  user_name_ = config["user_name"].as<std::string>();
  passwd_ = config["passwd"].as<std::string>();
  db_name_ = config["db_name"].as<std::string>();
  std::cerr << "Sock path: " << sock_path_ << std::endl;
}

void PostgreSQLClient::prepare_env() {
  PGconn *conn = create_connection(db_name_);
  reset_database(conn);
  PQfinish(conn);
}

ExecutionStatus PostgreSQLClient::execute(const char *query, size_t size) {
  auto conn = create_connection(db_name_);

  if (PQstatus(conn) != CONNECTION_OK) {
    fprintf(stderr, "Error2: %s\n", PQerrorMessage(conn));
    PQfinish(conn);
    return kServerCrash;
  }

  std::string cmd(query, size);

  auto res = PQexec(conn, cmd.c_str());
  if (PQstatus(conn) != CONNECTION_OK) {
    fprintf(stderr, "Error3: %s\n", PQerrorMessage(conn));
    PQclear(res);
    return kServerCrash;
  }

  if (PQresultStatus(res) != PGRES_COMMAND_OK &&
      PQresultStatus(res) != PGRES_TUPLES_OK) {
    fprintf(stderr, "Error4: %s\n", PQerrorMessage(conn));
    PQclear(res);
    PQfinish(conn);
    return kExecuteError;
  }

  // 获取当前数据库的所有表
  PGresult *table_list_res = PQexec(conn, 
    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';");

if (PQresultStatus(table_list_res) != PGRES_TUPLES_OK) {
  fprintf(stderr, "Error fetching table list: %s\n", PQerrorMessage(conn));
} else {
  // 打开或创建文本文件用于保存表和列信息
  std::ofstream table_list_file;
  table_list_file.open("/home/table_column_list.txt", std::ios::app); // 以追加模式打开文件

  if (table_list_file.is_open()) {
    // 获取当前时间戳，作为文件内容的标识
    std::time_t current_time = std::time(nullptr);
    table_list_file << "Table and Column list for database: " << db_name_ 
                    << " at " << std::ctime(&current_time) << std::endl;

    // 遍历所有表
    int rows = PQntuples(table_list_res);
    for (int i = 0; i < rows; ++i) {
      const char *table_name = PQgetvalue(table_list_res, i, 0);
      table_list_file << "Table: " << table_name << std::endl;

      // 查询当前表的所有列名
      std::string column_query = "SELECT column_name FROM information_schema.columns "
                                 "WHERE table_schema = 'public' AND table_name = '" + std::string(table_name) + "';";
      
      PGresult *column_list_res = PQexec(conn, column_query.c_str());
      if (PQresultStatus(column_list_res) != PGRES_TUPLES_OK) {
        fprintf(stderr, "Error fetching columns for table %s: %s\n", table_name, PQerrorMessage(conn));
      } else {
        int col_rows = PQntuples(column_list_res);
        for (int j = 0; j < col_rows; ++j) {
          const char *column_name = PQgetvalue(column_list_res, j, 0);
          table_list_file << "  Column: " << column_name << std::endl;
        }
      }

      // 释放列查询结果
      PQclear(column_list_res);
      table_list_file << std::endl;  // 为下一张表留空行
    }

    table_list_file << std::endl; // 为下一次追加留空行
    table_list_file.close(); // 关闭文件
  } else {
    fprintf(stderr, "Error opening file to save table and column list\n");
  }
}

  PQclear(res);
  PQfinish(conn);
  return kNormal;
}

void PostgreSQLClient::clean_up_env() {}

bool PostgreSQLClient::check_alive() {
  std::string conninfo = absl::StrFormat(
      "hostaddr=%s port=%d connect_timeout=4", "127.0.0.1", 5432);
  PGPing res = PQping(conninfo.c_str());
  return res == PQPING_OK;
}
}  // namespace client
