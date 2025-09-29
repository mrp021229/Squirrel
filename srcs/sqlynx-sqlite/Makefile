CC  = /home/Squirrel/AFLplusplus/afl-cc
CXX = /home/Squirrel/AFLplusplus/afl-c++

# C++ 编译选项（把原来的 CFLAGS 内容搬过来，并加上标准与优化/调试）
CXXFLAGS = -std=c++17 -O2 -g -I/home/sqlite3/bld

# 链接参数（保持你的设置）
LDFLAGS  = -L/home/sqlite3/bld -Wl,-rpath,/home/sqlite3/bld -lsqlite3 -lm

TARGETS  = sqlite_fuzz sqlite_test
SRC_FUZZ = sqlite_fuzz_wrapper.cc
SRC_TEST = sqlite_test.cc

.PHONY: all clean
all: $(TARGETS)

sqlite_fuzz: $(SRC_FUZZ)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

sqlite_test: $(SRC_TEST)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGETS)
