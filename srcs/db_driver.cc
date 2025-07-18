#ifdef __ANDROID__
#include "android-ashmem.h"
#endif
#include <fstream>
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/mman.h>
#include <sys/shm.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <chrono>
#include <iostream>

#include "absl/strings/str_format.h"
#include "client.h"
#include "config.h"
#include "env.h"
#include "types.h"
#include "yaml-cpp/yaml.h"

u8 *__afl_area_ptr;

#ifdef __ANDROID__
u32 __afl_map_size = MAP_SIZE;
#else
__thread u32 __afl_map_size = MAP_SIZE;
#endif

/* Error reporting to forkserver controller */

void send_forkserver_error(int error) {
  u32 status;
  if (!error || error > 0xffff) return;
  status = (FS_OPT_ERROR | FS_OPT_SET_ERROR(error));
  if (write(FORKSRV_FD + 1, (char *)&status, 4) != 4) return;
}

/* SHM setup. */

static void __afl_map_shm(void) {
  char *id_str = getenv(SHM_ENV_VAR);
  char *ptr;

  /* NOTE TODO BUG FIXME: if you want to supply a variable sized map then
     uncomment the following: */

  if ((ptr = getenv("AFL_MAP_SIZE")) != NULL) {
    u32 val = atoi(ptr);
    if (val > 0) __afl_map_size = val;
  }

  if (__afl_map_size > MAP_SIZE) {
    if (__afl_map_size > FS_OPT_MAX_MAPSIZE) {
      fprintf(stderr,
              "Error: AFL++ tools *require* to set AFL_MAP_SIZE to %u to "
              "be able to run this instrumented program!\n",
              __afl_map_size);
      if (id_str) {
        send_forkserver_error(FS_ERROR_MAP_SIZE);
        exit(-1);
      }

    } else {
      fprintf(stderr,
              "Warning: AFL++ tools will need to set AFL_MAP_SIZE to %u to "
              "be able to run this instrumented program!\n",
              __afl_map_size);
    }
  }

  if (id_str) {
#ifdef USEMMAP
    const char *shm_file_path = id_str;
    int shm_fd = -1;
    unsigned char *shm_base = NULL;

    /* create the shared memory segment as if it was a file */
    shm_fd = shm_open(shm_file_path, O_RDWR, 0600);
    if (shm_fd == -1) {
      fprintf(stderr, "shm_open() failed\n");
      send_forkserver_error(FS_ERROR_SHM_OPEN);
      exit(1);
    }

    /* map the shared memory segment to the address space of the process */
    shm_base =
        mmap(0, __afl_map_size, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);

    if (shm_base == MAP_FAILED) {
      close(shm_fd);
      shm_fd = -1;

      fprintf(stderr, "mmap() failed\n");
      send_forkserver_error(FS_ERROR_MMAP);
      exit(2);
    }

    __afl_area_ptr = shm_base;
#else
    u32 shm_id = atoi(id_str);

    __afl_area_ptr = (u8 *)shmat(shm_id, 0, 0);

#endif

    if (__afl_area_ptr == (void *)-1) {
      send_forkserver_error(FS_ERROR_SHMAT);
      exit(1);
    }

    /* Write something into the bitmap so that the parent doesn't give up */
    __afl_area_ptr[0] = 1;
  }
}

/* Fork server logic. */

static void __afl_start_forkserver(void) {
  u8 tmp[4] = {0, 0, 0, 0};
  u32 status = 0;

  if (__afl_map_size <= FS_OPT_MAX_MAPSIZE)
    status |= (FS_OPT_SET_MAPSIZE(__afl_map_size) | FS_OPT_MAPSIZE);
  if (status) status |= (FS_OPT_ENABLED);
  memcpy(tmp, &status, 4);

  /* Phone home and tell the parent that we're OK. */

  if (write(FORKSRV_FD + 1, tmp, 4) != 4) return;
}

static u32 __afl_next_testcase(u8 *buf, u32 max_len) {
  s32 status, res = 0xffffff;

  /* Wait for parent by reading from the pipe. Abort if read fails. */
  if (read(FORKSRV_FD, &status, 4) != 4) return 0;

  /* we have a testcase - read it */
  status = read(0, buf, max_len);

  /* report that we are starting the target */
  if (write(FORKSRV_FD + 1, &res, 4) != 4) return 0;

  return status;
}

