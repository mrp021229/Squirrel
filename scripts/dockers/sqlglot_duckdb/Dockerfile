from ubuntu:22.04
LABEL maintainer="Squirrel"

ENV DEBIAN_FRONTEND noninteractive

# common config
#tcl8.6 tcl8.6-tdbc-sqlite3
RUN apt-get update && \
    apt-get -y install \
      make cmake ninja-build build-essential pkg-config \
      clang lld llvm clang-format \
      git curl ca-certificates vim sudo \
      python3 python3-pip python3-venv python3-fire\
      libreadline-dev libssl-dev && \
    apt-get clean

# 更新 apt 并安装 Python3 和 pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

# 安装 sqlglot 库
RUN pip3 install sqlglot

# 安装Python依赖
RUN pip3 install --upgrade pip
RUN pip3 install psycopg2-binary chardet






RUN mkdir -p /home && \
    groupadd dobigthing && \
    useradd -l -K UMASK=0000 -d /home -g dobigthing dobigthing && \
    chown dobigthing:dobigthing /home

RUN	echo "dobigthing:dobigthing" | chpasswd && usermod -a -G sudo dobigthing
RUN chmod +w /etc/sudoers && \
    echo "%dobigthing   ALL=(ALL:ALL)NOPASSWD:ALL" >> /etc/sudoers && \
    chmod -w /etc/sudoers

USER dobigthing
WORKDIR /home

# COPY Squirrel/ Squirrel/
# RUN sudo chmod -R 777 Squirrel
# RUN sudo chown -R dobigthing Squirrel
# RUN cd Squirrel && \
#     cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DSQLITE=ON && \
#     cmake --build build -j && \
#     cd AFLplusplus/ && LLVM_CONFIG=llvm-config-14 make -j20


# COPY duckdb/ duckdb/
# RUN sudo chmod -R 777 duckdb
# RUN sudo chown -R dobigthing duckdb
# RUN git clone https://github.com/sqlite/sqlite sqlite3/ && cd sqlite3 && mkdir bld

# WORKDIR /home/sqlite3/bld

# ENV CC=/home/Squirrel/AFLplusplus/afl-cc
# ENV CXX=/home/Squirrel/AFLplusplus/afl-c++
# RUN ../configure && make -j && make sqlite3.c

# RUN $CC $CFLAGS -I. -c \
#     /home/sqlite3/test/ossfuzz.c -o /home/sqlite3/test/ossfuzz.o
# RUN $CC $CFLAGS -I. -c \
#     /home/sqlite3/test/ossshell.c -o /home/sqlite3/test/ossshell.o

# RUN $CXX $CXXFLAGS \
#     /home/sqlite3/test/ossfuzz.o /home/sqlite3/test/ossshell.o -o /home/ossfuzz \
#    ./sqlite3.o -ldl -pthread

# WORKDIR /home/Squirrel/scripts/utils
# ENTRYPOINT python3 run.py sqlite ../../data/fuzz_root/input
