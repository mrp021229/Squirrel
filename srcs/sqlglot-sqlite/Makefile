CC = /home/Squirrel/AFLplusplus/afl-cc
CXX = g++                             # 用 g++ 来编译 C++ 程序
CFLAGS = -I../sqlite3/bld             # SQLite 头文件路径
LDFLAGS = -L/home/sqlite3/bld -Wl,-rpath,/home/sqlite3/bld -lsqlite3 -lm  # SQLite 链接参数

TARGETS = sqlite_fuzz sqlite_test
SRC_FUZZ = sqlite_fuzz_wrapper.c
SRC_TEST = sqlite_test.cc

all: $(TARGETS)

sqlite_fuzz: $(SRC_FUZZ)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

sqlite_test: $(SRC_TEST)
	$(CXX) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGETS)
