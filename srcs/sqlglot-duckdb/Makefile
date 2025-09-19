CC  = /home/Squirrel/AFLplusplus/afl-cc
CXX = /home/Squirrel/AFLplusplus/afl-c++

# 指向你编译好的 duckdb（bld 目录）
CXXFLAGS = -std=c++17 -O2 -g -I/home/duckdb/src/include

# 链接 DuckDB 的动态库（.so）
LDFLAGS  = -L/home/bld/src -lduckdb -lm

# 可执行目标
TARGETS  = duckdb_test duckdb_fuzz

# 源码文件
SRC_TEST = duckdb_test.cc
SRC_FUZZ = persistent_duckdb_wrapper.cc

.PHONY: all clean

all: $(TARGETS)

duckdb_test: $(SRC_TEST)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

duckdb_fuzz: $(SRC_FUZZ)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGETS)
# CC=/home/Squirrel/AFLplusplus/afl-clang-fast \
# CXX=/home/Squirrel/AFLplusplus/afl-clang-fast++ \
# cmake ../duckdb \
#   -DCMAKE_C_COMPILER=/home/Squirrel/AFLplusplus/afl-clang-fast \
#   -DCMAKE_CXX_COMPILER=/home/Squirrel/AFLplusplus/afl-clang-fast++ \
#   -DCMAKE_BUILD_TYPE=RelWithDebInfo \
#   -DBUILD_SHELL=ON \
#   -DDUCKDB_ASSERTIONS=1 \
#   -DBUILD_SHARED_LIBS=OFF 