#include "client_mysql.h"

#include <unistd.h>

#include <cstring>
#include <deque>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>

#include <fstream>   // 
#include <ctime>     // 

#include "mysql.h"
#include "mysqld_error.h"

using namespace std;
namespace {
bool is_crash_response(int response) {
  return response == CR_SERVER_LOST || response == CR_SERVER_GONE_ERROR;
}
};  // namespace

namespace client {

void MySQLClient::initialize(YAML::Node config) {
  host_ = config["host"].as<std::string>();
  user_name_ = config["user_name"].as<std::string>();
  passwd_ = config["passwd"].as<std::string>();
  sock_path_ = config["sock_path"].as<std::string>();
  db_prefix_ = config["db_prefix"].as<std::string>();
}

void MySQLClient::prepare_env() {
  ++database_id_;
  std::string database_name = db_prefix_ + std::to_string(database_id_);
  if (!create_database(database_name)) {
    std::cerr << "Failed to create database." << std::endl;
  }
}

ExecutionStatus MySQLClient::execute(const char *query, size_t size) {
  // Create a connection for executing the query
  // Check the response.
  // Return status accordingly.
  std::string database_name = db_prefix_ + std::to_string(database_id_);
  std::optional<MYSQL> connection = create_connection(database_name);
  if (!connection.has_value()) {
    std::cerr << "Cannot creat connection at execute " << std::endl;
    return kServerCrash;
  }

  int server_response = mysql_real_query(&(*connection), query, size);
  if (is_crash_response(server_response)) {
    std::cerr << "Cannot mySQL_QUERY " << std::endl;
    return kServerCrash;
  }
  ExecutionStatus server_status = clean_up_connection(*connection);
// ? 获取数据库中所有表和列信息
MYSQL_RES *tables_res = mysql_list_tables(&(*connection), nullptr);
if (!tables_res) {
  std::cerr << "Error fetching table list: " << mysql_error(&(*connection)) << std::endl;
} else {
  std::ofstream table_list_file;
  table_list_file.open("/home/table_column_list.txt", std::ios::trunc);

  if (table_list_file.is_open()) {
    std::time_t current_time = std::time(nullptr);
    table_list_file << "Table and Column list for database: " << database_name 
                    << " at " << std::ctime(&current_time) << std::endl;

    MYSQL_ROW table_row;
    while ((table_row = mysql_fetch_row(tables_res))) {
      const char *table_name = table_row[0];
      //table_list_file << "Table: " << table_name << std::endl;

      std::string column_query = "SHOW COLUMNS FROM `" + std::string(table_name) + "`;";
      if (mysql_query(&(*connection), column_query.c_str()) == 0) {
        MYSQL_RES *columns_res = mysql_store_result(&(*connection));
        if (columns_res) {
          table_list_file << "Table: " << table_name << std::endl;
          MYSQL_ROW col_row;
          while ((col_row = mysql_fetch_row(columns_res))) {
            const char *column_name = col_row[0];
            table_list_file << "  Column: " << column_name << std::endl;
          }
          mysql_free_result(columns_res);
        } else {
          std::cerr << "Error fetching columns for table " << table_name 
                    << ": " << mysql_error(&(*connection)) << std::endl;
        }
      } else {
        std::cerr << "Error executing column query for table " << table_name 
                  << ": " << mysql_error(&(*connection)) << std::endl;
      }

      table_list_file << std::endl;
    }

    table_list_file.close();
  } else {
    std::cerr << "Error opening file to save table and column list\n";
  }

  mysql_free_result(tables_res);
}

  mysql_close(&(*connection));
  return server_status;
}

void MySQLClient::clean_up_env() {
  std::string database_name = db_prefix_ + std::to_string(database_id_);
  string reset_query = "DROP DATABASE IF EXISTS " + database_name + ";";
  std::optional<MYSQL> connection = create_connection("");
  if (!connection.has_value()) {
    return;
  }
  // TODO: clean up the connection.
  mysql_real_query(&(*connection), reset_query.c_str(), reset_query.size());
  clean_up_connection((*connection));
  mysql_close(&(*connection));
}

std::optional<MYSQL> MySQLClient::create_connection(std::string_view db_name) {
  MYSQL result;
  if (mysql_init(&result) == NULL) return std::nullopt;

  if (mysql_real_connect(&result, host_.c_str(), user_name_.c_str(),
                         passwd_.c_str(), db_name.data(), 0, sock_path_.c_str(),
                         CLIENT_MULTI_STATEMENTS) == NULL) {
    std::cerr << "Create connection failed: " << mysql_errno(&result)
              << mysql_error(&result) << std::endl;
    mysql_close(&result);
    return std::nullopt;
  }

  return result;
}

bool MySQLClient::check_alive() {
  std::optional<MYSQL> connection = create_connection("");
  if (!connection.has_value()) {
    return false;
  }
  mysql_close(&(*connection));
  return true;
}

bool MySQLClient::create_database(const std::string &database) {
  MYSQL tmp_m;

  if (mysql_init(&tmp_m) == NULL) {
    mysql_close(&tmp_m);
    return false;
  }

  if (mysql_real_connect(&tmp_m, host_.c_str(), user_name_.c_str(),
                         passwd_.c_str(), nullptr, 0, sock_path_.c_str(),
                         CLIENT_MULTI_STATEMENTS) == NULL) {
    fprintf(stderr, "Connection error3 %d, %s\n", mysql_errno(&tmp_m),
            mysql_error(&tmp_m));
    mysql_close(&tmp_m);
    return false;
  }

  string cmd = "CREATE DATABASE IF NOT EXISTS " + database + ";";
  // TODO: Check server response status.
  mysql_real_query(&tmp_m, cmd.c_str(), cmd.size());
  // std::cerr << "Server response: " << server_response << std::endl;
  clean_up_connection(tmp_m);
  mysql_close(&tmp_m);
  return true;
}

ExecutionStatus MySQLClient::clean_up_connection(MYSQL &mm) {
  int res = -1;
  do {
    auto q_result = mysql_store_result(&mm);
    if (q_result) mysql_free_result(q_result);
  } while ((res = mysql_next_result(&mm)) == 0);

  if (res != -1) {
    res = mysql_errno(&mm);
    if (is_crash_response(res)) {
      // std::cerr << "Found a crash!" << std::endl;
      return kServerCrash;
    }
    if (res == ER_PARSE_ERROR) {
      // std::cerr << "Syntax error" << std::endl;
      return kSyntaxError;
    } else {
      // std::cerr << "Semantic error" << std::endl;
      return kSemanticError;
    }
  }
  // std::cerr << "Normal" << std::endl;
  return kNormal;
}
};  // namespace client
