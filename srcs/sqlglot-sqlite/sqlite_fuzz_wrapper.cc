// persistent_sqlite_wrapper.cc  ~F~P ~_~@~T C++
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>         // ssize_t
#include <sqlite3.h>

#include <chrono>
#include <iostream>
#include <fstream>
#include <string>

// AFL++ 手动持久化接口（用 afl-clang-fast 编译时由运行时提供）
// extern void __AFL_INIT(void);
// extern int  __AFL_LOOP(unsigned int);

#define MAX_IN (1 << 20)  // 1MB 输入上限，可按需调大
int execute(sqlite3 *db, char *sql, char *err_msg){
    int rc = sqlite3_exec(db, sql, 0, 0, &err_msg);
    if (rc != SQLITE_OK) {
        //fprintf(stderr, "[exec_sql] error: %s\n", err ? err : "(unknown)");
        if (err_msg) sqlite3_free(err_msg); 
    }
    
    return rc;
}
static int exec_sql(sqlite3 *db, const char *sql) {
    char *err = NULL;
    int rc = sqlite3_exec(db, sql, NULL, NULL, &err);
    if (rc != SQLITE_OK) {
        //fprintf(stderr, "[exec_sql] error: %s\n", err ? err : "(unknown)");
        if (err) sqlite3_free(err);

    }
    return rc;
}

int dump_schema_to_file(sqlite3 *db, const char *path) {
    FILE *fp = fopen(path, "w");
    if (!fp) {
        perror("fopen");
        return -1;
    }

    const char *q_tables =
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name;";

    sqlite3_stmt *stmt_tables = NULL;
    if (sqlite3_prepare_v2(db, q_tables, -1, &stmt_tables, NULL) != SQLITE_OK) {
        fprintf(stderr, "prepare tables failed: %s\n", sqlite3_errmsg(db));
        fclose(fp);
        return -2;
    }

    while (sqlite3_step(stmt_tables) == SQLITE_ROW) {
        const unsigned char *tname_uc = sqlite3_column_text(stmt_tables, 0);
        const char *tname = (const char*)tname_uc;

        fprintf(fp, "Table: %s\n", tname);

        char pragma_sql[512];
        snprintf(pragma_sql, sizeof(pragma_sql), "PRAGMA table_info(%s);", tname);

        sqlite3_stmt *stmt_cols = NULL;
        if (sqlite3_prepare_v2(db, pragma_sql, -1, &stmt_cols, NULL) != SQLITE_OK) {
            fprintf(stderr, "prepare pragma failed for %s: %s\n",
                    tname, sqlite3_errmsg(db));
            continue;
        }

        while (sqlite3_step(stmt_cols) == SQLITE_ROW) {
            const unsigned char *cname_uc = sqlite3_column_text(stmt_cols, 1);
            const char *cname = (const char*)cname_uc;
            fprintf(fp, "  Column: %s\n", cname);
        }
        sqlite3_finalize(stmt_cols);

        fprintf(fp, "\n"); // 表之间空一行
    }

    sqlite3_finalize(stmt_tables);
    fclose(fp);
    return 0;
}

static void reset_db(sqlite3 **pdb) {
  if (*pdb) { sqlite3_close(*pdb); *pdb = NULL; }
  // 彻底清理可能存在的文件
  unlink("test.db");
  unlink("test.db-wal");
  unlink("test.db-shm");
  if (sqlite3_open("test.db", pdb) != SQLITE_OK) {
    fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(*pdb));
  }
}



int file_index = 1;
auto file_start_time = std::chrono::steady_clock::now();
std::ofstream sql_file;
// std::ofstream log_file;

void open_log_files(int index) {
  std::string sql_filename = "/home/output/sql_log_" + std::to_string(index) + ".txt";
  // std::string log_filename = "/home/output/fuzz_results_" + std::to_string(index) + ".csv";

  if (sql_file.is_open()) sql_file.close();
  // if (log_file.is_open()) log_file.close();

  sql_file.open(sql_filename, std::ios::app);
  // log_file.open(log_filename, std::ios::app);
  // log_file << "time,Syntax_correct_rate,Semantic_correct_rate,total,syntax,semantic,Timeout,Normal,ServerCrash,ExecuteError,ConnectFailed\n";
}

