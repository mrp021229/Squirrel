FROM ubuntu:22.04
LABEL maintainer="Squirrel"

# 安装构建工具与 ASan 所需最简依赖
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    clang llvm libclang-common-14-dev libllvm14 \
    build-essential git sudo \
    libpq-dev libreadline-dev zlib1g-dev flex bison pkg-config libicu-dev \
    python3 python3-pip && \
    apt-get clean

# 安装 Python 库
RUN pip3 install --upgrade pip && \
    pip3 install sqlglot psycopg2-binary chardet

# 创建非 root 用户
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

# 复制 PostgreSQL 源码
COPY postgres/ postgres/
RUN mkdir bld/
# 编译 PostgreSQL，开启 ASan 支持
WORKDIR /home/bld
RUN ../postgres/configure --enable-debug --enable-cassert \
    make clean && \
    CC=clang \
    CFLAGS="-fsanitize=address -O1 -fno-omit-frame-pointer" \
    LDFLAGS="-fsanitize=address" && \
    make -j$(nproc) && \
    sudo make install

# 初始化数据库目录
RUN sudo mkdir -p /usr/local/pgsql/data && \
    sudo chown dobigthing /usr/local/pgsql/data && \
    /usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data
