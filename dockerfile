FROM ubuntu:20.04
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        wireguard \
        python3-pip \
    && apt-get dist-upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

COPY requirements.txt /opt/vpn_enrollment/requirements.txt
WORKDIR /opt/vpn_enrollment
RUN pip install -r requirements.txt
COPY . /opt/vpn_enrollment/
CMD ["python3 -m flask run"]