int main(void) {
  // —— 每个持久化“会话”（最多2000用例）开始时重置数据库文件 ——
  unlink("test.db");  // 忽略返回值：不存在时无所谓

  // 初始化（forkserver 延迟到这里握手）
  __AFL_INIT();

  // 打开数据库（整个持久化会话内复用一个句柄，减少开销）
  sqlite3 *db = NULL;
  reset_db(&db);
  

  // 预分配一次输入缓冲
  static unsigned char buf[MAX_IN + 1];
  unsigned long long iters = 0;
  // —— 持久化主循环：同一进程内最多处理 2000 个输入 ——
  open_log_files(file_index);

  auto start_time = std::chrono::steady_clock::now();
  auto now = std::chrono::steady_clock::now();
  auto tips = std::chrono::duration_cast<std::chrono::seconds>(now - start_time).count();

  while (__AFL_LOOP(0x7fffffff)) {
    iters++;
    now = std::chrono::steady_clock::now();
    if (std::chrono::duration_cast<std::chrono::hours>(now - file_start_time).count() >= 1) {
      file_index++;
      file_start_time = now;
      open_log_files(file_index);
    }


    // 从 stdin 读取本轮样本（AFL 会把用例写到 stdin 并关闭写端）
    ssize_t len = read(STDIN_FILENO, buf, MAX_IN);
    if (len <= 0) {
      // 没读到数据就跳过这一轮，进入下一轮
      //（注意：不要阻塞等待“下一条”，下一条由下一次 __AFL_LOOP 驱动）
      continue;
    }
    if (len == 1 && buf[0] == '0') {
      continue;
    }
    buf[len] = '\0';  // 作为 SQL 文本使用时补 NUL

    // 执行 SQL；出现错误只释放错误消息，不退出
    char *err_msg = NULL;
    int rc = sqlite3_exec(db, (char *)buf, NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
      // 可在这里做最小化处理以避免噪声与性能损耗
      // fprintf(stderr, "SQL error: %s\n", err_msg);
      if (err_msg) sqlite3_free(err_msg);
      // 不要退出，继续下一轮
    }
    int a = dump_schema_to_file(db,"/home/table_column_list.txt");
    if (!sql_file.is_open()) {
      std::cerr << "!open't" << std::endl;
    } else {
        sql_file.write((const char *)buf, len); // 写入原始 SQL
        sql_file << std::endl;                  // 可选：换行
        sql_file.flush();                       // 立即写入磁盘
    }

    //count correct
    auto now = std::chrono::steady_clock::now();
    auto tim = std::chrono::duration_cast<std::chrono::seconds>(now - start_time).count();


    if(iters==2000){
      iters=0;
      reset_db(&db);
      std::ofstream ofs("/home/table_column_list.txt", std::ofstream::out | std::ofstream::trunc);
      ofs.close();
      if (!sql_file.is_open()) {
        std::cerr << "!open't" << std::endl;
      } else {
          sql_file << "New database";// 写入原始 SQL
          sql_file << std::endl;                  // 可选：换行
          sql_file.flush();                       // 立即写入磁盘
      }
    }
    // 准备下一轮前，把 stdin 中残留读干净（通常不需要；AFL 会完整投喂并关闭）
    // 若担心个别用例超出 MAX_IN，可在这里 drain，但一般不推荐阻塞等待。
  }

  // 会话结束（2000轮后）：收尾并退出；AFL 会 fork 新进程开始下一会话
  sqlite3_close(db);
  return 0;
}
// /home/Squirrel/AFLplusplus/afl-fuzz -i /home/Squirrel/data/fuzz_root/input/ -o /home/output ./sqlite_fuzz