static void __afl_end_testcase(client::ExecutionStatus status) {
  int waitpid_status = 0xffffff;
  if (status == client::kServerCrash) {
    waitpid_status = 0x6;  // raise.
  }

  if (write(FORKSRV_FD + 1, &waitpid_status, 4) != 4) exit(1);
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

int main(int argc, char *argv[]) {
  printf("Start!!!\n");
  const char *config_file_path = getenv(kConfigEnv);
  if (!config_file_path) {
    std::cerr << absl::StrFormat(
        "You should set the enviroment variable %s to "
        "the path of your config file.\n",
        kConfigEnv);
    exit(-1);
  }
  YAML::Node config = YAML::LoadFile(config_file_path);
  std::string db_name = config["db"].as<std::string>();
  std::string startup_cmd = config["startup_cmd"].as<std::string>();
  // char buffer[16];  // 假设最多 15 字符 + '\0'
  // auto *db = create_database(config);


  // std::ifstream in("/home/database.txt");
  // in.getline(buffer, sizeof(buffer));
  // in.close();

  // if (strcmp(buffer, "1") == 0) {
  //     std::ofstream out("/home/database.txt");
  //     out << "0";
  //     out.close();
      
  // }
  
  client::DBClient *database = client::create_client(db_name, config);
  database->initialize(config);

  /* This is were the testcase data is written into */
  constexpr size_t kMaxInputSize = 0x100000;
  u8 *buf = (u8 *)malloc(
      kMaxInputSize);  // this is the maximum size for a test case! set it!
  s32 len;

  __afl_map_size = MAP_SIZE;  // default is 65536

  /* then we initialize the shared memory map and start the forkserver */

  // Start the database server. In case that the driver
  // is stopped and restarted, we should not start another server.
  __afl_map_shm();
  if (!database->check_alive()) {
    system(startup_cmd.c_str());
    printf("checkalive!!\n");
    sleep(5);
  }
  else{
    printf("already,live\n");
  }

  // std::ofstream sql_file("/home/output/sql_log.txt", std::ios::app);
  // //count correct
  // std::ofstream log_file("/home/output/fuzz_results.csv", std::ios::app); // 追加写
  // log_file << "time,Syntax_correct_rate,Semantic_correct_rate,total,syntax,semantic,Timeout,Normal,ServerCrash,ExecuteError,ConnectFailed\n";
  open_log_files(file_index);
  __afl_start_forkserver();
  //count correct
  // kConnectFailed,
  // kExecuteError,
  // kServerCrash,
  // kNormal,
  // kTimeout,
  // kSyntaxError,
  // kSemanticError
  int SyntaxError=0;
  int SemanticError=0;
  int Timeout=0;
  int Normal=0;
  int ServerCrash=0;
  int ExecuteError=0;
  int ConnectFailed=0;
  int total=0;
  auto start_time = std::chrono::steady_clock::now();
  auto now = std::chrono::steady_clock::now();
  auto tips = std::chrono::duration_cast<std::chrono::seconds>(now - start_time).count();
  
  int cnt=0;
  database->prepare_env();
  while ((len = __afl_next_testcase(buf, kMaxInputSize)) > 0) {
    now = std::chrono::steady_clock::now();
    if (std::chrono::duration_cast<std::chrono::hours>(now - file_start_time).count() >= 1) {
      file_index++;
      file_start_time = now;
      open_log_files(file_index);
    }
    // Check for dummy tag "0"
  if (len == 1 && buf[0] == '0') {
    __afl_end_testcase(client::kNormal);  // Or another non-crashing status
    continue;
  }
    
    std::string query((const char *)buf, len);\

    
    // database->prepare_env();
    client::ExecutionStatus status = database->execute((const char *)buf, len);
    
    if (!sql_file.is_open()) {
    std::cerr << "!open't" << std::endl;
    } else {
        sql_file.write((const char *)buf, len); // 写入原始 SQL
        sql_file << std::endl;                  // 可选：换行
        sql_file.flush();                       // 立即写入磁盘
    }

    if(status==client::kSyntaxError) SyntaxError++;
    else if(status==client::kSemanticError) SemanticError++;

    if(status==client::kTimeout) Timeout++;
    if(status==client::kNormal) Normal++;
    if(status==client::kServerCrash) ServerCrash++;
    if(status==client::kExecuteError) ExecuteError++;
    if(status==client::kConnectFailed) ConnectFailed++;
    total++;
    

    
    //count correct
    auto now = std::chrono::steady_clock::now();
    auto tim = std::chrono::duration_cast<std::chrono::seconds>(now - start_time).count();
    
    if(tim-tips>=5.0){
      double SyntaxCorrect = (total-SyntaxError)*1.0/total;
      double SemanticCorrect = (total-SyntaxError-SemanticError)*1.0/total;
      // log_file << tim << "," << SyntaxCorrect << "," << SemanticCorrect << "," << total << "," << SyntaxError << "," << SemanticError  << "," << Timeout  << "," << Normal  << "," << ServerCrash  << "," << ExecuteError  << "," << ConnectFailed  <<"\n";
      // log_file.flush();
      total=0;
      SyntaxError=0;
      SemanticError=0;
      Timeout=0;
      Normal=0;
      ServerCrash=0;
      ExecuteError=0;
      ConnectFailed=0;
      tips = tim;
    }



    __afl_area_ptr[0] = 1;
    

    if (status == client::kServerCrash) {
      while (!database->check_alive()) {
        // Wait for the server to be restart.
        sleep(5);
      }
    }
    
    if(cnt > 2000){
      cnt=0;
      database->clean_up_env();
      database->prepare_env();
      // 清空文件内容
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
    else{
      cnt++;
    }
    __afl_end_testcase(status);
  }
  assert(false && "Crash on parent?");

  return 0;
}
