CC   = /home/Squirrel/AFLplusplus/afl-cc
CXX  = /home/Squirrel/AFLplusplus/afl-c++

# C++ 编译选项
# 注意修改 -I 为你安装 clickhouse-cpp 的 include 路径
CXXFLAGS = -std=c++17 -O2 -g -I/home/clickhouse-cpp/include

# 链接参数
# 注意修改 -L 为 clickhouse-cpp 库路径
# 库名可能是 -lclickhouse-cpp-lib 或 -lclickhouse-cpp-client -lclickhouse-cpp-common
LDFLAGS  = -L/home/clickhouse-cpp/lib -Wl,-rpath,/home/clickhouse-cpp/lib \
           -lclickhouse-cpp-lib -lpthread

TARGETS  = clickhouse_fuzz clickhouse_test
SRC_FUZZ = clickhouse_fuzz_wrapper.cc
SRC_TEST = clickhouse_test.cc

.PHONY: all clean
all: $(TARGETS)

clickhouse_fuzz: $(SRC_FUZZ)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

clickhouse_test: $(SRC_TEST)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGETS)
