from ubuntu:22.04
LABEL maintainer="Squirrel"

# common config
RUN apt-get update
RUN apt-get -y install make cmake build-essential vim sudo git \
    clang ninja-build pkg-config clang-format libpq-dev llvm libyaml-cpp-dev zlib1g-dev \
    libreadline8 libreadline-dev bison flex python3-fire

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

# # 配置SSH（通过传递无密码的密钥）
# ARG SSH_PRIVATE_KEY
# RUN mkdir -p /home/dobigthing/.ssh && \
#     printf "%s" "$SSH_PRIVATE_KEY" > /home/dobigthing/.ssh/id_ed25519_nopass && \
#     chmod 600 /home/dobigthing/.ssh/id_ed25519_nopass && \
#     ssh-keyscan github.com >> /home/dobigthing/.ssh/known_hosts && \
#     chown -R dobigthing:dobigthing /home/dobigthing/.ssh

# # 将无密码的SSH私钥和Git配置加入到docker镜像中
# RUN git config --global user.name "mrp021229" && \
#     git config --global user.email "mrp20021229@163.com"

USER dobigthing
WORKDIR /home
ARG CACHEBUST=1
RUN git clone https://github.com/mrp021229/Squirrel.git && \
    cd Squirrel && git submodule update --init && \
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DPOSTGRESQL=ON && \
    cmake --build build -j && \
    cd AFLplusplus/ && LLVM_CONFIG=llvm-config-14 make -j20

RUN git clone https://github.com/postgres/postgres.git postgres/ && \
    mkdir bld/ && cd bld/ && \
    CC=/home/Squirrel/AFLplusplus/afl-cc CXX=/home/Squirrel/AFLplusplus/afl-c++ \
    ../postgres/configure

RUN cd bld/ && make -j && sudo make install && \
    sudo mkdir /usr/local/pgsql/data && sudo chown dobigthing /usr/local/pgsql/data &&  \
    AFL_IGNORE_PROBLEMS=1 /usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data

RUN AFL_DEBUG=1 __AFL_SHM_ID=1234 /usr/local/pgsql/bin/postgres 2>&1 | grep "__afl_map_size" | tail -n 1 | cut -d"," -f8 | cut -d" " -f 3 > /tmp/mapsize
# WORKDIR /home/Squirrel/build
# ENTRYPOINT ./test_client /home/Squirrel/data/config_postgresql.yml
WORKDIR /home/Squirrel/scripts/utils
ENTRYPOINT AFL_MAP_SIZE=$(cat /tmp/mapsize) python3 run.py postgresql ../../data/fuzz_root/pqsql_input/
#docker中适配python-sqlglot环境，试运行sqlglot脚本