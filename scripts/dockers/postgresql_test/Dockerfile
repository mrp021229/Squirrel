FROM ubuntu:22.04
LABEL maintainer="Squirrel"

# 安装构建工具与依赖
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    clang llvm llvm-dev llvm-runtime llvm-tools-14 lldb-14 lld-14 \
    build-essential cmake git vim sudo python3 python3-pip \
    libpq-dev libreadline-dev zlib1g-dev flex bison libyaml-cpp-dev \
    python3-fire pkg-config clang-format && \
    apt-get clean

# 安装 Python 库
RUN pip3 install --upgrade pip && \
    pip3 install sqlglot psycopg2-binary chardet

# 创建用户
RUN mkdir -p /home && \
    groupadd dobigthing && \
    useradd -l -K UMASK=0000 -d /home -g dobigthing dobigthing && \
    chown dobigthing:dobigthing /home && \
    echo "dobigthing:dobigthing" | chpasswd && \
    usermod -a -G sudo dobigthing && \
    chmod +w /etc/sudoers && \
    echo "%dobigthing   ALL=(ALL:ALL)NOPASSWD:ALL" >> /etc/sudoers && \
    chmod -w /etc/sudoers

USER dobigthing
WORKDIR /home
ARG CACHEBUST=1

# 设置 ASan 编译环境变量
ENV CC=clang
ENV CXX=clang++
ENV CFLAGS="-fsanitize=address -O1 -fno-omit-frame-pointer -g"
ENV CXXFLAGS="-fsanitize=address -O1 -fno-omit-frame-pointer -g"
ENV LDFLAGS="-fsanitize=address"

# 复制 PostgreSQL 源码并编译
COPY postgres/ postgres/
RUN mkdir bld/ && cd bld/ && \
    ../postgres/configure --enable-debug --enable-cassert && \
    make -j$(nproc) && \
    sudo make install

# 初始化数据目录
RUN sudo mkdir -p /usr/local/pgsql/data && \
    sudo chown dobigthing /usr/local/pgsql/data && \
    /usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data