from ubuntu:22.04
LABEL maintainer="Squirrel"



# common config
RUN apt-get update && \
    apt-get -y install make cmake build-essential vim sudo git \
    clang libmysqlclient-dev ninja-build pkg-config clang-format \
    libpq-dev libyaml-cpp-dev lld llvm bison python3-fire
# RUN apt-get update && apt-get install -y libssl-dev

RUN mkdir -p /home && \
    groupadd dobigthing && \
    useradd -l -K UMASK=0000 -d /home -g dobigthing dobigthing && \
    chown dobigthing:dobigthing /home

RUN	echo "dobigthing:dobigthing" | chpasswd && usermod -a -G sudo dobigthing
RUN chmod +w /etc/sudoers && \
    echo "%dobigthing   ALL=(ALL:ALL)NOPASSWD:ALL" >> /etc/sudoers && \
    chmod -w /etc/sudoers
USER root

# 安装 OpenSSL 1.1.1（保持工作目录不变）
RUN apt-get update && apt-get install -y build-essential wget tar libz-dev && \
    wget https://www.openssl.org/source/openssl-1.1.1w.tar.gz && \
    tar -xf openssl-1.1.1w.tar.gz && \
    cd openssl-1.1.1w && \
    ./config --prefix=/usr/local/openssl-1.1.1 shared zlib && \
    make -j$(nproc) && make install && \
    rm -rf openssl-1.1.1w*

# 设置动态库搜索路径
ENV LD_LIBRARY_PATH="/usr/local/openssl-1.1.1/lib:$LD_LIBRARY_PATH"
USER dobigthing
WORKDIR /home
ARG CACHEBUST=1
RUN git clone -b original https://github.com/mrp021229/Squirrel.git && \
    cd Squirrel && git submodule update --init && \
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -Wno-dev -DMYSQL=ON && \
    cmake --build build -j && \
    cd AFLplusplus/ && LLVM_CONFIG=llvm-config-14 make -j20
    

# RUN git clone --branch mysql-8.0.0 --depth 1 https://github.com/mysql/mysql-server.git mysql
# RUN sudo apt-get -y install apt-transport-https curl software-properties-common gnutls-dev
# RUN mkdir bld && cd bld/ && \
#     CC=/home/Squirrel/AFLplusplus/afl-clang-fast CXX=/home/Squirrel/AFLplusplus/afl-clang-fast++ \
#     cmake ../mysql/ -DDOWNLOAD_BOOST=1 -DWITH_BOOST=../boost \
#     -DWITH_DEBUG=1 -DCPACK_MONOLITHIC_INSTALL=1 -DWITH_UNIT_TESTS=OFF

RUN git clone --branch mysql-8.0.27 --depth 1 https://github.com/mysql/mysql-server.git mysql

# 安装依赖 + 下载 Boost
RUN sudo apt-get -y install apt-transport-https curl software-properties-common gnutls-dev && \
    mkdir -p /home/boost && \
    curl -L --retry 5 --retry-delay 5 \
      -o /home/boost_1_73_0.tar.gz \
      https://archives.boost.io/release/1.73.0/source/boost_1_73_0.tar.gz && \
    tar -xzf /home/boost_1_73_0.tar.gz -C /home/boost && \
    rm /home/boost_1_73_0.tar.gz



# # 构建 MySQL，使用下载好的 Boost
# RUN mkdir bld && cd bld/ && \
#     CC=/home/Squirrel/AFLplusplus/afl-clang-fast CXX=/home/Squirrel/AFLplusplus/afl-clang-fast++ \
#     cmake ../mysql/ -DDOWNLOAD_BOOST=0 -DWITH_BOOST=/home/boost/boost_1_73_0 \
#     -DWITH_DEBUG=1 -DCPACK_MONOLITHIC_INSTALL=1 -DWITH_UNIT_TESTS=OFF

# 安装 OpenSSL 1.1.1 到 /usr/local/openssl-1.1.1（不会更改 WORKDIR）
# RUN apt-get update && apt-get install -y build-essential wget tar libz-dev && \
#     wget https://www.openssl.org/source/openssl-1.1.1w.tar.gz && \
#     tar -xf openssl-1.1.1w.tar.gz && \
#     cd openssl-1.1.1w && \
#     ./config --prefix=/usr/local/openssl-1.1.1 shared zlib && \
#     make -j$(nproc) && make install && \
#     rm -rf openssl-1.1.1w*

# # 设置动态库搜索路径（防止运行时找不到）
# ENV LD_LIBRARY_PATH="/usr/local/openssl-1.1.1/lib:$LD_LIBRARY_PATH"
# 构建 MySQL（引用 OpenSSL 1.1.1）
RUN mkdir bld && cd bld/ && \
    CC=/home/Squirrel/AFLplusplus/afl-clang-fast \
    CXX=/home/Squirrel/AFLplusplus/afl-clang-fast++ \
    cmake ../mysql/ \
        -DDOWNLOAD_BOOST=0 \
        -DWITH_BOOST=/home/boost/boost_1_73_0 \
        -DWITH_DEBUG=1 \
        -DCPACK_MONOLITHIC_INSTALL=1 \
        -DWITH_UNIT_TESTS=OFF \
        -DWITH_SSL=system \
        -DOPENSSL_INCLUDE_DIR=/usr/local/openssl-1.1.1/include \
        -DOPENSSL_LIBRARIES=/usr/local/openssl-1.1.1/lib \
        -DCMAKE_C_FLAGS="-I/usr/local/openssl-1.1.1/include -L/usr/local/openssl-1.1.1/lib" \
        -DCMAKE_CXX_FLAGS="-I/usr/local/openssl-1.1.1/include -L/usr/local/openssl-1.1.1/lib" \
        -DCMAKE_EXE_LINKER_FLAGS="-L/usr/local/openssl-1.1.1/lib -lssl -lcrypto"

# 添加屏蔽警告参数并关闭将警告视为错误（Werror）
# RUN cd bld && cmake -DCMAKE_CXX_FLAGS="-Wno-deprecated-copy -Wno-error -w" -DCMAKE_C_FLAGS="-Wno-error -w" .

# 编译并安装
RUN cd bld && make -j && sudo cmake --install . --prefix /usr/local/mysql/


RUN sudo chown dobigthing:dobigthing /usr/local/mysql/ -R && \
    cd /usr/local/mysql/ && mkdir mysql-files && chmod 750 mysql-files && \
    AFL_IGNORE_PROBLEMS=1 bin/mysqld --initialize-insecure --user=dobigthing && bin/mysql_ssl_rsa_setup

#ENTRYPOINT bash
#ENTRYPOINT /usr/local/mysql/bin/mysqld --basedir=/usr/local/mysql \
#            --datadir=/usr/local/mysql/data --log-error=err_log.err \
#            --pid-file=server_pid.pid --max_statement_time=1
RUN AFL_DEBUG=1 __AFL_SHM_ID=1234 /usr/local/mysql/bin/mysqld 2>&1 | grep "__afl_map_size" | tail -n 1 | cut -d"," -f8 | cut -d" " -f 3 > /tmp/mapsize
WORKDIR /home/Squirrel/scripts/utils
# ENTRYPOINT AFL_IGNORE_PROBLEMS=1 AFL_MAP_SIZE=$(cat /tmp/mapsize) python3 run.py mysql ../../data/fuzz_root/mysql_input/
