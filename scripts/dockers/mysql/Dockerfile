from ubuntu:22.04
LABEL maintainer="Squirrel"

# common config
RUN apt-get update
RUN apt-get -y install make cmake build-essential vim sudo git \
    clang libmysqlclient-dev ninja-build pkg-config clang-format \
    libpq-dev libyaml-cpp-dev lld llvm bison python3-fire

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

RUN git clone https://github.com/Dobigthing666/Squirrel.git && \
    cd Squirrel && git submodule update --init && \
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -Wno-dev -DMYSQL=ON && \
    cmake --build build -j && \
    cd AFLplusplus/ && LLVM_CONFIG=llvm-config-14 make -j20

RUN git clone --depth=1 https://github.com/mysql/mysql-server.git mysql
RUN sudo apt-get -y install apt-transport-https curl software-properties-common gnutls-dev
RUN mkdir bld && cd bld/ && \
    CC=/home/Squirrel/AFLplusplus/afl-clang-fast CXX=/home/Squirrel/AFLplusplus/afl-clang-fast++ \
    cmake ../mysql/ -DDOWNLOAD_BOOST=1 -DWITH_BOOST=../boost \
    -DWITH_DEBUG=1 -DCPACK_MONOLITHIC_INSTALL=1 -DWITH_UNIT_TESTS=OFF
    
RUN cd bld/ && make -j && sudo cmake --install . --prefix /usr/local/mysql/

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
