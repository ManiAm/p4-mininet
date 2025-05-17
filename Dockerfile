FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    openvswitch-switch \
    iproute2 \
    iputils-ping \
    net-tools \
    tcpdump \
    sudo \
    curl \
    git \
    nano \
    python3 \
    python3-pip \
    python3-venv \
    cmake \
    g++ \
    automake \
    libtool \
    libgc-dev \
    bison \
    flex \
    libfl-dev \
    libboost-dev \
    libboost-iostreams-dev \
    libboost-graph-dev \
    llvm \
    pkg-config \
    clang-format \
    gpg \
    lsb-release

WORKDIR /opt

RUN pip install --upgrade pip setuptools

RUN pip install \
    psutil

# Clone and install Mininet
RUN git clone https://github.com/mininet/mininet.git && \
    cd mininet && \
    git checkout 2.3.1b4 && \
    PYTHON=python3 ./util/install.sh -a

# Install Python packages for P4C
RUN pip install \
    pyroute2==0.7.3 \
    ply==3.11 \
    "ptf @ git+https://github.com/p4lang/ptf@d016cdfe99f2d609cc9c7fd7f8c414b56d5b3c5c" \
    "p4runtime @ git+https://github.com/p4lang/p4runtime@ec4eb5ef70dbcbcbf2f8357a4b2b8c2f218845a5#subdirectory=py" \
    scapy==2.5.0 \
    clang-format==18.1.0 \
    isort==5.13.2 \
    black==24.3.0 \
    protobuf==3.20.2 \
    grpcio==1.67.0 \
    googleapis-common-protos==1.53.0

# Clone and build P4C
RUN git clone --recursive https://github.com/p4lang/p4c.git && \
    cd p4c && \
    git checkout v1.2.5.6 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make check && \
    make install

# Install BMv2
RUN . /etc/os-release && \
    echo "deb http://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${VERSION_ID}/ /" > /etc/apt/sources.list.d/home_p4lang.list && \
    curl -fsSL https://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${VERSION_ID}/Release.key | gpg --dearmor > /etc/apt/trusted.gpg.d/home_p4lang.gpg

RUN apt-get update && \
    apt-get install -y p4lang-bmv2

COPY simple_forward/ ./simple_forward/

COPY mytopofile.py ./mytopofile.py
RUN chmod +x ./mytopofile.py

COPY startup.sh /usr/local/bin/startup.sh
RUN chmod +x /usr/local/bin/startup.sh

ENTRYPOINT ["/usr/local/bin/startup.sh"]

CMD ["/bin/bash"]
