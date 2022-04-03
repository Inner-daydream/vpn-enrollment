FROM ubuntu:20.04
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        wireguard \
        python3 \
        python3-pip \
        iproute2 \
        iptables \
        git \
    && apt-get dist-upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

COPY requirements.txt /opt/vpn_enrollment/requirements.txt
WORKDIR /opt/vpn_enrollment
RUN pip install -r requirements.txt
COPY . /opt/vpn_enrollment/
EXPOSE 8080/tcp
EXPOSE 51820/udp
CMD ["python3", "/opt/vpn_enrollment/main.py"]
